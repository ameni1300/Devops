from flask import Flask, request, jsonify
import time
import logging
import uuid
import requests
from decimal import Decimal, ROUND_HALF_UP
from prometheus_client import generate_latest, Counter, Histogram, Gauge

app = Flask(__name__)

# Configuration du logging simple et robuste
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Métriques Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['endpoint'])
CONVERSION_COUNT = Counter('currency_conversions_total', 'Total currency conversions')
CACHE_SIZE = Gauge('exchange_cache_size', 'Current exchange rate cache size')
ACTIVE_REQUESTS = Gauge('http_requests_active', 'Active HTTP requests')

# Métriques legacy (pour compatibilité)
request_count = 0
conversions_count = 0
exchange_cache = {}

def structured_log(level, message, **extra):
    """Fonction de logging structuré manuel"""
    trace_id = getattr(request, 'trace_id', 'none') if hasattr(request, 'trace_id') else 'system'
    log_data = {
        "time": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "level": level,
        "trace_id": trace_id,
        "message": message,
        **extra
    }
    print(f"LOG: {log_data}")

@app.before_request
def before_request():
    request.start_time = time.time()
    request.trace_id = request.headers.get('X-Trace-ID', str(uuid.uuid4()))
    ACTIVE_REQUESTS.inc()
    structured_log("INFO", "Request started", 
                   method=request.method, path=request.path, ip=request.remote_addr)

@app.after_request
def after_request(response):
    ACTIVE_REQUESTS.dec()
    
    if hasattr(request, 'start_time'):
        response_time = time.time() - request.start_time
        # Métriques Prometheus
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
        REQUEST_DURATION.labels(endpoint=request.path).observe(response_time)
        
        structured_log("INFO", "Request completed", 
                      method=request.method, path=request.path, 
                      status_code=response.status_code, 
                      response_time_ms=round(response_time * 1000, 2))
    
    response.headers['X-Trace-ID'] = getattr(request, 'trace_id', 'none')
    return response

def get_exchange_rate(from_currency, to_currency):
    cache_key = f"{from_currency}_{to_currency}"
    current_time = time.time()
    
    # Vérifier le cache (valide 1 heure)
    if cache_key in exchange_cache:
        cached_data = exchange_cache[cache_key]
        if current_time - cached_data['timestamp'] < 3600:
            structured_log("INFO", "Cache hit", from_currency=from_currency, to_currency=to_currency)
            return cached_data['rate']
    
    try:
        # API Frankfurter (gratuite)
        url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        rate = Decimal(str(data['rates'][to_currency]))
        
        # Mettre en cache
        exchange_cache[cache_key] = {
            'rate': rate,
            'timestamp': current_time
        }
        
        # Mettre à jour la métrique de cache
        CACHE_SIZE.set(len(exchange_cache))
        
        structured_log("INFO", "Rate fetched from API", 
                      from_currency=from_currency, to_currency=to_currency, rate=float(rate))
        return rate
        
    except requests.exceptions.RequestException as e:
        structured_log("ERROR", "API request failed", error=str(e))
        return None
    except (KeyError, ValueError) as e:
        structured_log("ERROR", "Invalid API response", error=str(e))
        return None

@app.route('/')
def home():
    return jsonify({
        "message": "Currency Converter API",
        "version": "1.0.0",
        "endpoints": {
            "convert": "/convert?from=EUR&to=USD&amount=100",
            "currencies": "/currencies",
            "metrics": "/metrics",
            "health": "/health"
        },
        "observability": {
            "metrics": "Prometheus format at /metrics",
            "tracing": "X-Trace-ID header support",
            "logging": "Structured JSON logs"
        }
    })

@app.route('/health')
def health():
    cache_status = "healthy" if len(exchange_cache) > 0 else "empty"
    return jsonify({
        "status": "healthy",
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "cache": {
            "size": len(exchange_cache),
            "status": cache_status
        },
        "version": "1.0.0",
        "uptime": "Running"
    })

@app.route('/currencies')
def list_currencies():
    currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "BRL"]
    return jsonify({
        "supported_currencies": sorted(currencies),
        "count": len(currencies)
    })

@app.route('/convert')
def convert():
    global request_count, conversions_count
    request_count += 1
    
    # Récupérer les paramètres
    from_currency = request.args.get('from', '').upper()
    to_currency = request.args.get('to', '').upper()
    amount_str = request.args.get('amount', '')
    
    # Validation
    if not from_currency or not to_currency or not amount_str:
        return jsonify({
            "error": "Paramètres manquants",
            "required": ["from", "to", "amount"],
            "example": "/convert?from=EUR&to=USD&amount=100"
        }), 400
    
    try:
        amount = Decimal(amount_str)
        if amount <= 0:
            return jsonify({"error": "Le montant doit être positif"}), 400
    except:
        return jsonify({"error": "Montant invalide"}), 400
    
    # Conversion
    rate = get_exchange_rate(from_currency, to_currency)
    if rate is None:
        return jsonify({"error": "Taux de change non disponible"}), 400
    
    converted_amount = (amount * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    conversions_count += 1
    CONVERSION_COUNT.inc()
    
    structured_log("INFO", "Conversion successful", 
                  from_currency=from_currency, to_currency=to_currency, 
                  amount=float(amount), converted_amount=float(converted_amount),
                  rate=float(rate))
    
    return jsonify({
        "conversion": {
            "from": from_currency,
            "to": to_currency,
            "amount": float(amount),
            "converted_amount": float(converted_amount),
            "rate": float(rate),
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ')
        },
        "trace_id": getattr(request, 'trace_id', 'none')
    })

@app.route('/metrics')
def metrics():
    # Mettre à jour les métriques de cache
    CACHE_SIZE.set(len(exchange_cache))
    
    # Générer les métriques Prometheus
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    global exchange_cache
    exchange_cache.clear()
    CACHE_SIZE.set(0)
    structured_log("INFO", "Cache cleared")
    return jsonify({
        "message": "Cache vidé avec succès",
        "cache_size": 0
    })

@app.route('/trace')
def trace_test():
    """Endpoint pour tester le tracing"""
    return jsonify({
        "trace_id": getattr(request, 'trace_id', 'none'),
        "message": "Trace ID test endpoint",
        "headers": dict(request.headers)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint non trouvé",
        "path": request.path,
        "trace_id": getattr(request, 'trace_id', 'none')
    }), 404

@app.errorhandler(500)
def internal_error(error):
    structured_log("ERROR", "Internal server error", 
                  error=str(error), path=request.path, trace_id=getattr(request, 'trace_id', 'none'))
    return jsonify({
        "error": "Erreur interne du serveur",
        "trace_id": getattr(request, 'trace_id', 'none')
    }), 500

if __name__ == '__main__':
    print("🚀 Currency Converter API starting on http://0.0.0.0:5000")
    print("📊 Endpoints disponibles: /convert, /currencies, /metrics, /health, /trace")
    print("🔍 Observability: Prometheus metrics, structured logging, request tracing")
    app.run(host='0.0.0.0', port=5000, debug=False)
from flask import Flask, request, jsonify
import time
import logging
import uuid
import requests
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)

# Configuration du logging simple et robuste
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Métriques
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
    structured_log("INFO", "Request started", 
                   method=request.method, path=request.path, ip=request.remote_addr)

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        response_time = time.time() - request.start_time
        structured_log("INFO", "Request completed", 
                      method=request.method, path=request.path, 
                      status_code=response.status_code, response_time=round(response_time, 3))
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
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "cache_size": len(exchange_cache)
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
    
    structured_log("INFO", "Conversion successful", 
                  from_currency=from_currency, to_currency=to_currency, 
                  amount=float(amount), converted_amount=float(converted_amount))
    
    return jsonify({
        "conversion": {
            "from": from_currency,
            "to": to_currency,
            "amount": float(amount),
            "converted_amount": float(converted_amount),
            "rate": float(rate),
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    })

@app.route('/metrics')
def metrics():
    cache_size = len(exchange_cache)
    cache_hit_ratio = 0.5  # Simplifié pour l'exemple
    
    metrics_data = f"""
# HELP http_requests_total Total number of HTTP requests.
# TYPE http_requests_total counter
http_requests_total {request_count}

# HELP currency_conversions_total Total number of currency conversions.
# TYPE currency_conversions_total counter
currency_conversions_total {conversions_count}

# HELP cache_size_current Current size of exchange rate cache.
# TYPE cache_size_current gauge
cache_size_current {cache_size}

# HELP cache_hit_ratio Cache hit ratio.
# TYPE cache_hit_ratio gauge
cache_hit_ratio {cache_hit_ratio}
"""
    return metrics_data, 200, {'Content-Type': 'text/plain'}

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    global exchange_cache
    exchange_cache.clear()
    structured_log("INFO", "Cache cleared")
    return jsonify({"message": "Cache vidé avec succès"})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint non trouvé"}), 404

@app.errorhandler(500)
def internal_error(error):
    structured_log("ERROR", "Internal server error", error=str(error))
    return jsonify({"error": "Erreur interne du serveur"}), 500

if __name__ == '__main__':
    print("🚀 Currency Converter API starting on http://0.0.0.0:5000")
    print("📊 Endpoints disponibles: /convert, /currencies, /metrics, /health")
    app.run(host='0.0.0.0', port=5000, debug=False)
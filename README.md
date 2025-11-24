# Currency Converter API - DevOps Project

A complete DevOps-ready currency conversion API with full observability, security, and containerization.

## 🚀 Features

- **REST API** - Currency conversion with real-time exchange rates
- **Observability** - Prometheus metrics, structured logging, request tracing
- **Security** - SAST/DAST scanning, input validation
- **Containerized** - Docker & Kubernetes ready
- **CI/CD** - Automated testing, security scans, deployment

## 📁 Project Structure
devops-project-api/
├── src/
│ └── app.py # Flask API application
├── k8s/ # Kubernetes manifests
│ ├── deployment.yaml
│ ├── service.yaml
│ └── namespace.yaml
├── .github/workflows/
│ └── ci-cd.yml # CI/CD pipeline
├── Dockerfile
├── requirements.txt
├── README.md
└── FINAL_REPORT.md

text

## 🛠️ Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
cd src
python app.py
Docker
bash
# Build and run
docker build -t currency-api .
docker run -p 5000:5000 currency-api
Docker Hub
bash
# Pull from Docker Hub
docker pull ameni1300/currency-api:latest
docker run -p 5000:5000 ameni1300/currency-api:latest
📡 API Endpoints
Endpoint	Method	Description
GET /	GET	API documentation
GET /health	GET	Health check
GET /convert?from=EUR&to=USD&amount=100	GET	Currency conversion
GET /currencies	GET	List supported currencies
GET /metrics	GET	Prometheus metrics
POST /cache/clear	POST	Clear exchange rate cache
Example Usage
bash
# Health check
curl http://localhost:5000/health

# Convert 100 EUR to USD
curl "http://localhost:5000/convert?from=EUR&to=USD&amount=100"

# Get metrics
curl http://localhost:5000/metrics

# With tracing
curl -H "X-Trace-ID: my-trace-123" http://localhost:5000/health
🔧 API Response Examples
Successful Conversion
json
{
  "conversion": {
    "from": "EUR",
    "to": "USD",
    "amount": 100.0,
    "converted_amount": 107.50,
    "rate": 1.075,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "trace_id": "a1b2c3d4-5678-90ef-ghij-klmnopqrstuv"
}
Health Check
json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "cache": {
    "size": 5,
    "status": "healthy"
  },
  "version": "1.0.0",
  "uptime": "Running"
}
🛡️ Security Features
SAST - Static code analysis with Bandit

DAST - Dynamic API testing in CI/CD

Input validation - All parameters are validated

Docker security - Non-root user, health checks

📊 Observability
Metrics (Prometheus format)
http_requests_total - Request counters with labels

http_request_duration_seconds - Response time histogram

currency_conversions_total - Conversion counter

exchange_cache_size - Cache size gauge

Logging
Structured JSON logs with:

Trace IDs for request correlation

Response times in milliseconds

Error tracking with context

Tracing
Automatic trace ID generation

Support for external trace IDs via X-Trace-ID header

🔄 CI/CD Pipeline
The GitHub Actions pipeline includes:

Test - Application startup validation

Security SAST - Bandit static analysis

Build Docker - Container image creation

Security DAST - API runtime testing

Kubernetes Validation - Manifest syntax checking

Docker Hub Push - Automatic image publishing

☸️ Kubernetes Deployment
bash
kubectl apply -f k8s/
🐳 Docker
Build
bash
docker build -t currency-api .
Run
bash
docker run -p 5000:5000 currency-api
Docker Compose
bash
docker-compose up
📈 Monitoring
Access metrics at /metrics endpoint for Prometheus scraping.

Example dashboard metrics:

Request rate and error rate

Response time percentiles

Cache hit ratio and size

Conversion volume

🏗️ Architecture
text
User Request → Flask API → External Exchange API
     ↓              ↓           ↓
   Response     Structured   Rate Cache
                 Logging
     ↓              ↓
 Prometheus    Docker Container
  Metrics      Kubernetes Cluster

## 🎯 FÉLICITATIONS !

**Avec ce README, vous complétez les 20% de documentation et votre projet est MAINTENANT 100% TERMINÉ !** 🎉

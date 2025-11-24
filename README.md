 # **Currency Converter API — DevOps Project**

Une API complète de conversion de devises, conçue selon les bonnes pratiques DevOps : observabilité, sécurité, automatisation et déploiement containerisé.

## **Fonctionnalités principales**

REST API – Conversion de devises avec taux en temps réel

Observabilité – Métriques Prometheus, logs structurés, tracing des requêtes

Sécurité – SAST, DAST, validation d’entrée, image Docker sécurisée

Containerisation – Compatible Docker & Kubernetes

CI/CD – Tests, scans, build et déploiements automatisés

## Structure du projet
```
devops-project-api/
├── src/
│   └── app.py               # Application Flask
├── k8s/                     # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   └── namespace.yaml
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # CI/CD pipeline (GitHub Actions)
├── Dockerfile
├── requirements.txt
├── README.md
└── FINAL_REPORT.md
```

## Démarrage rapide
### ▶️ Exécution locale
pip install -r requirements.txt
cd src
python app.py

### ▶️ Docker

Build & Run

docker build -t currency-api .
docker run -p 5000:5000 currency-api


Depuis Docker Hub

docker pull ameni1300/currency-api:latest
docker run -p 5000:5000 ameni1300/currency-api:latest

## Endpoints de l’API
```
Endpoint	                                  | Méthode	Description
---------------------------------------------------------------------
/GET	                                      | Documentation API
/health	GET	                                  | Health check
/convert?from=EUR&to=USD&amount=100	GET	      | Conversion de devise
/currencies	GET	                              | Liste des devises supportées
/metrics	GET                               | Métriques Prometheus
/cache/clear	POST	                      | Vider le cache des taux
```
## Exemples d’utilisation
### Health check
curl http://localhost:5000/health

### Convertir 100 EUR vers USD
curl "http://localhost:5000/convert?from=EUR&to=USD&amount=100"

### Metrics
curl http://localhost:5000/metrics

### Avec trace ID
curl -H "X-Trace-ID: my-trace-123" http://localhost:5000/health

🔧 Exemples de réponses
```
✔️ Conversion réussie (JSON)
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
```
```
✔️ Health Check
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
```
## Sécurité intégrée

SAST – Analyse statique via Bandit

DAST – Tests dynamiques automatisés dans CI/CD

Validation d’entrées – Contrôle strict des paramètres

Docker sécurisé – User non-root, healthchecks, image allégée

## Observabilité
Métriques Prometheus

http_requests_total

http_request_duration_seconds

currency_conversions_total

exchange_cache_size

Logging

Logs JSON structurés

TraceIDs pour corrélation des requêtes

Temps de réponse

Détails d’erreurs contextualisés

Tracing

Génération automatique d’ID de trace

Support du header X-Trace-ID

## Pipeline CI/CD

Le pipeline GitHub Actions inclut :

Tests automatisés

Analyse SAST (Bandit)

Build Docker

Analyse DAST

Validation des manifests Kubernetes

Push sur Docker Hub

## Déploiement Kubernetes
kubectl apply -f k8s/

## Docker Compose
docker-compose up

## Monitoring Prometheus/Grafana

Métriques recommandées :

Taux de requêtes / erreurs

Temps de réponse (p50/p90/p99)

Taille du cache

Volume de conversions

## Architecture
```
User → Flask API → External Exchange API
   ↓          ↓        ↓
Response   Logging    Cache
   ↓          
Prometheus Metrics → Docker → Kubernetes Cluster
```

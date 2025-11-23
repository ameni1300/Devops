FROM python:3.11-slim

WORKDIR /app

# Copier les dépendances d'abord (optimisation du cache Docker)
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ .

# Exposer le port
EXPOSE 5000

# Variables d'environnement
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Commande de démarrage
CMD ["python", "app.py"]
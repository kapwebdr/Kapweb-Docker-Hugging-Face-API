FROM python:3.9

WORKDIR /app

# Copie des fichiers de dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# En environnement de développement, ces lignes sont essentiellement superflues
# car le code source est monté via les volumes de docker-compose.
# En production, décommentez la ligne COPY pour inclure les fichiers de l'application.
# COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
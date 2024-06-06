FROM python:3.8-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requisitos
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Establecer el PYTHONPATH para incluir /app y /core
ENV PYTHONPATH=/app:/app/core

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

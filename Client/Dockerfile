# Dockerfile para el cliente
FROM python:3.10.12

# Crear un directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación al directorio de trabajo
COPY . .

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8080 para acceder a la aplicación
EXPOSE 8080

# Ejecutar la aplicación cuando el contenedor se inicie
# CMD ["python", "client.py"]
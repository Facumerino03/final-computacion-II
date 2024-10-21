FROM python:3.8

# Crear un directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación al directorio de trabajo
COPY .. .

# Instalar las dependencias necesarias
RUN pip3 install --no-cache-dir -r requirements.txt

# Exponer el puerto 6000 para acceder a la aplicación
EXPOSE 6000

# Ejecutar la aplicación cuando el contenedor se inicie
CMD ["python", "client.py"]

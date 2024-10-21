# Imagen base de Python 3.8
FROM python:3.8-alpine3.15

# Crear un directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación al directorio de trabajo
COPY ../../.. .

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

#Instala dependencias del sistema
RUN apk add mariadb-dev py3-mysqlclient mysql-client

# Exponer el puerto 5000 para acceder a la aplicación
EXPOSE 5000

# Ejecutar la aplicación cuando el contenedor se inicie
CMD ["python", "server.py"]
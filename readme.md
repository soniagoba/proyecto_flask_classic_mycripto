# Proyecto Flask classic - MYCRIPTO

Aplicación web con flask para el registro de movimientos de compra-venta de criptomonedas. La aplicación consultará en www.coinapi.io el valor real en euros de las distintas criptomonedas para valorar si la inversión inicial ha crecido o no.

## Pasos para la instalación:

### Entorno virtual e instalaciones con pip install:

1. Crear un entorno virtual.
2. Instalar los diferentes programas, librerías, etc indicados en el archivo "requirements.txt" (pip install -r requirements.txt).


### API KEY:

1. Solicitar una api key a la página coinAPI.io. 
2. Incluirla en el fichero "config_template.py" ("aqui_tu_apikey").


### Crear base de datos Sqlite3:

1. En la carpeta "data", ejecuta el archivo "crear_tabla.py" para obtener la base de datos.
2. Introducir la ruta a la base de datos en el fichero "config_template.py" (data/operaciones.db).


### Fichero ".env_template":

1. Copiar el fichero '.env_template', renombrarlo a '.env' y elegir una de las opciones de FLASK_ENV (development).


### Fichero "config_template.py":

1. Renombrar el fichero "config_template.py" como "config.py".
2. Introducir en el lugar indicado en el fichero la ruta a la base de datos sqlite que se haya creado (data/operaciones.db). 
3. Introducir la API Key recibida de coinAPI.io en el lugar indicado en el fichero ("aqui_tu_apikey").
3. Introducir una secret key, necesaria para el correcto funcionamiento de flask. Puedes utilizar la página https://randomkeygen.com/ para generar una segura.

import requests
from requests import RequestException
from flask import flash

URL_TASA_ESPECIFICA = "https://rest.coinapi.io/v1/exchangerate/{}/{}?apikey={}"
CONNECT_ERROR = 699 # LLEVARLO A CARPETA ERRORS. Creo que lo puedo quitar
 
#----------------------------API-------------------------------

class APIError(Exception): #sACARLO A UNA CARPETA ERRORS
    pass

class ProcesaDatosApi: 
    def __init__(self, apikey, origen = "", destino = ""): #lA APIKEY IBA AQUÍ EN EL EJEMPLO PARA PODER HACER LUEGO LOS TESTS
        self.apikey = apikey
        self.origen = origen
        self.destino = destino
        self.tasa = 0.0
  
    #Obtengo la tasa de la api
    def obtener_tasa(self):
        try:
            respuesta = requests.get(URL_TASA_ESPECIFICA.format(
                self.origen,
                self.destino,
                self.apikey
            ))
        
        #No sé si esTO NO VA AQUÍ PORQUE PARECE QUE ESTOY REPITIENDO COSAS EN EL ROUTES:
        #Creo que se puede quitar - pendiente más pruebas
        except requests.RequestException: 
            raise APIError(CONNECT_ERROR)
        
        if respuesta.status_code != 200:
            raise APIError(respuesta.status_code)
        
        self.tasa = respuesta.json()["rate"]
            
        return self.tasa

    #Con la tasa calculo la cantidad de moneda que se adquiriría. De momento no la estoy usando. Lo he calculado directamente en routes
    def obtener_cantidad_to(self, cantidad_from):
        self.cantidad_to = round(cantidad_from / self.tasa , 2)
 
        return self.cantidad_to  

    def control_errores_api(self, e):
        if e.args[0] == 400:
            flash("Error en la petición.")
        elif e.args[0] == 401:
            flash("No autorizado - API key errónea.")
        elif e.args[0] == 403:
            flash("Prohibido - Tu API no tiene acceso a esta funcionalidad.")
        elif e.args[0] == 429:
            flash("Excedido el límite de peticiones de tu API key.")
        elif e.args[0] == 550: 
            flash("Sin datos - La moneda solicitada no existe en nuestra base de datos.")
        elif e.args[0] == 404 or e.args[0] == CONNECT_ERROR:
            flash("Imposible comunicar con la API. Inténtelo más tarde.")
        else: 
            flash("Sin información sobre el código {}.".format(e.args[0]))
        

import sqlite3 
from datetime import datetime

MONEDAS_TRABAJO = {"EUR", "ETH", "BNB", "LUNA", "SOL", "BTC", "BCH", "LINK", "ATOM", "USDT"} 
  
#-------------------------BDD---------------------------------
class ProcesaDatosBdd: 
    def __init__(self, file=":memory:"):
        self.origen_datos = file

    def haz_consulta(self, consulta, params=[]):
        con = sqlite3.connect(self.origen_datos)
        cur = con.cursor()

        cur.execute(consulta, params)

        if cur.description: #Si la consulta devuelve algo: select
            resultado = cur.fetchall()
        else: #Si la consulta no devuelve nada: insert
            resultado = None
            con.commit()
        
        con.close()

        return resultado

    def importar_registro(self):
     
        return self.haz_consulta("""
                SELECT date, time, moneda_from, cantidad_from, moneda_to, cantidad_to, precio_unitario
                FROM operaciones
                ORDER BY date
                """
        )   

    def guardar_registro(self, params):  
        
        return self.haz_consulta("""
        INSERT INTO operaciones (date, time, moneda_from, cantidad_from, moneda_to, cantidad_to, precio_unitario, tasa)
                    values (?, ?, ?, ?, ?, ?, ?, ?)
        """, params)

    
    def cantidades_to_por_moneda(self, moneda_to):
        resultado_cantidad_to = self.haz_consulta("""
                        SELECT cantidad_to
                        FROM operaciones
                        WHERE moneda_to = ?
                    """, (moneda_to,))

        return resultado_cantidad_to

    
    def cantidades_from_por_moneda(self, moneda_from):
        resultado_cantidad_from= self.haz_consulta("""
                        SELECT cantidad_from
                        FROM operaciones
                        WHERE moneda_from = ?
                    """, (moneda_from,))
        
        return resultado_cantidad_from



#--------------SALDO DE MONEDAS | WALLET--------------- 
    #PRIMERO HABÍA CREADO OTRA CLASE QUE HEREDABA DE LA ANTERIOR. PERO SOLO PARA UNA FUNCIÓN....?
    # ENCUENTRO ESTO Y FUNCIONA parece: (en la clase 20 llama a una función dentro de otra de la misma clase ante pregunta D. Revisar)
    #https://www.tutorialesprogramacionya.com/pythonya/detalleconcepto.php?punto=45&codigo=45&inicio=30
    #https://www.adamsmith.haus/python/answers/how-to-call-an-instance-method-in-the-same-class-in-python
    # PASA CADA VEZ SUBMIT POR AHÍ¿¿¿PUEDO HACER QUE EL WALLET SEA UN ATRIBUTO DE LA CLASE Y CALCULARLO CON LA FUNCIÓN DE DEBAJO??

    def generar_wallet(self):#Saldo de cada moneda disponible (INCLUYE EUR)    
    
        wallet = {"EUR": 0} 
        
        for cripto in MONEDAS_TRABAJO:
            #obtengo cantidad to y from de moneda como una lista de tuplas = [[1.2], [0.6]]
            cantidad_to_moneda = self.cantidades_to_por_moneda(cripto)
            cantidad_from_moneda = self.cantidades_from_por_moneda(cripto)
            importe_to = 0
            importe_from = 0
            for item in cantidad_to_moneda:
                importe_to += item[0]
            for item in cantidad_from_moneda:
                importe_from += item[0]
            saldo_moneda = importe_to - importe_from
            #Actualizamos el wallet
            if cripto not in wallet:
                wallet[cripto] = saldo_moneda
            else:
                wallet[cripto] += saldo_moneda
        return wallet

    def generar_lista_monedas_from(self):
        wallet = self.generar_wallet()
        lista_monedas_from = ["EUR"]
        for key in wallet:
            if wallet[key] > 0:
                lista_monedas_from.append(key)
        return lista_monedas_from


#------------------FECHA / HORA ---------------------------
    def obtener_fecha(self):
        date_no_format = datetime.now().date()
        date = date_no_format.strftime('%d-%m-%Y') #No consigo hacerlo en jinja
        return date
    
    def obtener_hora(self):
        time_milisegundos = str(datetime.now().time())
        time = (time_milisegundos.split("."))[0]
        return time

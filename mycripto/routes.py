import sqlite3
from mycripto import app
from flask import render_template, flash, request, url_for, redirect
from mycripto.models import ProcesaDatosBdd
from mycripto.forms import ComprasForm
from mycripto.models_api import ProcesaDatosApi, APIError


ruta_bdd = app.config["RUTA_BDD"]
api_key = app.config["API_KEY"]
data_manager = ProcesaDatosBdd(ruta_bdd)


@app.route("/")
def inicio():
    try:
        datos = data_manager.importar_registro()
        return render_template("movimientos.html", operaciones=datos)
    except sqlite3.Error as e:
        flash("Error en la base de datos (INICIO). Inténtelo pasados unos minutos.")
        return render_template("movimientos.html", operaciones=[])

@app.route("/purchase", methods=["GET", "POST"])
def compra(): 
    form = ComprasForm()
    
    try:
        #Paso cada vez por aquí... NO PUEDE SER. tiene que ir dentro del get...
        wallet = data_manager.generar_wallet()   
        lista_monedas_from = data_manager.generar_lista_monedas_from()
    except sqlite3.Error as e:
        flash("Error en la base de datos(WALLET / MONEDAS_FROM). Inténtelo pasados unos minutos.")
        return render_template("movimientos.html", operaciones=[])
    
    form.moneda_from.choices = lista_monedas_from #AQUÍ PASO LA LISTA DE MONEDAS AL FORMULARIO
        
    if request.method == "GET":
        return render_template("purchase.html", formulario=form) 
     
    else:    
        if form.aceptar.data:    
            if form.estado_boton_calcular.data != "1": 
                flash("Primero hay que calcular.")
                return render_template("purchase.html", formulario=form)
            
            #Esto para segunda vuelta tras mofificación en cantidad_to sin recalcular: (necesito evitar validate porque están monedas bloqueadas)
            elif form.cantidad_from_oculta.data != "" and float(form.cantidad_from_oculta.data) != form.cantidad_from.data:       
                
                if form.cantidad_from.data <= 0:
                    flash("Debe ser una cantidad positiva.")
                if form.moneda_from_oculta.data == "EUR": #Si es EUR no valido cantidad porque es infinita
                        pass
                else: 
                    if wallet[form.moneda_from_oculta.data] < form.cantidad_from.data:
                        flash("Solo tienes {} {} disponibles. Ajusta cantidad.".format(wallet[form.moneda_from_oculta.data], form.moneda_from_oculta.data))
                flash("Tienes que recalcular importe.")
                #Le vuelvo a pasar las monedas ocultas que están bloqueadas para que las renderice en el formulario:
                form.moneda_from.data = form.moneda_from_oculta.data
                form.moneda_to.data = form.moneda_to_oculta.data
            
                return render_template("purchase.html", formulario=form)
                
            else: #Si ha dado a aceptar y todo es ok:
                date = data_manager.obtener_fecha()
                time = data_manager.obtener_hora()
                
                tasa_float = float(form.cantidad_to_oculta.data) / float(form.cantidad_from_oculta.data)
                tasa = str(tasa_float)
                precio_unitario_float = float(form.cantidad_from_oculta.data) / float(form.cantidad_to_oculta.data)
                precio_unitario = str(precio_unitario_float)
                try:
                    data_manager.guardar_registro((date, time, form.moneda_from_oculta.data, form.cantidad_from_oculta.data, form.moneda_to_oculta.data, form.cantidad_to_oculta.data, precio_unitario, tasa))
                    flash("Registro guardado correctamente.")
                    return redirect(url_for("inicio"))
                except sqlite3.Error as e:
                    flash("Error en la base de datos (GUARDAR REGISTRO). Inténtelo pasados unos minutos.") #Creo que no llega nunca aquí y se podría quitar porque coge el del inicio de la compra
                    return render_template("movimientos.html", operaciones=[]) #Podría poner el mismo return en ambos casos?? redirect...
       
        if form.calcular.data:
            #Primera vuelta:
            if form.estado_boton_calcular.data != "1":
                if not form.validate():
                    return render_template("purchase.html", formulario=form)  
                else:
                    moneda_from = form.moneda_from.data
                    cantidad_from = float(form.cantidad_from.data) 
                    moneda_to = form.moneda_to.data 

            #Esto para segunda vuelta tras modificación en cantidad_to (necesito evitar validate porque están monedas bloqueadas)       
            elif form.estado_boton_calcular.data == "1": #Es mejor elif que else y usar solo else para cosas no contempladas??
                
                if form.cantidad_from_oculta.data != "" and float(form.cantidad_from_oculta.data) != form.cantidad_from.data:       
                    if form.moneda_from_oculta.data == "EUR": #Si es EUR no valido cantidad porque es infinita
                        pass
                    else: #Aquí usa el wallet, tengo que mete también try-except acceso BDD???
                        if wallet[form.moneda_from_oculta.data] < form.cantidad_from.data:
                            flash("Solo tienes {} {} disponibles. Ajusta cantidad.".format(wallet[form.moneda_from_oculta.data], form.moneda_from_oculta.data))
                            return render_template("purchase.html", formulario=form)
                        
                #Le vuelvo a pasar las monedas ocultas que están bloqueadas para que las renderice en el formulario:
                moneda_from = form.moneda_from_oculta.data
                cantidad_from = float(form.cantidad_from.data)
                moneda_to = form.moneda_to_oculta.data          
            
            try:
                data_manager_api = ProcesaDatosApi(api_key, moneda_from, moneda_to)
                tasa = data_manager_api.obtener_tasa() 
                cantidad_to = cantidad_from * float(tasa)
                form.cantidad_to.data = cantidad_to 
                form.cantidad_to_oculta.data = cantidad_to 
                estado_boton_calcular = "1"
                form.estado_boton_calcular.data = estado_boton_calcular
                cantidad_from_oculta = cantidad_from
                form.cantidad_from_oculta.data = cantidad_from_oculta
                # Guardamos las monedas en el oculto para no perderlas tras deshabilitarlas:
                form.moneda_from.data = moneda_from
                form.moneda_from_oculta.data = moneda_from
                form.moneda_to.data = moneda_to
                form.moneda_to_oculta.data = moneda_to
                # Bloqueamos monedas;
                monedas_deshabilitadas = 1
                form.monedas_deshabilitadas.data = monedas_deshabilitadas

                #Esto se puede quitar o modificar o sacar a función porque lo tengo también en aceptar al guardar el registro en la bdd
                precio_unitario_float = float(form.cantidad_from_oculta.data) / float(form.cantidad_to_oculta.data)
                precio_unitario = str(precio_unitario_float) #Lo guardo por si puedo añadir funcionalidad (que compare los precios para orientar o desaconsejar nuevas operaciones)
                return render_template("purchase.html", formulario=form, precio_unitario_float=precio_unitario_float)               
           
            except APIError as e: 
                data_manager_api.control_errores_api(e)
                return redirect(url_for("inicio"))    

@app.route("/status")
def status():
    
    #-------EUROS INVERTIDOS------
    try:
        euros_invertidos_lista_tuplas = data_manager.cantidades_from_por_moneda("EUR")
        
        invertido_euros = 0
        if len(euros_invertidos_lista_tuplas) == 0:
            flash("Aún no ha invertido Euros.")
            #return render_template("status.html")
        else:
            for movimiento in euros_invertidos_lista_tuplas:
                invertido_euros += movimiento[0] 
    except sqlite3.Error as e:
        flash("Error en la base de datos (STATUS EUR INVERTIDOS). Inténtelo pasados unos minutos.")
        return render_template("movimientos.html", operaciones=[]) 

      
    #---------SALDOS DE CADA MONEDA (INCLUIDO EL EUR)---------      
         
    try:
        #Me traigo el wallet actualizado (EL WALLET INCLUYE EUROS):
        wallet = data_manager.generar_wallet()   #Diccionario moneda - saldo 
    except sqlite3.Error as e:
        flash("Error en la base de datos (STATUS -WALLET PARA SALDOS). Inténtelo pasados unos minutos.")
        return render_template("movimientos.html", operaciones=[])
        
    #Obtener tasa cambio € a las demás monedas en una sola llamada de ser posible
    valor_actual_criptos = 0 # Total menos euro
    saldo_euros_invertidos = wallet["EUR"]
    for key, value in wallet.items(): #Problema de separar es que recorro 2 veces el wallet. En models para los saldos y luego aquí para multiplicar por la tasa
        if key != "EUR" and wallet[key] != 0:
            try:
                data_manager_api = ProcesaDatosApi(api_key, key, "EUR")
                tasa = data_manager_api.obtener_tasa()
                moneda_cambiada_eur = wallet[key] * tasa
                valor_actual_criptos += moneda_cambiada_eur
          
            except APIError as e: 
                data_manager_api.control_errores_api(e)
                return redirect(url_for("inicio")) 
        else: #Es necesario el else?
            pass

    #-----------------VALOR ACTUAL TOTAL (según documentación proyecto)-------------------------

    valor_actual_total = invertido_euros + saldo_euros_invertidos + valor_actual_criptos #El valor actual es lo que has recuperado en € + valor en € de las criptomonedas.
    
    #------------------RESULTADO DE LA INVERSIÓN --------------------

    resultado_neto_inversion = invertido_euros - valor_actual_total

    return render_template("status.html", wallet=wallet, valor_actual_total=valor_actual_total, invertido_euros=invertido_euros, valor_actual_criptos=valor_actual_criptos, resultado_neto_inversion=resultado_neto_inversion)

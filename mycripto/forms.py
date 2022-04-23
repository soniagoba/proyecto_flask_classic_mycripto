from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from mycripto.models import ProcesaDatosBdd

MONEDAS_TRABAJO = {"EUR", "ETH", "BNB", "LUNA", "SOL", "BTC", "BCH", "LINK", "ATOM", "USDT", "LOLA"} #Lola solo para probar error API


# Validadores adicionales para el campo "moneda_to": 
def validar_combinacion_monedas(formulario, campo): 
    if campo.data == formulario.moneda_from.data:
        raise ValidationError("Las monedas deben ser diferentes. Cambia tu selección.")
    if formulario.moneda_from.data == "EUR" and campo.data != "BTC":
        raise ValidationError("Desde EUR solo se cambia a BTC. Cambia tu selección.")
    if formulario.moneda_from.data != "BTC" and campo.data == "EUR":
        raise ValidationError("Cambio a EUR solo desde BTC. Cambia tu selección.")
           
# Validadores adicionales para el campo "cantidad_from":  
def validar_cantidad_from(formulario, campo): 
    if campo.data == "":
        raise ValidationError("Introduce cantidad.") #NO pasa por aquí porque me salta un error con un bocadillo "!Competa este campo!????
    elif campo.data <= 0:
        raise ValidationError("Debe ser una cantidad positiva.")
    elif campo.data >= 1000000:
        raise ValidationError("Máximo por operación: 1.000.000")
    else:
        if formulario.moneda_from.data  == "EUR":
            pass
        else:
            data_manager = ProcesaDatosBdd("data/operaciones.db")
            wallet = data_manager.generar_wallet()
            if campo.data > wallet[formulario.moneda_from.data]:
                raise ValidationError("Solo tiene {} {} disponibles. Ajusta cantidad.".format(wallet[formulario.moneda_from.data], formulario.moneda_from.data))

class ComprasForm(FlaskForm):  
    moneda_from = SelectField("Moneda origen:") # coerce=str: El coerc creo que coje el str por defecto. Lo puedo quitar
    moneda_from_oculta = HiddenField("Moneda_from_oculta")
    cantidad_from = FloatField("Cantidad origen:", validators=[DataRequired("Indicar una cantidad positiva."), validar_cantidad_from])
    cantidad_from_oculta = HiddenField("Cantidad_from_oculta")
    moneda_to = SelectField("Moneda destino:", choices=MONEDAS_TRABAJO, validators=[validar_combinacion_monedas]) 
    moneda_to_oculta = HiddenField("Moneda_to_oculta")
    cantidad_to = FloatField("Cantidad destino:")
    cantidad_to_oculta = HiddenField("Cantidad_to_oculta")
    estado_boton_calcular = HiddenField("Estado_boton_calcular")
    monedas_deshabilitadas = HiddenField("Estado_deshabilitado")
    calcular = SubmitField("Calcular:") 
    aceptar = SubmitField("✔")
     
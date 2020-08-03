from mindmeld import Application
from mindmeld.components.dialogue import AutoEntityFilling
import screening_app.prediabetes as pd

app = Application(__name__)


@app.handle(intent='greet')
def welcome(request, responder):
    """
    When the user begins the conversation with a greeting. Explain the system options.
    """

    responder.reply(('Bienvenido al sistema de evaluación de salud. Mediante unas'
                     ' sencillas preguntas, puedo ayudarte a determinar tu riesgo'
                     ' a padecer prediabetes. Desea conocer su riesgo de padecer prediabetes?'))


@app.handle(intent='exit')
def say_goodbye(request, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    # Clear the dialogue frame to start afresh for the next user request.
    responder.frame = {}

    # Respond with a random selection from one of the canned "goodbye" responses.
    responder.reply(['Gracias por su visita. Adios!',
                     'Gracias por su visita. Hasta luego!',
                     'Gracias por su visita. Que tenga buen día.'])


@app.handle(intent='answer_no')
def handle_rejection(request, responder):
    """
    When the user rejects the screening, gracefully exit the conversation.
    """
    # Clear the dialogue frame to start afresh for the next user request.
    responder.frame = {}

    responder.reply(['Estamos para servirle. Gracias por su visita.'])


@app.auto_fill(intent='opt_in', form=pd.form_prediabetes)
def screen_prediabetes(request, responder):
    """
    If the user accepts the sceening, begin a dialogue flow.
    """

    for entity in request.entities:
        if entity['type'] == 'sys_number':
            if entity['role'] == 'age':
                responder.frame[pd.Q_AGE] = entity['value'][0]['value']
            elif entity['role'] == 'height':
                responder.frame[pd.Q_HEIGHT] = entity['value'][0]['value']
            else:  # Weight
                responder.frame[pd.Q_WEIGHT] = entity['value'][0]['value']
        elif entity['type'] == 'unit':
            if entity['role'] == 'height':
                if entity['value'][0]['cname'] == 'Metros':
                    if len(str(int(responder.frame[pd.Q_HEIGHT]))) > 1:
                        # Number was given in centimeters, convert to meters
                        responder.frame[pd.Q_HEIGHT] = responder.frame[pd.Q_HEIGHT] / 100
                    responder.frame[pd.Q_HEIGHT] = pd.meters_to_feet(responder.frame[pd.Q_HEIGHT])
            else:  # Weight unit
                if entity['value'][0]['cname'] == 'Kilogramos':
                    responder.frame[pd.Q_WEIGHT] = pd.kilos_to_pounds(responder.frame[pd.Q_WEIGHT])
        elif entity['type'] == 'binary':
            if entity['role'] == 'family_history':
                responder.frame[pd.Q_FAM] = entity['value'][0]['cname']
            elif entity['role'] == 'hbp':
                responder.frame[pd.Q_BP] = entity['value'][0]['cname']
            else:  # Active
                responder.frame[pd.Q_ACT] = entity['value'][0]['cname']
        else:  # Gender
            responder.frame[pd.Q_GENDER] = entity['value'][0]['cname']

    if responder.frame[pd.Q_GENDER] == 'Mujer':
        AutoEntityFilling(answer_subform,
                          pd.subform_prediabetes_female,
                          app).invoke(request, responder)
    else:
        risk = pd.calculate_risk_score(responder.frame)
        if risk >= 5:
            responder.reply(pd.HIGH_RISK_MSG)
        else:
            responder.reply(pd.LOW_RISK_MSG)


@app.handle(default=True)
def default(request, responder):
    welcome(request, responder)


def answer_subform(request, responder):
    """
    Fill the slot for gestational diabetes question asked only if gender is female.
    """

    entity = next((e for e in request.entities
                   if e['type'] == 'binary' and e['role'] == 'gestational_diabetes'), None)

    if entity:
        responder.frame[pd.Q_GEST] = entity['value'][0]['cname']

    risk = pd.calculate_risk_score(responder.frame)
    if risk >= 5:
        responder.reply(pd.HIGH_RISK_MSG)
    else:
        responder.reply(pd.LOW_RISK_MSG)

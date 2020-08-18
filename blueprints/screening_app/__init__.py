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
                     ' a padecer prediabetes. ¿Desea conocer su riesgo de padecer prediabetes?'))


@app.handle(intent='exit')
def say_goodbye(request, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    # Clear the dialogue frame to start afresh for the next user request.
    responder.frame = {}

    # Respond with a random selection from one of the canned "goodbye" responses.
    responder.reply(['Gracias por su visita. ¡Adios!',
                     'Gracias por su visita. ¡Hasta luego!',
                     'Gracias por su visita. ¡Que tenga buen día.'])


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

    value_map = {'age': pd.Q_AGE, 'weight': pd.Q_WEIGHT, 'height': pd.Q_HEIGHT}
    cname_map = {'family_history': pd.Q_FAM, 'hbp': pd.Q_BP, 'active': pd.Q_ACT}

    for entity in request.entities:
        if entity['type'] == 'sys_number':
            responder.frame[value_map[entity['role']]] = entity['value'][0]['value']
        elif entity['type'] == 'binary':
            responder.frame[cname_map[entity['role']]] = entity['value'][0]['cname']
        else:  # Gender
            responder.frame[pd.Q_GENDER] = entity['value'][0]['cname']

    if responder.frame[pd.Q_GENDER] == 'Mujer':
        AutoEntityFilling(answer_subform,
                          pd.subform_prediabetes_female,
                          app).invoke(request, responder)
    else:
        if pd.calculate_risk_score(responder.frame):
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

    if pd.calculate_risk_score(responder.frame):
        responder.reply(pd.HIGH_RISK_MSG)
    else:
        responder.reply(pd.LOW_RISK_MSG)

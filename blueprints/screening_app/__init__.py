from mindmeld import Application
import screening_app.prediabetes as pd

app = Application(__name__)

@app.handle(intent='greet')
def welcome(request, responder):
    """
    When the user begins the conversation with a greeting. Explain the system options.
    """
    #responder.params.allowed_intents = ['prediabetes_screening.answer_age']
    responder.reply('Bienvenido al sistema de evaluación de salud. ' +
    'Mediante unas sencillas preguntas, puedo ayudarte a determinar tu riesgo a padecer prediabetes. ' +
    'Desea conocer su riesgo de padecer prediabetes?')

@app.handle(intent='exit')
def say_goodbye(request, responder):
    """
    When the user ends a conversation, clear the dialogue frame and say goodbye.
    """
    # Clear the dialogue frame to start afresh for the next user request.
    responder.frame = {}

    # Respond with a random selection from one of the canned "goodbye" responses.
    responder.reply(['Gracias por su visita. Adios!', 'Gracias por su visita. Hasta luego!', 'Gracias por su visita. Que tenga buen día.'])
  
@app.handle(intent='answer_no')
def handle_rejection(request, responder):
    """
    When the user rejects the screening, gracefully exit the conversation.
    """
    # Clear the dialogue frame to start afresh for the next user request.
    responder.frame = {}
    
    responder.reply(['Estamos para servirle. Gracias por su visita.'])

@app.auto_fill(intent='answer_yes', form=pd.form_prediabetes)
def screen_prediabetes(request, responder):
    """
    If the user accepts the sceening, begin a dialogue flow.
    """

    for entity in request.entities:
        if entity['type'] == 'sys_number':
            if entity['role'] == 'age':
                responder.slots['age'] = entity['value'][0]['value']
            elif entity['role'] == 'height':
                responder.slots['height'] = entity['value'][0]['value']
            else: #Weight
                responder.slots['weight'] = entity['value'][0]['value']
        elif entity['type'] == 'unit':
            if entity['role'] == 'height':
                responder.slots['height_unit'] = entity['value'][0]['cname']
            else: #Weight unit
                responder.slots['weight_unit'] = entity['value'][0]['cname']
        elif entity['type'] == 'binary':
            if entity['role'] == 'family_history':
                responder.slots['family_history'] = entity['value'][0]['cname']
            elif entity['role'] == 'hbp':
                responder.slots['hbp'] = entity['value'][0]['cname']
            else: #Active
                responder.slots['active'] = entity['value'][0]['cname']
        else: #Gender
            responder.slots['gender'] = entity['value'][0]['cname']

    # TODO if gender is female ask additional question
    # else calculate results and reply.

    replies = ["Form completed."]
    responder.reply(replies)

# Remember the user may answer with explicit 'yes'. How do I handle 2 ways to start form with slot filling

@app.handle(default=True)
def default(request, responder):
    welcome(request, responder)

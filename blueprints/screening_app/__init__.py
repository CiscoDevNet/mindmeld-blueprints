from mindmeld import Application
import screening_app.prediabetes as pd

app = Application(__name__)

@app.handle(intent='greet')
def welcome(request, responder):
    """
    When the user begins the conversation with a greeting. Explain the system options.
    """
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


@app.dialogue_flow(domain='prediabetes_screening', intent='opt_in')
def screen_prediabetes(request, responder):
    """
    If the user accepts the sceening, begin a dialogue flow.
    """
    # Clear the dialogue frame to start fresh
    responder.frame = {}
        
    first_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=1)
    
    responder.frame['previous_question'] = first_question[0]['text']
    responder.frame['previous_question_number'] = first_question[0]['question_number']
    responder.frame['screening'] = dict()
    
    responder.reply(first_question[0]['text'])
    responder.listen()
    

@screen_prediabetes.handle(intent='answer_age')
def set_age_send_next(request, responder):
    """
    When the user provides their age, save the answer and move to the next question.
    """        
    previous_question = responder.frame['previous_question_number']    
    age_question = app.question_answerer.get(index='prediabetes_screening_questions', id=1)
    
    age_question_number = age_question[0]['question_number']
    
    if age_question_number is previous_question:
        number_entity = next((e for e in request.entities if e['type'] == 'sys_number'), None)
        if number_entity:
            responder.frame['screening'][previous_question] = number_entity['value'][0]['value']
            responder.frame['count'] = 0
            
            try:
                next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
                responder.frame['previous_question'] = next_question[0]['text']
                responder.frame['previous_question_number'] = next_question[0]['question_number']
                responder.reply(next_question[0]['text'])
                responder.listen()
                
                return
            except IndexError:
                # No more questions. Reply with results.
                risk = pd.calculate_risk_score(responder.frame['screening'])
                
                if risk >= 5:
                    responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                        ' Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
                else:
                    responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
                responder.exit_flow()  
                return
        else:
            # No age was provided. Re-ask question.
            question_text = age_question[0]['text']
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
    responder.frame['count'] = responder.frame.get('count', 0) + 1

    if responder.frame['count'] <= 3:
        responder.reply(question_text)
        responder.listen()
    else:
        responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
        responder.exit_flow()    

  
@screen_prediabetes.handle(intent='answer_gender')
def set_gender_send_next(request, responder):
    """
    When the user provides their gender, save the answer and move to the next question.
    """  
    previous_question = responder.frame['previous_question_number']
    gender_question = app.question_answerer.get(index='prediabetes_screening_questions', id=2)
    
    gender_question_number = gender_question[0]['question_number']
    
    if gender_question_number is previous_question:
        gender_entity = next((e for e in request.entities if e['type'] == 'gender'), None)
        if gender_entity:
            responder.frame['screening'][previous_question] = gender_entity['value'][0]['cname']
            responder.frame['count'] = 0
            
            try:
                if gender_entity['value'][0]['cname'] == 'Mujer':
                    next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
                else:
                    next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 2))
                
                responder.frame['previous_question'] = next_question[0]['text']
                responder.frame['previous_question_number'] = next_question[0]['question_number']
                responder.reply(next_question[0]['text'])
                responder.listen()
                
                return
            except IndexError:
                # No more questions. Reply with results.
                risk = pd.calculate_risk_score(responder.frame['screening'])
                
                if risk >= 5:
                    responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                        ' Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
                else:
                    responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
                responder.exit_flow()  
                return
        else:
            # No gender was provided. Re-ask question.
            question_text = gender_question[0]['text']
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
    responder.frame['count'] = responder.frame.get('count', 0) + 1

    if responder.frame['count'] <= 3:
        responder.reply(question_text)
        responder.listen()
    else:
        responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
        responder.exit_flow()  


@screen_prediabetes.handle(intent='answer_yes_gestational')
def confirm_gestational_send_next(request, responder):
    """
    When the user implicitly confirms having had gestational diabetes, save the answer and move to the next question.
    """          
    previous_question = responder.frame['previous_question_number']
    gestational_question = app.question_answerer.get(index='prediabetes_screening_questions', id=3)
    
    gestational_question_number = gestational_question[0]['question_number']
    
    if gestational_question_number is previous_question:
        responder.frame['screening'][previous_question] = True
        responder.frame['count'] = 0
            
        try:
            next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
            responder.frame['previous_question'] = next_question[0]['text']
            responder.frame['previous_question_number'] = next_question[0]['question_number']
            responder.reply(next_question[0]['text'])
            responder.listen()
            
            return
        except IndexError:
            # No more questions. Reply with results.
            risk = pd.calculate_risk_score(responder.frame['screening'])
                
            if risk >= 5:
                responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                    ' Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
            else:
                responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
            responder.exit_flow()  
            return
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
        responder.frame['count'] = responder.frame.get('count', 0) + 1

        if responder.frame['count'] <= 3:
            responder.reply(question_text)
            responder.listen()
        else:
            responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
            responder.exit_flow()


@screen_prediabetes.handle(intent='answer_yes_family')
def confirm_family_send_next(request, responder):
    """
    When the user implicitly confirms having family with diabetes, save the answer and move to the next question.
    """          
    previous_question = responder.frame['previous_question_number']
    family_question = app.question_answerer.get(index='prediabetes_screening_questions', id=4)
    
    family_question_number = family_question[0]['question_number']
    
    if family_question_number is previous_question:
        responder.frame['screening'][previous_question] = True
        responder.frame['count'] = 0
            
        try:
            next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
            responder.frame['previous_question'] = next_question[0]['text']
            responder.frame['previous_question_number'] = next_question[0]['question_number']
            responder.reply(next_question[0]['text'])
            responder.listen()
            
            return
        except IndexError:
            # No more questions. Reply with results.
            risk = pd.calculate_risk_score(responder.frame['screening'])
                
            if risk >= 5:
                responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                    ' Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
            else:
                responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
            responder.exit_flow()  
            return
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
        responder.frame['count'] = responder.frame.get('count', 0) + 1

        if responder.frame['count'] <= 3:
            responder.reply(question_text)
            responder.listen()
        else:
            responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
            responder.exit_flow()


@screen_prediabetes.handle(intent='answer_yes_hbp')
def confirm_hbp_send_next(request, responder):
    """
    When the user implicitly confirms having high blood pressure, save the answer and move to the next question.
    """          
    previous_question = responder.frame['previous_question_number']
    hbp_question = app.question_answerer.get(index='prediabetes_screening_questions', id=5)
    
    hbp_question_number = hbp_question[0]['question_number']
    
    if hbp_question_number is previous_question:
        responder.frame['screening'][previous_question] = True
        responder.frame['count'] = 0
            
        try:
            next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
            responder.frame['previous_question'] = next_question[0]['text']
            responder.frame['previous_question_number'] = next_question[0]['question_number']
            responder.reply(next_question[0]['text'])
            responder.listen()
            
            return
        except IndexError:
            # No more questions. Reply with results.
            risk = pd.calculate_risk_score(responder.frame['screening'])
                
            if risk >= 5:
                responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                    ' Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
            else:
                responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
            responder.exit_flow()  
            return
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
        responder.frame['count'] = responder.frame.get('count', 0) + 1

        if responder.frame['count'] <= 3:
            responder.reply(question_text)
            responder.listen()
        else:
            responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
            responder.exit_flow()


@screen_prediabetes.handle(intent='answer_yes_active')
def confirm_active_send_next(request, responder):
    """
    When the user implicitly confirms being physically active, save the answer and move to the next question.
    """          
    previous_question = responder.frame['previous_question_number']
    active_question = app.question_answerer.get(index='prediabetes_screening_questions', id=6)
    
    active_question_number = active_question[0]['question_number']
    
    if active_question_number is previous_question:
        responder.frame['screening'][previous_question] = True
        responder.frame['count'] = 0
            
        try:
            next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
            responder.frame['previous_question'] = next_question[0]['text']
            responder.frame['previous_question_number'] = next_question[0]['question_number']
            responder.reply(next_question[0]['text'])
            responder.listen()
            
            return
        except IndexError:
            # No more questions. Reply with results.
            risk = pd.calculate_risk_score(responder.frame['screening'])
                
            if risk >= 5:
                responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                    ' Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
            else:
                responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
            responder.exit_flow()  
            return
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
        responder.frame['count'] = responder.frame.get('count', 0) + 1

        if responder.frame['count'] <= 3:
            responder.reply(question_text)
            responder.listen()
        else:
            responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
            responder.exit_flow()
        

@screen_prediabetes.handle(intent='answer_height')
def set_height_send_next(request, responder):
    """
    When the user provides their height, save the answer and move to the next question.
    """          
    previous_question = responder.frame['previous_question_number']
    height_question = app.question_answerer.get(index='prediabetes_screening_questions', id=7)
    
    height_question_number = height_question[0]['question_number']
    
    if height_question_number is previous_question:
        number_entities = iter([e for e in request.entities if e['type'] == 'sys_number'])
        unit_entity = next((e for e in request.entities if e['type'] == 'unit'), None)
        
        main_number = next(number_entities, None)
        secondary_number = next(number_entities, None)
        
        if main_number:
            # Convert to feet and inches if in meters
            if unit_entity is None or len(unit_entity['value']) == 0 or unit_entity['value'][0]['cname'] in ['Metros', 'Centimetros']:
                if secondary_number is None:
                    number = main_number['value'][0]['value']
                    if len(str(int(number))) > 1: # Number was given in centimeters, convert to meters
                        number = number / 100
                else:
                    number = main_number['value'][0]['value'] + secondary_number['value'][0]['value'] / 100
                height = pd.meters_to_feet(number)
            else:
                if secondary_number is None:
                    height = str(main_number['value'][0]['value']) + '\'0"'
                else:
                    height = str(main_number['value'][0]['value']) + '\'' + str(secondary_number['value'][0]['value']) + '"'
                
            responder.frame['screening'][previous_question] = height
            responder.frame['count'] = 0
            
            try:
                next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
                responder.frame['previous_question'] = next_question[0]['text']
                responder.frame['previous_question_number'] = next_question[0]['question_number']
                responder.reply(next_question[0]['text'])
                responder.listen()
                
                return
            except IndexError:
                # No more questions. Reply with results.
                risk = pd.calculate_risk_score(responder.frame['screening'])
                
                if risk >= 5:
                    responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                        ' Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
                else:
                    responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
                responder.exit_flow()  
                return
        else:
            # No height was provided. Re-ask question.
            question_text = height_question[0]['text']
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
    responder.frame['count'] = responder.frame.get('count', 0) + 1

    if responder.frame['count'] <= 3:
        responder.reply(question_text)
        responder.listen()
    else:
        responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
        responder.exit_flow()


@screen_prediabetes.handle(intent='answer_weight')
def set_weight_send_next(request, responder):
    """
    When the user provides their weight, save the answer and move to the next question.
    """  
    previous_question = responder.frame['previous_question_number']
    weight_question = app.question_answerer.get(index='prediabetes_screening_questions', id=8)
    
    weight_question_number = weight_question[0]['question_number']
    
    if weight_question_number is previous_question:
        number_entity = next((e for e in request.entities if e['type'] == 'sys_number'), None)
        unit_entity = next((e for e in request.entities if e['type'] == 'unit'), None)
        
        if number_entity:
            # Convert to lbs if in kilograms
            if unit_entity is None or len(unit_entity['value']) == 0 or unit_entity['value'][0]['cname'] == 'Kilogramos':
                weight = pd.kilos_to_pounds(number_entity['value'][0]['value'])
            else:
                weight = number_entity['value'][0]['value']
            
            responder.frame['screening'][previous_question] = weight
            responder.frame['count'] = 0
            
            try:
                next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
                responder.frame['previous_question'] = next_question[0]['text']
                responder.frame['previous_question_number'] = next_question[0]['question_number']
                responder.reply(next_question[0]['text'])
                responder.listen()
                
                return
            except IndexError:
                # No more questions. Reply with results.
                risk = pd.calculate_risk_score(responder.frame['screening'])
                
                if risk >= 5:
                    responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                        ' Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
                else:
                    responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
                responder.exit_flow()  
                return
        else:
            # No age was provided. Re-ask question.
            question_text = age_question[0]['text']
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
    responder.frame['count'] = responder.frame.get('count', 0) + 1

    if responder.frame['count'] <= 3:
        responder.reply(question_text)
        responder.listen()
    else:
        responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
        responder.exit_flow()  


@screen_prediabetes.handle(intent='answer_yes')
def confirm_send_next(request, responder):
    """
    If the user accepts the sceening, begin a dialogue flow, or if the user
    answers with an explicit yes to a question, save the answer and move to the next question.
    """
    if 'previous_question_number' not in responder.frame:
        # Start questionnaire
        
        # Clear the dialogue frame to start fresh
        responder.frame = {}
        
        first_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=1)
    
        responder.frame['previous_question'] = first_question[0]['text']
        responder.frame['previous_question_number'] = first_question[0]['question_number']
        responder.frame['screening'] = dict()
    
        responder.reply(first_question[0]['text'])
        responder.listen()
        
        return
    
    previous_question = responder.frame['previous_question_number']
    question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=previous_question)       

    question_type = question[0]['type']
    question_id = question[0]['id']
    
    if question_type == 'Binary':
        if question_id == '3': # Gestational diabetes
            confirm_gestational_send_next(request, responder)
        elif question_id == '4': # Family with diabetes
            confirm_family_send_next(request, responder)
        elif question_id == '5': # High blood pressure
            confirm_hbp_send_next(request, responder)
        elif question_id == '6': # Physically active
            confirm_active_send_next(request, responder)
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
        
        responder.frame['count'] = responder.frame.get('count', 0) + 1

        if responder.frame['count'] <= 3:
            responder.reply(question_text)
            responder.listen()
        else:
            responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
            responder.exit_flow()
    

@screen_prediabetes.handle(intent='answer_no')
def negate_send_next(request, responder): 
    """
    When the user answers no to a question, save the answer and move to the next question.
    """  
    previous_question = responder.frame['previous_question_number']
    question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=previous_question)

    question_type = question[0]['type']
    
    if question_type == 'Binary':
        responder.frame['screening'][previous_question] = False
        responder.frame['count'] = 0
            
        try:
            next_question = app.question_answerer.get(index='prediabetes_screening_questions', question_number=str(int(previous_question) + 1))
            responder.frame['previous_question'] = next_question[0]['text']
            responder.frame['previous_question_number'] = next_question[0]['question_number']
            responder.reply(next_question[0]['text'])
            responder.listen()
            
            return
        except IndexError:
            # No more questions. Reply with results.
            risk = pd.calculate_risk_score(responder.frame['screening'])
                
            if risk >= 5:
                responder.reply('Usted presenta un riesgo elevado de padecer de prediabetes y de desarrollar diabetes tipo 2.' +
                    'Sólo un doctor puede darle un diagnóstico confiable por lo que recomendamos visite a su médico.')
            else:
                responder.reply('Su riesgo de padecer de prediabetes es bajo, sin embargo sólo un doctor puede darle un diagnóstico confiable.')
                    
            responder.exit_flow()  
            return
    else:
        # Answer is out of questionnaire flow. Re-ask question.
        question_text = responder.frame['previous_question']
    
    responder.frame['count'] = responder.frame.get('count', 0) + 1

    if responder.frame['count'] <= 3:
        responder.reply(question_text)
        responder.listen()
    else:
        responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
        responder.exit_flow()
            
 
@screen_prediabetes.handle(intent='opt_in')
def screen_prediabetes_in_flow_handler(request, responder):
    screen_prediabetes(request, responder)
    

@screen_prediabetes.handle(intent='exit')
def exit_questionnaire(request, responder):
    """
    When the user requests to cancel, say goodbye.
    """  
    say_goodbye(request, responder)
            
 
@screen_prediabetes.handle(default=True)
def default_handler(request, responder):
    responder.frame['count'] = responder.frame.get('count', 0) + 1
    if responder.frame['count'] <= 3:
        question_text = responder.frame['previous_question']
        responder.reply(question_text)
        responder.listen()
    else:
        responder.reply('Disculpe, no le he podido entender. Por favor intente de nuevo.')
        responder.exit_flow()  
        

@app.handle(default=True)
def default(request, responder):
    welcome(request, responder)

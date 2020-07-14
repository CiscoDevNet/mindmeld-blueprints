from mindmeld.core import FormEntity

Q_AGE = "1"
Q_GENDER = "2"
Q_GEST = "3"
Q_FAM = "4"
Q_BP = "5"
Q_ACT = "6"
Q_HEIGHT = "7"
Q_WEIGHT = "8"

one_pt_weight_cats = {
    '4\'10"': (119,142),
    '4\'11"': (124,147),
    '5\'0"': (128,152),
    '5\'1"': (132,157),
    '5\'2"': (136,163),
    '5\'3"': (141,168),
    '5\'4"': (145,173),
    '5\'5"': (150,179),
    '5\'6"': (155,185),
    '5\'7"': (159,190),
    '5\'8"': (164,196),
    '5\'9"': (169,202),
    '5\'10"': (174,208),
    '5\'11"': (179,214),
    '6\'0"': (184,220),
    '6\'1"': (189,226),
    '6\'2"': (194,232),
    '6\'3"': (200,239),
    '6\'4"': (205,245)
}

two_pt_weight_cats = {
    '4\'10"': (143,190),
    '4\'11"': (148,197),
    '5\'0"': (153,203),
    '5\'1"': (158,210),
    '5\'2"': (164,217),
    '5\'3"': (169,224),
    '5\'4"': (174,231),
    '5\'5"': (180,239),
    '5\'6"': (186,246),
    '5\'7"': (191,254),
    '5\'8"': (197,261),
    '5\'9"': (203,269),
    '5\'10"': (209,277),
    '5\'11"': (215,285),
    '6\'0"': (221,293),
    '6\'1"': (227,301),
    '6\'2"': (233,310),
    '6\'3"': (240,318),
    '6\'4"': (246,327)
}

three_pt_weight_cats = {
    '4\'10"': 191,
    '4\'11"': 198,
    '5\'0"': 204,
    '5\'1"': 211,
    '5\'2"': 218,
    '5\'3"': 225,
    '5\'4"': 232,
    '5\'5"': 240,
    '5\'6"': 247,
    '5\'7"': 255,
    '5\'8"': 262,
    '5\'9"': 270,
    '5\'10"': 278,
    '5\'11"': 286,
    '6\'0"': 294,
    '6\'1"': 302,
    '6\'2"': 311,
    '6\'3"': 319,
    '6\'4"': 328
}
    
def get_weight_category_score(height, weight):
    if height not in one_pt_weight_cats:
        # Height is out of measured range
        return 0
    
    w = float(weight)
    if one_pt_weight_cats[height][0] <= w <= one_pt_weight_cats[height][0]:
        return 1
    elif two_pt_weight_cats[height][0] <= w <= two_pt_weight_cats[height][0]:
        return 2
    elif three_pt_weight_cats[height] <= w:
        return 3
    else:
        return 0
        
def meters_to_feet(meters):
    feet = round(float(meters) // .3048)
    inches = round(float(meters) / .3048 % 1 * 12)
    
    return str(feet) + '\'' + str(inches) + '"'
    
def kilos_to_pounds(weight):
    return str(float(weight) * 2.2046)
    
def calculate_risk_score(answers):
    score = 0
    
    # Add points for age
    age = int(answers[Q_AGE])
    if 40 <= age <= 49:
        score += 1
    elif 50 <= age <= 59:
        score += 2
    elif 60 <= age:
        score += 3
        
    # Add a point if male
    if answers[Q_GENDER] == "Hombre":
        score += 1
    elif answers[Q_GEST]:
        # Add a point if had gestational diabetes
        score += 1
        
    # Add a point if has family with diabetes or high blood pressure
    score += sum([answers[Q_FAM], answers[Q_BP]])
    
    # Add point if not physically active
    if not(answers[Q_ACT]):
        score += 1
        
    # Add points for weight category
    score += get_weight_category_score(answers[Q_HEIGHT], answers[Q_WEIGHT])
    
    return score
    

form_prediabetes = {
    'entities':[
        FormEntity(
            entity='sys_number',
            role='age',
            responses=['¿Cuál es su edad?']
        ),
        # FormEntity(
        #     entity='gender',
        #     responses=['¿Es de género masculino o femenino?']
        # ),
        # FormEntity(
        #     entity='binary',
        #     role='family_history',
        #     responses=['¿Tiene algún familiar inmediato que haya sido diagnosticado con diabetes? Estos incluyen padre, madre, hermano o hermana.'],
        # ),
        # FormEntity(
        #     entity='binary',
        #     role='hbp',
        #     responses=['¿Alguna vez le han diagnosticado con tener presión alta?'],
        # ),
        # FormEntity(
        #     entity='binary',
        #     role='active',
        #     responses=['¿Realiza actividad física con regularidad?'],
        # ),
        # FormEntity(
        #     entity='sys_number',
        #     role='height',
        #     responses=['¿Cuánto mide en estatura?']
        # ),
        # FormEntity(
        #     entity='unit',
        #     role='height',
        #     responses=['¿Su respuesta fue en metros o pies?']
        # ),
        # FormEntity(
        #     entity='sys_number',
        #     role='weight',
        #     responses=['¿Cuál es su peso?']
        # ),
        # FormEntity(
        #     entity='unit',
        #     role='weight',
        #     responses=['¿Su respuesta fue en kilos o libras?']
        # ),
    ],
    'max_retries': 3,
    'exit_keys': ['cancelar', 'salir'],
    'exit_msg': 'Disculpe, no le he podido entender. Por favor intente de nuevo.'
}   

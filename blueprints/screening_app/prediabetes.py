Q_AGE = 0
Q_GENDER = 1
Q_GEST = 2
Q_FAM = 3
Q_BP = 4
Q_ACT = 5
Q_HEIGHT = 6
Q_WEIGHT = 7

LOW_RISK_MSG = ('Su riesgo de padecer de prediabetes es bajo, '
                'sin embargo sólo un doctor puede darle un diagnóstico confiable.')
HIGH_RISK_MSG = ('Usted presenta un riesgo elevado de padecer de prediabetes y de '
                 'desarrollar diabetes tipo 2. Sólo un doctor puede darle un '
                 'diagnóstico confiable por lo que recomendamos visite a su médico.')
WELCOME_MSG = ('Bienvenido al sistema de evaluación de salud. Mediante unas sencillas '
               'preguntas, puedo ayudarte a determinar tu riesgo a padecer prediabetes. '
               '¿Desea conocer su riesgo de padecer prediabetes?')

one_pt_weight_cats = {
    '4\'10"': (119, 142),
    '4\'11"': (124, 147),
    '5\'0"': (128, 152),
    '5\'1"': (132, 157),
    '5\'2"': (136, 163),
    '5\'3"': (141, 168),
    '5\'4"': (145, 173),
    '5\'5"': (150, 179),
    '5\'6"': (155, 185),
    '5\'7"': (159, 190),
    '5\'8"': (164, 196),
    '5\'9"': (169, 202),
    '5\'10"': (174, 208),
    '5\'11"': (179, 214),
    '6\'0"': (184, 220),
    '6\'1"': (189, 226),
    '6\'2"': (194, 232),
    '6\'3"': (200, 239),
    '6\'4"': (205, 245)
}

two_pt_weight_cats = {
    '4\'10"': (143, 190),
    '4\'11"': (148, 197),
    '5\'0"': (153, 203),
    '5\'1"': (158, 210),
    '5\'2"': (164, 217),
    '5\'3"': (169, 224),
    '5\'4"': (174, 231),
    '5\'5"': (180, 239),
    '5\'6"': (186, 246),
    '5\'7"': (191, 254),
    '5\'8"': (197, 261),
    '5\'9"': (203, 269),
    '5\'10"': (209, 277),
    '5\'11"': (215, 285),
    '6\'0"': (221, 293),
    '6\'1"': (227, 301),
    '6\'2"': (233, 310),
    '6\'3"': (240, 318),
    '6\'4"': (246, 327)
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
    if one_pt_weight_cats[height][0] <= w <= one_pt_weight_cats[height][1]:
        return 1
    elif two_pt_weight_cats[height][0] <= w <= two_pt_weight_cats[height][1]:
        return 2
    elif three_pt_weight_cats[height] <= w:
        return 3
    else:
        return 0


def meters_to_feet(meters):
    feet = round(float(meters) // .3048)
    inches = round(float(meters) / .3048 % 1 * 12)

    return f'{feet}\'{inches}"'


def kilos_to_pounds(weight):
    return str(float(weight) * 2.2046)


def calculate_risk_score(answers):
    """
    Risk score is calculated based on the questionnaire provided by
    the American Diabetes Association and the Centers for Disease Control and Prevention.
    https://www.cdc.gov/diabetes/risktest/index.html
    """
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
    elif answers[Q_GEST] in [1, 'si']:
        # Add a point if had gestational diabetes
        score += 1

    # Add a point if has family with diabetes
    if answers[Q_FAM] in [1, 'si']:
        score += 1

    # Add a point if high blood pressure
    if answers[Q_BP] in [1, 'si']:
        score += 1

    # Add point if not physically active
    if answers[Q_ACT] in [0, 'no']:
        score += 1

    # Add points for weight category
    score += get_weight_category_score(answers[Q_HEIGHT], answers[Q_WEIGHT])

    return score >= 5


def height_converter(request):
    number_entities = iter([e for e in request.entities if e['type'] == 'sys_number'])
    unit_entity = next((e for e in request.entities if e['type'] == 'unit'), None)

    main_number = next(number_entities, None)
    secondary_number = next(number_entities, None)

    if main_number:
        # Convert to feet and inches if in meters
        if (unit_entity is None or len(unit_entity['value']) == 0
                or unit_entity['value'][0]['cname'] in ['Metros', 'Centimetros']):
            if secondary_number is None:
                number = main_number['value'][0]['value']
            else:
                number = main_number['value'][0]['value']
                + secondary_number['value'][0]['value'] / 100
            height = meters_to_feet(number)
        else:
            if secondary_number is None:
                height = str(main_number['value'][0]['value']) + '\'0"'
            else:
                height = str(main_number['value'][0]['value']) +\
                     '\'' + str(secondary_number['value'][0]['value']) + '"'

        return height
    return False, {}


def weight_converter(request):
    number_entities = next((e for e in request.entities if e['type'] == 'sys_number'), None)
    unit_entity = next((e for e in request.entities if e['type'] == 'unit'), None)

    if number_entities:
        # Convert to lbs if in kilograms
        if (unit_entity is None or len(unit_entity['value']) == 0
           or unit_entity['value'][0]['cname'] == 'Kilogramos'):
            weight = kilos_to_pounds(number_entities['value'][0]['value'])
        else:
            weight = number_entities['value'][0]['value']

        return weight
    return False, {}

import json

questionaire_json = """
{
    "1": {
        "text":"¿Cuál es su edad?",
        "type":"Numeric"
    },
    "2": {
        "text":"¿Es de género masculino o femenino?",
        "type":"Gender"
    },
    "3": {
        "text":"¿Alguna vez ha sido diagnosticada con diabetes gestacional?",
        "type":"Binary"
    },
    "4": {
        "text":"¿Tiene algún familiar inmediato que haya sido diagnosticado con diabetes? Estos incluyen padre, madre, hermano o hermana.",
        "type":"Binary"
    },
    "5": {
        "text":"¿Alguna vez le han diagnosticado con tener presión alta?",
        "type":"Binary"
    },
    "6": {
        "text":"¿Realiza actividad física con regularidad?",
        "type":"Binary"
    },
    "7": {
        "text":"¿Cuánto mide en estatura?",
        "type":"Numeric"
    },
    "8": {
        "text":"¿Cuál es su peso?",
        "type":"Numeric"
    }
}
""" # noqa: ignore=E501

prediabetes_questions = json.loads(questionaire_json)

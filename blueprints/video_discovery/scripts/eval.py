from mmworkbench.components import NaturalLanguageProcessor
nlp = NaturalLanguageProcessor('../')
nlp.load()

dc = nlp.domain_classifier
dc_eval = dc.evaluate()

ic = nlp.domains['video_content'].intent_classifier
ic_eval = ic.evaluate()

er = nlp.domains['video_content'].intents['browse'].entity_recognizer
er_eval = er.evaluate()

print(dc_eval)
print(ic_eval)
print(er_eval)

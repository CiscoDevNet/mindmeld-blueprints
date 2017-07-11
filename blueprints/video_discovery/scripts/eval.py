import ipdb
from mmworkbench.components import NaturalLanguageProcessor
nlp = NaturalLanguageProcessor('../')
nlp.load()

ic = nlp.domains['video_content'].intent_classifier
ic_eval = ic.evaluate()

er = nlp.domains['video_content'].intents['browse'].entity_recognizer
er_eval = er.evaluate()
for result in er_eval.incorrect_results():
    if len(result.expected) != len(result.predicted):
        print(result.expected)
        print(result.predicted)
        continue
    for i in range(len(result.expected)):
        type = result.expected[i].entity.type
        if type == 'sys_interval' or type == 'sys_interval':
            print(result.expected[i].text)
            print(result.predicted[i].text)
            print(result.expected[i].entity.type)
            print(result.predicted[i].entity.type)
            print(result.expected[i].text)
            print(result.predicted[i].text)
            print(result.expected[i].span)
            print(result.predicted[i].span)
            ipdb.set_trace()

print(ic_eval)
print(er_eval)

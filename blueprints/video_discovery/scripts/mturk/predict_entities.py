"""Script for pre-annotation

Inputs: path to input text file with raw query on each line
Outputs: pre_annotate.txt with annotated query on each line (based on trained model)

*Assumes models have already been built (loads stored model)
"""

import argparse
from mmworkbench.components import NaturalLanguageProcessor

parser = argparse.ArgumentParser()
parser.add_argument(dest="input_file", type=str, help="Please provide input file path")
args = parser.parse_args()
input_file = args.input_file

nlp = NaturalLanguageProcessor('../mindmeld-blueprints/blueprints/video_discovery')
nlp.load()

with open(input_file, 'r') as queries:
    with open('pre_annotate.txt', 'w+') as predictions:
        for query in queries:
            query = query.rstrip()
            prediction = nlp.domains["video_content"]._children["browse"]\
                .entity_recognizer.predict(query)
            new_string = ''
            counter = 0
            for entity in prediction:
                entity_text = entity.text
                entity_start = entity.span.start
                entity_end = entity.span.end
                entity_type = entity.entity.type
                new_string += query[counter:entity_start]
                new_string += ('{' + entity_text + '|' + entity_type + '}')
                counter = entity.span.end + 1
            new_string += query[counter:]
            predictions.write(new_string + '\n')

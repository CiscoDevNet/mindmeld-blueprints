"""Script for extracting gazetteers from json data

Inputs: path to input json
Outputs: title.txt, cast.txt, director.txt, genre.txt
"""

import argparse
import json
import logging
import os
import sys

import pycountry

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def write_gazes(objs, output_dir, filename):
    output_file = os.path.join(output_dir, filename)
    with open(output_file, 'w') as fp:
        for gaz, count in sorted(objs.items(), key=lambda x: x[0]):
            fp.write(str(count) + '\t' + gaz + '\n')


def add_count(count_dict, entity):
    if not entity:
        return
    entity = str(entity)
    count = count_dict.get(entity, 0)
    count_dict[entity] = count + 1


def add_list_count(count_dict, entities):
    if not entities:
        return
    [add_count(count_dict, entity) for entity in entities]


def expand_country_names(country_codes):
    country_names = []
    for country_code in country_codes:
        country_names.append(country_code)
        try:
            country = pycountry.countries.get(alpha_2=country_code)
        except Exception:
            logging.error('Cannot find country name for {}'.format(country_code))
            continue
        country_names.append(country.name)
    return country_names


def main(args):
    input_file = args.input_file
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        logging.info('Folder {} not exist, creating one.'.format(output_dir))
        os.mkdir(output_dir)

    titles = {}
    casts = {}
    directors = {}
    genres = {}
    countries = {}

    logging.info('Reading data from {}.'.format(input_file))
    with open(input_file, 'r') as fp:
        for line in fp:
            json_text = line
            parsed_json = json.loads(json_text)
            add_count(titles, parsed_json['title'])

            add_list_count(casts, parsed_json['cast'])
            add_list_count(directors, parsed_json['directors'])
            add_list_count(genres, parsed_json['genres'])
            country_names = expand_country_names(parsed_json['countries'])
            add_list_count(countries, country_names)

    logging.info('Writing gazes to folder {}.'.format(output_dir))
    write_gazes(titles, output_dir, 'title.txt')
    write_gazes(casts, output_dir, 'cast.txt')
    write_gazes(directors, output_dir, 'director.txt')
    write_gazes(genres, output_dir, 'genre.txt')
    write_gazes(countries, output_dir, 'country.txt')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="input_file", type=str, help="Please provide input file path")
    parser.add_argument("-o", dest="output_dir", type=str, help="Please provide output dir path",
                        default='gazes')
    args = parser.parse_args()
    main(args)

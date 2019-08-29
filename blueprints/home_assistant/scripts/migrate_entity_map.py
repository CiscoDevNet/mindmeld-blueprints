#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""This script will perform a basic migration of entity data from an old style
app to a new mindmeld 3 compatible app.

This script will take each key from an old entity map and add it to
gazetteer.txt with a population of 1.0
"""
from argparse import ArgumentParser
import codecs
import logging
import json
import os

from mindmeld import configure_logs, path


def main():
    migrate_entity_map(**parse_args())


def migrate_entity_map(app_path, old_entity_map_path):
    """Populates gazetteer.txt files for each entity using an old entity map"""
    configure_logs(format='%(asctime)-15s: %(message)s')

    #  Load old entity map
    old_entity_map = load_json_file(old_entity_map_path)

    entity_types = path.get_entity_types(app_path)

    for e in old_entity_map['entities']:
        entity_type = e['entity-name']

        if entity_type not in entity_types:
            logging.info('Creating entity folder for %r', entity_type)
            # Create
            os.mkdir(os.path.relpath(path.get_entity_folder(app_path, entity_type)))
        mapping_path = path.get_entity_map_path(app_path, entity_type)
        if not os.path.exists(mapping_path):
            # Create an empty mapping.json for this entity
            dump_json_file(mapping_path, [])

        gaz_txt_path = path.get_entity_gaz_path(app_path, entity_type)
        entity_data_path = os.path.join(app_path, 'entity-data', '{}-entities.tsv').format(
            entity_type)

        try:
            entity_data = load_gazetteer_txt(entity_data_path)
        except OSError:
            entity_data = {}

        min_pop = min(entity_data.values()) if len(entity_data) else 1.0

        # fields which existed in an old style entity map
        map_fields = ['map', 'text-map', 'clause-map']
        for field in map_fields:
            try:
                entity_mappings = e[field]
            except KeyError:
                # no map of this type for this entity
                continue
            # TODO: create a new mapping.json from this info
            # This would only be possible when there are no commas and we have no
            for synonym in entity_mappings:
                #
                entity_data[synonym] = entity_data.get(synonym, min_pop)

        dump_gazetteer_txt(gaz_txt_path, entity_data)


def load_json_file(file_path):
    result = None
    with open(file_path) as json_file:
        result = json.load(json_file)
    return result


def dump_json_file(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=2, separators=(',', ': '))


def load_tsv_file(file_path, num_cols=None):
    with codecs.open(file_path, encoding='utf8') as data_file:
        for idx, row in enumerate(data_file):
            split_row = row.strip('\n').split('\t')
            if num_cols is None:
                num_cols = len(split_row)

            if len(split_row) != num_cols:
                msg = "Row {} of .tsv file '{}' malformed, expected {} columns"
                raise ValueError(msg.format(idx + 1, file_path, num_cols))

            yield split_row


def dump_tsv_file(file_path, rows):
    with codecs.open(file_path, 'w', encoding='utf8') as data_file:
        for row in rows:
            data_file.write('{}\n'.format('\t'.join((str(x) for x in row))))


def load_gazetteer_txt(file_path):
    # Loads gazetteer
    pop_dict = {}
    for pop, text in load_tsv_file(file_path):
        pop_dict[text] = pop
    return pop_dict


def dump_gazetteer_txt(file_path, pop_dict):
    rows = ((value, key) for key, value in pop_dict.items())
    dump_tsv_file(file_path, rows)


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def parse_args():
    parser = ArgumentParser(description="Get paths for ")
    parser.add_argument('-p', '--app-path', required=True,
                        help="the location of the app's data")
    parser.add_argument('-m', '--old-entity-map-path', required=True,
                        help="the location of the old entity map file")
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    main()

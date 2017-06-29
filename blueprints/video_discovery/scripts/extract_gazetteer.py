"""Script for extracting gazetteers from json data

Inputs: path to input json
Outputs: title.txt, cast.txt, director.txt, genre.txt
"""

import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument(dest="input_file", type=str, help="Please provide input file path")
args = parser.parse_args()
input_file = args.input_file

f = open(input_file, 'r')

titles = {}
casts = {}
directors = {}
genres = {}

for line in f:
    json_text = line
    parsed_json = json.loads(json_text)
    if parsed_json['title']:
        parsed_title = str(parsed_json['title'])
        if parsed_title in titles:
            titles[parsed_title] += 1
        else:
            titles[parsed_title] = 1
    for cast_member in parsed_json['cast']:
        parsed_cast = str(cast_member)
        if parsed_cast in casts:
            casts[parsed_cast] += 1
        else:
            casts[parsed_cast] = 1
    for director in parsed_json['directors']:
        parsed_director = str(director)
        if parsed_director in directors:
            directors[parsed_director] += 1
        else:
            directors[parsed_director] = 1
    for genre in parsed_json['genres']:
        parsed_genre = str(genre)
        if parsed_genre in genres:
            genres[parsed_genre] += 1
        else:
            genres[parsed_genre] = 1

f.close()

title_gaz = open('title.txt', 'w+')
cast_gaz = open('cast.txt', 'w+')
director_gaz = open('director.txt', 'w+')
genre_gaz = open('genre.txt', 'w+')

for title, count in titles.items():
    title_gaz.write(str(count) + '\t' + title + '\n')
for cast, count in casts.items():
    cast_gaz.write(str(count) + '\t' + cast + '\n')
for director, count in directors.items():
    director_gaz.write(str(count) + '\t' + director + '\n')
for genre, count in genres.items():
    genre_gaz.write(str(count) + '\t' + genre + '\t' + '\n')

genre_gaz.close()
director_gaz.close()
cast_gaz.close()
title_gaz.close()

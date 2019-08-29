import csv

first_line = True
with open('mturk.csv', 'r') as csvfile:
    with open('initial_mturk_data.txt', 'w+') as output:
        reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
        for line in reader:
            if first_line:
                first_line = False
                continue
            line = line[-4:]
            for query in line:
                if query != "{}":
                    output.write(query + '\n')

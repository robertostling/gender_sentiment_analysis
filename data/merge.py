import sys
import os
import csv
from collections import defaultdict
from pprint import pprint

#def read_old_annotations(filename):
#    text_label = {}
#    with open(filename, 'r', newline='') as f:
#        reader = csv.reader(f, delimiter='\t')
#        for row in reader:
#            text_label[(row[1], row[2])] = row[0]
#
#    return text_label
#
#
#def expand_joint_data(filename, text_label):
#    n_found = 0
#    with open(filename, 'r', newline='') as f:
#        reader = csv.DictReader(f, delimiter='\t')
#        for row in reader:
#            key = (row['Form'], row['Text'])
#            if key in text_label:
#                print(key)
#                n_found += 1
#    #print(f'Found {n_found} texts to match')


def read_annotations(filename):
    with open(filename, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)

    return reader.fieldnames, rows


def merge_annotations(all_rows):
    def get_key(row):
        return (row['Form'],
                row['Sentence'] if 'Sentence' in row else row['Text'])

    def merge_fields(rows):
        field_values = defaultdict(set)
        for row in rows:
            for k, v in row.items():
                field_values[k].add(v)
        for k, vs in field_values.items():
            if len(vs) != 1:
                print(f'WARNING: conflicting values: {k} -> {vs}')
                #raise ValueError(f'Conflicting values: {k} -> {vs}')
        return {k: vs.pop() for k, vs in field_values.items()}

    key_rows = defaultdict(list)
    for rows in all_rows:
        for row in rows:
            key_rows[get_key(row)].append(row)

    return [merge_fields(rows) for rows in key_rows.values()]


def write_annotations(filename, fieldnames, rows):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames, delimiter='\t',
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in rows:
            print(row)
            writer.writerow(row)


out_filename = sys.argv[1]
if os.path.exists(out_filename):
    print(f'Refusing to overwrite {out_filename}')
    sys.exit(1)
fields_rows = [read_annotations(filename) for filename in sys.argv[2:]]
merged_rows = merge_annotations([rows for _, rows in fields_rows])
write_annotations(out_filename,
                  sorted({k for row in merged_rows for k in row}),
                  merged_rows)

#text_label = read_old_annotations('cna_xin_robert_100.csv')
#expand_joint_data('cna_xin_forms.tsv', text_label)


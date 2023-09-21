# Script to convert Natalia's manually annotated English data to pyABSA 2
# format, as needed by train.py

import csv
import sys

with open(sys.argv[1], newline='', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        form = row['Form']
        sentence = row['Sentence']
        i = sentence.lower().index(form)
        sentiment = row['Sentiment_Manual_Natalia']
        print(sentence[:i] + '$T$' + sentence[i+len(form):])
        print(form)
        print(sentiment)


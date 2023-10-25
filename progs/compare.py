import sys
from pprint import pprint
from collections import Counter
import csv

import numpy as np
import sklearn.metrics

from examples import few_shot_examples

all_examples = {
        example[-1]
        for language, examples in few_shot_examples.items()
        for example in examples}

filename, gold_label, pred_label = sys.argv[1:]

with open(filename, newline='') as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    rows = list(reader)
    #data = [line.strip().split('\t') for line in f]


labels = 'Negative', 'Neutral', 'Positive'
label_index = {label:i for i,label in enumerate(labels)}

y_true = []
y_pred = []
confusion = np.zeros((len(labels), len(labels)), dtype=int)
#for gold, pred, target, text in data:
for row in rows:
    text = row['Sentence'] if 'Sentence' in row else row['Text']
    if text in all_examples:
        print('Skipping example from few-shot data')
        continue
    gold = row[gold_label]
    pred = row[pred_label]
    if gold not in ('Negative', 'Positive', 'Neutral'): continue
    if pred not in ('Negative', 'Positive', 'Neutral'): continue
    gold = label_index[gold]
    pred = label_index[pred]
    y_true.append(gold)
    y_pred.append(pred)
    confusion[(gold, pred)] += 1

print(confusion)
accuracy = (confusion * np.eye(len(labels))).sum() / (confusion.sum())
print(f'Accuracy: {100*accuracy:.1f}%')
print('F1:', sklearn.metrics.f1_score(y_true, y_pred,
                                      labels=list(range(len(labels))),
                                      average=None))
print('Macro F1:', sklearn.metrics.f1_score(y_true, y_pred, average='macro'))


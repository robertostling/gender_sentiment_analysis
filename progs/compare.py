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


gold_label, pred_label, *filenames = sys.argv[1:]

rows = []

for filename in filenames:
    with open(filename, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        rows.extend(list(reader))


labels = 'Negative', 'Neutral', 'Positive'
label_index = {label:i for i,label in enumerate(labels)}

y_true = []
y_pred = []
confusion = np.zeros((len(labels), len(labels)), dtype=int)
#for gold, pred, target, text in data:
n_fewshot = 0
n_excluded = 0
for row in rows:
    text = row['Sentence'] if 'Sentence' in row else row['Text']
    if text in all_examples:
        n_fewshot += 1
        continue
    gold = row[gold_label]
    pred = row[pred_label]
    if (not gold) or (not pred):
        continue
    if gold not in ('Negative', 'Positive', 'Neutral'):
        n_excluded += 1
        continue
    if pred not in ('Negative', 'Positive', 'Neutral'):
        n_excluded += 1
        continue
    gold = label_index[gold]
    pred = label_index[pred]
    y_true.append(gold)
    y_pred.append(pred)
    confusion[(gold, pred)] += 1

print(f'Skipped {n_fewshot} examples from few-shot data')
print(f'Skipped {n_excluded} examples with other tags')
print(f'Data points in evaluation: {confusion.sum()}')
print(confusion)
accuracy = (confusion * np.eye(len(labels))).sum() / (confusion.sum())
print(f'Accuracy: {100*accuracy:.1f}%')
print('F1:', sklearn.metrics.f1_score(y_true, y_pred,
                                      labels=list(range(len(labels))),
                                      average=None))
print('Macro F1:', sklearn.metrics.f1_score(y_true, y_pred, average='macro'))


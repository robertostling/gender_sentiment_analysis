"""Uses for paper:

python3 compare.py Manual gpt-3.5-turbo ../data/chinese_first300.tsv ../data/chinese_original.tsv.gpt-3.5-turbo.12345.0 
[[  6  17   0]
 [  9 102  25]
 [  0  12  22]]
Accuracy: 67.4%
F1: [0.31578947 0.76404494 0.54320988]
Macro F1: 0.5410147646825485

python3 compare.py Manual gpt-4 ../data/chinese_first300.tsv.gpt-4.12345.0 ../data/chinese_original.tsv.gpt-4.12345.0 
Skipped 12 examples from few-shot data
Data points in evaluation: 193
[[14  9  0]
 [24 87 25]
 [ 0  9 25]]
Accuracy: 65.3%
F1: [0.45901639 0.7219917  0.5952381 ]
Macro F1: 0.5920820633085104


"""
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
f1_scores = sklearn.metrics.f1_score(
        y_true, y_pred, labels=list(range(len(labels))), average=None)
macro_f1 = sklearn.metrics.f1_score(y_true, y_pred, average='macro')
print(f'Macro F1: {macro_f1:.3f}')
for label, f1 in zip(labels, f1_scores):
    print(f'    F1 for {label}: {f1:.3f}')


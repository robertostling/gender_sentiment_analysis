import sys
from pprint import pprint
from collections import Counter
import numpy as np

with open(sys.argv[1]) as f:
    data = [line.strip().split('\t') for line in f]


labels = 'Negative', 'Neutral', 'Positive'
label_index = {label:i for i,label in enumerate(labels)}

confusion = np.zeros((len(labels), len(labels)), dtype=int)
for gold, pred, target, text in data:
    if gold not in ('Negative', 'Positive', 'Neutral'): continue
    confusion[(label_index[gold], label_index[pred])] += 1

print(confusion)
#pprint(confusion.most_common())


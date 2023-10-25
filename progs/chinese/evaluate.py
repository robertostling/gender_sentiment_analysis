from pprint import pprint
import csv
from collections import Counter
import sys
import numpy as np

from pyabsa import available_checkpoints
from pyabsa import AspectPolarityClassification as APC

#ckpts = available_checkpoints()
#pprint(ckpts)


def read_data(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        return list(reader)


def evaluate_classifier(checkpoint, data):
    result = Counter()
    sentiment_classifier = APC.SentimentClassifier(checkpoint=checkpoint)
    for sentiment, form, text in data:
        i = text.index(form)
        assert i >= 0
        # The Chinese training data seems to be split into separate
        # characters, but this did not significantly change predictions
        #text = ' '.join(text)
        tagged_text = text[:i] + '[B-ASP]' + form + '[E-ASP]' \
                    + text[i+len(form):]
        prediction = sentiment_classifier.predict(
            text=tagged_text,
            print_result=True,
            ignore_error=False,
            eval_batch_size=32,
        )
        pred_sentiment = prediction['sentiment'][0]
        result[(sentiment, pred_sentiment)] += 1
    pprint(result.most_common())
    labels = ['Negative', 'Neutral', 'Positive']
    return np.array([
        [result[(actual, pred)] for pred in labels]
        for actual in labels])


data = read_data(sys.argv[1])
chinese = evaluate_classifier("chinese", data)
#custom = evaluate_classifier(
#        "fast_lsa_t_v2_erc_custom_eng_acc_86.47_f1_80.46", data)
#builtin = evaluate_classifier("multilingual", data)

print("Builtin Chinese model")
pprint(chinese)

#print("Custom model")
#pprint(custom)
#
#print("Builtin multilingual model")
#pprint(builtin)



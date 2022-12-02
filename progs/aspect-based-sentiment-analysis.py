# Adapted from:
# install pyabsa beforehand : https://github.com/yangheng95/PyABSA
# file: ensemble_classification_inference.py
# time: 05/11/2022 19:48
# author: yangheng <hy345@exeter.ac.uk>
# github: https://github.com/yangheng95
# GScholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# ResearchGate: https://www.researchgate.net/profile/Heng-Yang-17/research
# Copyright (C) 2022. All Rights Reserved.
import pandas as pd
import re
from pyabsa import AspectPolarityClassification as APC
# to check available models
from pyabsa import available_checkpoints
ckpts = available_checkpoints()

# loading model
# sent_classifier = APC.SentimentClassifier('fast_lcf_bert_Multilingual_acc_82.66_f1_82.06.zip')
sent_classifier = APC.SentimentClassifier('multilingual')
# sent_classifier = APC.SentimentClassifier('english')
# sent_classifier = APC.SentimentClassifier('chinese')

# load sentences from csv file (with Text field)
def get_sentences(filepath):
    df = pd.read_csv(filepath, sep="\t")
    return df.Text.to_list()

# English
fn = './English_fiction_woman_forR.txt'
fn2 = fn+'.asp.txt'
w = 'woman'

# French
fn = './French_news_2020.txt'
fn2 = fn+'.asp.txt'
w = 'femme'

#

examples = get_sentences(fn)
examples = [re.sub(w, "[B-ASP]" + w + "[E-ASP]", s, flags=re.I) for s in examples]
with open(fn2, mode="w") as fout:
    fout.write("\n".join(examples[0:100]))

#res = sent_classifier.predict(examples[0:20])#, save_result=True
sent_classifier.batch_predict(fn2, save_result=True)
#print(res)

import sys
import pickle
from pprint import pprint
import os.path
import csv

import numpy as np

# Argument: a directory where histwords zip files have been unpacked
histwords_path = sys.argv[1]

# https://github.com/wac81/Chinese-Sentiment/tree/master/Sentiment%20features/Sentiment%20dictionary%20features/sentiment%20dictionary%20source
# https://github.com/shekhargulati/sentiment-analysis-python/tree/master/opinion-lexicon-English

def load_sentiment_vectors(path_pattern, vocab_idx, m):
    with open(path_pattern.format('negative')) as f:
        negative_words = f.read().split()

    with open(path_pattern.format('positive')) as f:
        positive_words = f.read().split()

    positive_vocab = [w for w in positive_words if w in vocab_idx]
    negative_vocab = [w for w in negative_words if w in vocab_idx]
    positive_vectors = [m[vocab_idx[w]] for w in positive_vocab]
    negative_vectors = [m[vocab_idx[w]] for w in negative_vocab]

    return (negative_vocab, np.array(negative_vectors),
            positive_vocab, np.array(positive_vectors))


def load_embeddings(path_prefix):
    vocab_filename = path_prefix + '-vocab.pkl'
    array_filename = path_prefix + '-w.npy'
    m = np.load(array_filename)
    with open(vocab_filename, 'rb') as f:
        vocab = pickle.load(f)
    return vocab, m


def estimate_trajectories(sentiment_path_pattern, vectors_path, years,
                          target_words):
    result = {}
    for year in years:
        path_prefix = f'{vectors_path}/{year}'
        vocab, m = load_embeddings(path_prefix)
        vocab_idx = {w:i for i,w in enumerate(vocab)}
        negative_vocab, negative, positive_vocab, positive \
                = load_sentiment_vectors(sentiment_path_pattern, vocab_idx, m)

        print(f'Creating {year} model from {len(negative)} negative and '
              f'{len(positive)} positive items...')

        positive_centroid = np.mean(positive, axis=0)
        negative_centroid = np.mean(negative, axis=0)
        positivity = positive_centroid - negative_centroid
        centroid = 0.5 * (positive_centroid + negative_centroid)

        def project(v):
            return np.dot(v - centroid, positivity) \
                    / np.dot(positivity, positivity)

        target_vocab = [w for w in target_words if w in vocab_idx]
        target_m = np.array([m[vocab_idx[w]] for w in target_vocab])

        result[int(year)] = {
                word: project(v)
                for word, v in zip(target_vocab, target_m)}

    return result


TERM_LISTS = {
        'chinese': [
            ('adult', 'f', '女人', None),
            ('adult', 'm', '男人', None),
            ('not_adult', 'f', '女孩子 女孩儿 女孩', None),
            ('not_adult', 'm', '男孩子 男孩儿 男孩', None),
            ('parent', 'f', '母亲 妈妈', None),
            ('parent', 'm', '父亲 爸爸', None),
            ('child', 'f', '女儿', None),
            ('child', 'm', '儿子', None),
            ('sibling', 'f', '姐姐 妹妹 姐妹', None),
            ('sibling', 'm', '哥哥 弟弟 兄弟', None),
            ('spouse', 'f', '妻子', None),
            ('spouse', 'm', '丈夫', None),
            ('parent_in_law', 'f', '婆婆 岳母', None),
            ('parent_in_law', 'm', '公公 岳父', None),
             ],
        'english': [
            ('adult', 'f','woman', 's'),
            ('adult', 'f', 'women', 'p'),
            ('adult', 'm', 'man', 's'),
            ('adult', 'm', 'men', 'p'),
            ('not_adult', 'f', 'girl', 's'),
            ('not_adult', 'f', 'girls', 'p'),
            ('not_adult', 'm', 'boy', 's'),
            ('not_adult', 'm', 'boys', 'p'),
            ('parent', 'f', 'mother', 's'),
            ('parent', 'f', 'mothers', 'p'),
            ('parent', 'm', 'father', 's'),
            ('parent', 'm', 'fathers', 'p'),
            ('child', 'f', 'daughter', 's'),
            ('child', 'f', 'daughters', 'p'),
            ('child', 'm', 'son', 's'),
            ('child', 'm', 'sons', 'p'),
            ('sibling', 'f', 'sister', 's'),
            ('sibling', 'f', 'sisters', 'p'),
            ('sibling', 'm', 'brother', 's'),
            ('sibling', 'm', 'brothers', 'p'),
            ('spouse', 'f', 'wife', 's'),
            ('spouse', 'f', 'wives', 'p'),
            ('spouse', 'm', 'husband', 's'),
            ('spouse', 'm', 'husbands', 'p'),
            ('parent_in_law', 'f', 'mother-in-law', 's'),
            ('parent_in_law', 'f', 'mothers-in-law', 'p'),
            ('parent_in_law', 'm', 'father-in-law', 's'),
            ('parent_in_law', 'm', 'fathers-in-law', 'p'),
            ]}


def generate_table(filename, language, sentiment_path_pattern, vectors_path,
                   identifier, from_year, to_year):
    terms = TERM_LISTS[language]
    words = {form for _, _, forms, _ in terms
                  for form in forms.split()}
    years = list(range(from_year, to_year+10, 10))
    result = estimate_trajectories(
            sentiment_path_pattern, vectors_path, list(map(str, years)), words)
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow('model language concept gender form number year value'.split())
        for concept, gender, forms, number in terms:
            for form in forms.split():
                for year in years:
                    if form not in result[year]:
                        continue
                    value = result[year][form]
                    number = 'x' if number is None else number
                    writer.writerow([identifier, language, concept, gender,
                                     form, number, year, value])


generate_table('english-greenwald-fiction.tsv', 'english',
               'english/{}-greenwald.txt',
               os.path.join(histwords_path, 'eng-fiction-all', 'sgns'),
               'fiction_greenwald', 1900, 1990)

generate_table('english-greenwald-coha.tsv', 'english',
               'english/{}-greenwald.txt',
               os.path.join(histwords_path, 'coha-word', 'sgns'),
               'coha_greenwald', 1900, 1990)

generate_table('english-huliu-coha.tsv', 'english',
               'english/{}-words.txt',
               os.path.join(histwords_path, 'coha-word', 'sgns'),
               'coha_huliu', 1900, 1990)

generate_table('chinese-ntu.tsv', 'chinese', 'chinese/ntusd-{}.txt',
               os.path.join(histwords_path, 'chi-sim-all', 'sgns'),
               'ntu', 1950, 1990)


# Plotting code, expecting the output from estimate_trajectories:
#
#import pinyin
#from matplotlib import pyplot as plt
#from cycler import cycler
#
#def plot_result(result, filename=None):
#    default_cycler = (
#            cycler(color=['r', 'g', 'b', 'y', 'c', 'm', 'y', 'k']) +
#            cycler(linestyle=['-', '--', ':', '-.', '-', '--', ':', '-.']))
#    plt.rc('axes', prop_cycle=default_cycler)
#
#    vocab = {word for sentiments in result.values()
#                  for word in sentiments.keys()}
#    for word in vocab:
#        xs = sorted(result.keys())
#        ys = [result[x][word] for x in xs]
#        plt.plot(xs, ys, label=pinyin.get(word))
#    plt.legend()
#    if filename:
#        plt.savefig(filename)
#    plt.show()
#
#if False:
#    result = do_chinese(sys.argv[1])
#    plot_result(result, 'chinese.pdf')
#else:
#    result = do_english(sys.argv[1])
#    plot_result(result, 'english.pdf')
#pprint(result)


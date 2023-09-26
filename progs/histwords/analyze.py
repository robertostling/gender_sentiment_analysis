import sys
import pickle
from pprint import pprint
import os.path

from matplotlib import pyplot as plt
import numpy as np
import pinyin

# skiv:/home/corpora/histwords/chi-sim-all/sgns
# https://github.com/wac81/Chinese-Sentiment/tree/master/Sentiment%20features/Sentiment%20dictionary%20features/sentiment%20dictionary%20source
# https://github.com/shekhargulati/sentiment-analysis-python/tree/master/opinion-lexicon-English

def load_sentiment_vectors(path, vocab_idx, m):
    with open(os.path.join(path, 'negative.txt')) as f:
        negative_words = f.read().split()

    with open(os.path.join(path, 'positive.txt')) as f:
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


def estimate_trajectories(sentiment_path, histwords_path, years, target_words):
    result = {}
    for year in years:
        path_prefix = f'{histwords_path}/{year}'
        vocab, m = load_embeddings(path_prefix)
        vocab_idx = {w:i for i,w in enumerate(vocab)}
        negative_vocab, negative, positive_vocab, positive \
                = load_sentiment_vectors(sentiment_path, vocab_idx, m)

        print(f'Creating {year} model from {len(negative)} negative and '
              f'{len(positive)} positive items...')

        positivity = np.mean(positive, axis=0) - np.mean(negative, axis=0)

        def project(v):
            return np.dot(v, positivity) / np.dot(positivity, positivity)

        target_vocab = [w for w in target_words if w in vocab_idx]
        target_m = np.array([m[vocab_idx[w]] for w in target_vocab])

        result[int(year)] = {
                word: project(v)
                for word, v in zip(target_vocab, target_m)}

    return result


def do_chinese(histwords_path):
    target_words = ('女人 男人 妻子 丈夫 母亲 母親 父亲 父親 女儿 女兒 '
                    '儿子 兒子').split()
    result = estimate_trajectories(
            'chinese', os.path.join(histwords_path, 'chi-sim-all', 'sgns'),
            [str(year) for year in range(1950, 2000, 10)], target_words)
    return result

def do_english(histwords_path):
    target_words = (#'woman man wife husband mother father daughter son '
                    'women men wives husbands mothers fathres daughters sons '
                    #'good bad horrible terrible awesome fantastic great awful '
                    #'kind caring selfish worthless '
                    ).split()
    result = estimate_trajectories(
            'english', os.path.join(histwords_path, 'eng-fiction-all', 'sgns'),
            [str(year) for year in range(1900, 2000, 10)], target_words)
    return result


from cycler import cycler

def plot_result(result):
    default_cycler = (
            cycler(color=['r', 'g', 'b', 'y', 'c', 'm', 'y', 'k']) +
            cycler(linestyle=['-', '--', ':', '-.', '-', '--', ':', '-.']))
    plt.rc('axes', prop_cycle=default_cycler)

    vocab = {word for sentiments in result.values()
                  for word in sentiments.keys()}
    for word in vocab:
        xs = sorted(result.keys())
        ys = [result[x][word] for x in xs]
        plt.plot(xs, ys, label=pinyin.get(word))
    plt.legend()
    plt.show()

result = do_chinese(sys.argv[1])
#result = do_english(sys.argv[1])
pprint(result)
plot_result(result)


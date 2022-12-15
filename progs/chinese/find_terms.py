import sys

FORM_TABLE = {
        'woman': ['女人'],
        'man': ['男人'],
        'girl': ['女孩子', '女孩儿', '女孩兒', '女孩'],
        'boy': ['男孩子', '男孩儿', '男孩兒', '男孩'],
        'wife': ['妻子'],
        'husband': ['丈夫'],
        'mother': ['母亲', '母親', '妈妈', '媽媽'],
        'father': ['父亲', '爸爸', '父親'],
        'daughter': ['女儿', '女兒'],
        'son': ['儿子', '兒子'],
        'sister': ['姐姐', '妹妹',' 姐妹'], # '姐', '妹']
        'brother': ['哥哥', '弟弟', '兄弟'], # '哥', '弟'
        'mother-in-law': ['婆婆', '岳母'],
        'father-in-law': ['公公', '岳父'],
        }


def find_forms(filename):
    with open(filename) as f:
        for line in f:
            line = line.rstrip('\n')
            date, source, sentence = line.split('\t')
            for concept, forms in FORM_TABLE.items():
                for form in forms:
                    if form in sentence:
                        yield date[:4], concept, form, source, sentence
                        break


def main():
    print('Concept\tForm\tYear\tRegister\tSource\tText')
    for year, concept, form, source, sentence in find_forms(sys.argv[1]):
        print('\t'.join([concept, form, year, 'NEWS', source, sentence]))


if __name__ == '__main__':
    main()


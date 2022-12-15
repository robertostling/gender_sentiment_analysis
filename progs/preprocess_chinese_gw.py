import sys
import os.path
import gzip
import re
import glob

re_sentence = re.compile(r'[^。]+。')

def split_sentences(text):
    return re_sentence.findall(text)


def get_sentences(filename, text_types=('story',)):
    re_doc = re.compile(r'<DOC id="([A-Z]{3})_CMN_(\d+)\.\d+" type="(\w+)"\s*>')
    with gzip.open(filename, 'rt') as f:
        open_tags = set()
        text = ''
        doc_type = None
        date = None
        source = None
        for line in f:
            line = line.strip()
            m = re_doc.match(line)
            #print(m is None, open_tags, doc_type, date, source, line)
            if m:
                source = m.group(1)
                date = m.group(2)
                doc_type = m.group(3)
                open_tags.add('DOC')
            elif line in ('<TEXT>', '<P>'):
                open_tags.add(line[1:-1])
            elif line in ('</TEXT>', '</P>', '</DOC>'):
                open_tags.remove(line[2:-1])
                if line == '</P>' and doc_type == 'story':
                    for sentence in split_sentences(text):
                        yield date, source, sentence
                    text = ''
            else:
                if 'TEXT' in open_tags and 'P' in open_tags:
                    text += line.strip()

def main():
    gw_dir = sys.argv[1]
    # Iterate through all files in cna and xin subdirectories (only ones
    # dating back to 1991)
    filenames  = glob.glob(os.path.join(gw_dir, 'data/cna_cmn/cna_cmn_*.gz'))
    filenames += glob.glob(os.path.join(gw_dir, 'data/xin_cmn/xin_cmn_*.gz'))

    for filename in sorted(filenames):
        for date, source, sentence in get_sentences(filename):
            sentence = ' '.join(sentence.split())
            print(f'{date[:4]}\t{source}\t{sentence}')

if __name__ == '__main__':
    main()


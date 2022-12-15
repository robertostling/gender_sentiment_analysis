import sys
import os.path
import gzip
import re

def get_sentences(filename, text_types=('story',)):
    re_doc = re.compile(r'DOC id="([A-Z]{3})_CMN_(\d+)\.\d+" type="(\w+)">')
    with gzip.open(filename, 'rt') as f:
        for line in f:
            line = line.strip()
            m = re_doc.match(line)
            if m:
                source = m.group(1)
                date = m.group(2)
                doc_type = m.group(3)
                # Continue only if doc_type in text_types
                # Wait for <P> within <TEXT> inside the current <DOC>
                # Sentence-split using 。！？
                # Yield each sentence

def main():
    gw_dir = sys.argv[1]
    # Iterate through all files in cna and xin subdirectories (only ones
    # dating back to 1991)
    filename = os.path.join(gw_dir, 'data/cna_cmn/cna_cmn_199104.gz')
    for sentence in get_sentences(filename):
        print(sentence)

if __name__ == '__main__':
    main()


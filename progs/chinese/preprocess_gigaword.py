import sys
import os.path
import gzip
import re
import glob

from chinese_names.chinese_names import ChineseNames

cn = ChineseNames()

re_sentence = re.compile(r'[^。]+。')

def split_sentences(text):
    return re_sentence.findall(text)


def get_texts(filename, text_types=('story',)):
    re_doc = re.compile(r'<DOC id="([A-Z]{3})_CMN_(\d+)\.\d+" type="(\w+)"\s*>')
    with gzip.open(filename, 'rt') as f:
        open_tags = set()
        text = ''
        doc_type = None
        date = None
        source = None
        dateline_text = ''
        paragraphs = []
        for line in f:
            line = line.strip()
            m = re_doc.match(line)
            #print(m is None, open_tags, doc_type, date, source, line)
            if m:
                source = m.group(1)
                date = m.group(2)
                doc_type = m.group(3)
                open_tags.add('DOC')
            elif line in ('<TEXT>', '<P>', '<DATELINE>'):
                open_tags.add(line[1:-1])
            elif line in ('</TEXT>', '</P>', '</DATELINE>', '</DOC>'):
                open_tags.remove(line[2:-1])
                if line == '</P>' and doc_type == 'story':
                    #for sentence in split_sentences(text):
                    #    yield date, source, sentence, dateline_text
                    paragraphs.append(text)
                    text = ''
                elif line == '</DOC>':
                    yield date, source, paragraphs, dateline_text
                    dateline_text = ''
                    paragraphs = []
                    date = None
                    source = None
                    assert len(open_tags) == 0
            else:
                if 'TEXT' in open_tags and 'P' in open_tags:
                    text += line.strip()
                elif 'DATELINE' in open_tags:
                    dateline_text += line.strip()

def main():
    gw_dir = sys.argv[1]
    # Iterate through all files in cna and xin subdirectories (only ones
    # dating back to 1991)
    filenames = []
    filenames += sorted(glob.glob(
        os.path.join(gw_dir, 'data/xin_cmn/xin_cmn_*.gz')))
    filenames += sorted(glob.glob(
        os.path.join(gw_dir, 'data/cna_cmn/cna_cmn_*.gz')))

    # May want to be more inclusive about formats here
    re_writer = re.compile(r'\(记者(\w+)\)')

    for filename in filenames:
        # for date, source, sentence in get_sentences(filename):
        for date, source, paragraphs, dateline_text in get_texts(filename):
            date = f'{date[:4]}-{date[4:6]}-{date[6:]}'
            gender = '_'
            author = '_'
            if source == 'XIN':
                m = re_writer.search(dateline_text)
                if m is None:
                    m = re_writer.search(' '.join(paragraphs))
                if m is not None:
                    writer = m.group(1)
                    name = cn.parse(writer)
                    if name is not None and len(name.given_name) <= 2:
                        author = writer
                        if name.p_male >= 0.95:
                            gender = 'M'
                        elif name.p_female >= 0.95:
                            gender = 'F'
            for paragraph in paragraphs:
                for sentence in split_sentences(paragraph):
                    sentence = ' '.join(sentence.split())
                    print(f'{date}\t{source}\t{author}\t{gender}\t{sentence}')

if __name__ == '__main__':
    main()


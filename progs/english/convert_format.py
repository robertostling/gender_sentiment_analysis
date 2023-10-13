import sys

with open(sys.argv[1]) as f:
    lines = [line.strip() for line in f]
    for i in range(0, len(lines), 3):
        text, word, label = lines[i:i+3]
        text = text.replace('Ê', ' ').replace('$T$', word)
        print('\t'.join([label, word, text]))


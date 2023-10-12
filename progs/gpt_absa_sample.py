import os
import sys
import csv
from collections import defaultdict
import random
from operator import itemgetter

from openai import OpenAI

with open(os.path.join(os.getenv('HOME'), '.openai.key')) as f:
    api_key = f.read().strip()

client = OpenAI(api_key=api_key)
#chat, model = False, 'gpt-3.5-turbo-instruct'
chat, model = True, 'gpt-3.5-turbo'
#chat, model = True, 'gpt-4'
options = ['Positive', 'Negative', 'Neutral']

temperature = 1e-6
filename = sys.argv[1]
n_samples = int(sys.argv[2])
seed = 12345
random.seed(seed)
output_filename = f'{filename}.{model}.{seed}.{n_samples}'


def annotate(row):
    target = row['Form']
    text = row['Text'] if 'Text' in row else row['Sentence']

    if target.casefold() not in text.casefold():
        print(f'{target} not in {text}')
        return False

    if chat:
        completion = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                dict(
                    role='system',
                    content='You will guess the sentiment of the author '
                            'towards a particular object in a number of '
                            'sentences. Answer only with a single '
                            'word, one of the following: '
                            'Positive, Negative, Neutral. When in doubt, '
                            'answer Neutral.'),
                dict(
                    role='user',
                    content=f'Consider the following text:\n{text}\n'
                            f'What sentiment does the author convey towards '
                            f'the person/people referred to as "{target}"? '
                            f'[{"/".join(options)}]:'),
            ])
        prediction = completion.choices[0].message.content.strip().strip('.').capitalize()
    else:
        completion = client.completions.create(
                model=model,
                temperature=temperature,
                prompt='You will guess the sentiment of the author '
                            'towards a particular object in a number of '
                            'sentences. Answer only with a single '
                            'word, one of the following: '
                            'Positive, Negative, Neutral. When in doubt, '
                            'answer Neutral.\n\n'
                            f'Consider the following text:\n{text}\n'
                            f'What sentiment does the author convey towards '
                            f'the person referred to as "{target}"? '
                            f'[{"/".join(options)}]:')
        prediction = completion.choices[0].text.strip().strip('.').capitalize()
 
    if prediction not in options:
        print(f'Invalid answer: {prediction}')
        return False

    row[model] = prediction
    return True

with open(filename, newline='') as f:
    reader = csv.DictReader(f, delimiter='\t')
    rows = list(reader)

concept_gender_samples = defaultdict(list)
for row in rows:
    if 'Number' in row:
        concept_gender = (row['Concept'], row['Number'])
    else:
        concept_gender = row['Concept']
    #(row['ConceptPair'], row['Gender'])
    concept_gender_samples[concept_gender].append(row)

with open(output_filename, 'w', newline='') as f:
    writer = csv.DictWriter(
            f,
            delimiter='\t',
            fieldnames=reader.fieldnames + [model])
    writer.writeheader()
    for concept_gender, all_rows in sorted(concept_gender_samples.items(),
                                           key=itemgetter(0)):
        if n_samples >= len(all_rows):
            sample = all_rows
        else:
            sample = random.sample(all_rows, n_samples)

        for row in sample:
            success = annotate(row)
            if success:
                writer.writerow(row)
                print(row['Concept'], row[model])
            else:
                print(f'Failed!')


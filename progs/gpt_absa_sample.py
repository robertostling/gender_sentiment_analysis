import os
import sys
import csv
from collections import defaultdict
import random
from operator import itemgetter
from pprint import pprint
import re

from openai import OpenAI
from examples import few_shot_examples

if __name__ == '__main__':
    with open(os.path.join(os.getenv('HOME'), '.openai.key')) as f:
        api_key = f.read().strip()

    client = OpenAI(api_key=api_key)
    #chat, model = False, 'gpt-3.5-turbo-instruct'
    #chat, model = True, 'gpt-3.5-turbo'
    chat, model = True, 'gpt-4'
    options = ['Positive', 'Negative', 'Neutral']

    batch_size = 10 # Note, internal batching, nothing to do with OpenAI's API
    temperature = 1e-6
    filename = sys.argv[1]
    n_samples = int(sys.argv[2])
    language = sys.argv[3]
    assert language in ('eng', 'rus', 'zho')
    seed = 12345
    random.seed(seed)
    output_filename = f'{filename}.{model}.{seed}.{n_samples}'

    def generate_chat_prompt(examples, query_sentences):
        messages = [
            dict(
                role='system',
                content='You will guess the sentiment of the author '
                        'towards a particular person.'
                        #' Answer only with a single '
                        #'word, one of the following: '
                        #'Positive, Negative, Neutral.'
                        #' When in doubt, ' 'answer Neutral.'
                        )
            ]

        batches = [
                examples[:1+len(examples)//2],
                examples[1+len(examples)//2:]]

        for batch in batches:
            user_lines = []
            assistant_lines = []

            for idx, (label, word, text) in enumerate(batch):
                user_lines.append(
                    f'Question {idx+1}: what is the attitude towards "{word}" in '
                    f'the following text? <<< {text} >>>')
                assistant_lines.append(f'Answer {idx+1}:{label}')

            messages.append(dict(
                role='user',
                content='\n'.join(user_lines)))

            messages.append(dict(
                role='assistant',
                content='\n'.join(assistant_lines)))

        user_lines = []
        for idx, (word, text) in enumerate(query_sentences):
            user_lines.append(
                f'Question {idx+1}: what is the attitude towards "{word}" in '
                f'the following text? <<< {text} >>>')
     
        messages.append(dict(
            role='user',
            content='\n'.join(user_lines)))

        return messages


    def annotate_batch(language, rows):
        # Note: no checking is done here if the form is actually present in the
        # text
        query_sentences = [
                (row['Form'],
                 row['Text'] if 'Text' in row else row['Sentence'])
                for row in rows]
        completion = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=8*len(rows), # guesstimate, work out exact number
            messages=generate_chat_prompt(few_shot_examples[language],
                                          query_sentences))

        answers = completion.choices[0].message.content.strip().split('\n')
        pprint(answers)
        for line in answers:
            m = re.match(r'Answer (\d+):(Negative|Neutral|Positive)$', line)
            if m:
                idx = int(m.group(1))-1
                label = m.group(2)
                if 0 <= idx < len(rows):
                    rows[idx][model] = label

        n_annotated = sum(int(model in row) for row in rows)
        print(f'{n_annotated} of {len(rows)} in batch annotated')


    with open(filename, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        rows = list(reader)

    if n_samples > 0:
        concept_gender_samples = defaultdict(list)
        for row in rows:
            if 'Number' in row:
                concept_gender = (row['Concept'], row['Number'])
            else:
                concept_gender = row['Concept']
            #(row['ConceptPair'], row['Gender'])
            concept_gender_samples[concept_gender].append(row)
            
        selected_rows = []
        for concept_gender, all_rows in sorted(concept_gender_samples.items(),
                                               key=itemgetter(0)):
            if n_samples >= len(all_rows):
                sample = all_rows
            else:
                sample = random.sample(all_rows, n_samples)
            selected_rows.extend(sample)
        random.shuffle(selected_rows)
    else:
        selected_rows = rows


    print(f'Annotating {len(selected_rows)} items with {model} using '
          f'batch size {batch_size}')

    with open(output_filename, 'w', newline='') as f:
        writer = csv.DictWriter(
                f,
                delimiter='\t',
                quoting=csv.QUOTE_NONE,
                escapechar='\\',
                fieldnames=reader.fieldnames + [model])
        writer.writeheader()

        for i in range(0, len(selected_rows), batch_size):
            print(f'Annotating batch {i}:{i+batch_size} of {len(selected_rows)}')
            batch = selected_rows[i:i+batch_size]
            annotate_batch(language, batch)
            for row in batch:
                if model in row:
                    writer.writerow(row)
                    f.flush()



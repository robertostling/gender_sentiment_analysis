import os
import sys

from openai import OpenAI

with open(os.path.join(os.getenv('HOME'), '.openai.key')) as f:
    api_key = f.read().strip()

client = OpenAI(api_key=api_key)
#chat, model = False, 'gpt-3.5-turbo-instruct'
#chat, model = True, 'gpt-3.5-turbo'
chat, model = True, 'gpt-4'
options = ['Positive', 'Negative', 'Neutral']


with open(sys.argv[1]) as f:
    input_data = [line.strip().split('\t') for line in f]

for line_no, (gold_label, target, text) in enumerate(input_data):
    if target not in text:
        print(f'Line {line_no+1}: {target} not in {text}')
        continue

    if chat:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                dict(
                    role='system',
                    content='You will guess the sentiment of the author '
                            'towards a particular object in a number of '
                            'Chinese sentences. Answer only with a single '
                            'word, one of the following: '
                            'Positive, Negative, Neutral. When in doubt, '
                            'answer Neutral. About 65% of sentences are '
                            'neutral.'),
                dict(
                    role='user',
                    content=f'Consider the following text: {text}\n'
                            f'What is the sentiment of {target}? '
                            f'[{"/".join(options)}]:'),
            ])
        prediction = completion.choices[0].message.content.strip().strip('.').capitalize()
    else:
        completion = client.completions.create(
                model=model,
                prompt='You will guess the sentiment of the author '
                            'towards a particular object in a number of '
                            'Chinese sentences. Answer only with a single '
                            'word, one of the following: '
                            'Positive, Negative, Neutral. When in doubt, '
                            'answer Neutral. About 65% of sentences are '
                            'neutral.\n'
                            f'Consider the following text: {text}\n'
                            f'What is the sentiment of {target}? '
                            f'[{"/".join(options)}]:')
        prediction = completion.choices[0].text.strip().strip('.').capitalize()
 
    if prediction not in options:
        print(f'Invalid answer: {prediction}')
        continue

    print('\t'.join([gold_label, prediction, target, text]), flush=True)

    #if line_no > 2: break


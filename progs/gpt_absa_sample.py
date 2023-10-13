import os
import sys
import csv
from collections import defaultdict
import random
from operator import itemgetter
from pprint import pprint
import re

from openai import OpenAI

with open(os.path.join(os.getenv('HOME'), '.openai.key')) as f:
    api_key = f.read().strip()

client = OpenAI(api_key=api_key)
#chat, model = False, 'gpt-3.5-turbo-instruct'
chat, model = True, 'gpt-3.5-turbo'
#chat, model = True, 'gpt-4'
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

few_shot_examples = {
        'eng': [
            ('Neutral', # Positive
             'women',
             'tranquil and relaxed, telling a more conventional '
             'story than The Amazon about what makes women.'),
            ('Positive', # Neutral
             'woman',
             'The woman, an attractive lady apparently in her mid- thirties, '
             'bent over Rajiv to kiss'),
            ('Neutral', # Positive
             'boy',
             'head I imagined an enormous house, a mansion I had visited '
             'once as a boy.'),
            ('Neutral', # Negative
             'woman',
             'And the woman was sniffling and quietly weeping into her drink!'),
            ('Neutral', # Positive
             'daughters',
             'Gilliard was the tutor the imperial daughters had studied with '
             'all their lives, and Zoya knew he had gone to Siberia'),
            ('Negative', # Neutral
             'boys',
             "Though there couldn't have been more than six boys in all, "
             "they roared like school letting out."),
            ('Negative', # Positive
             'wife',
             'wound in her hair and small flowers framed a face far too '
             'lovely for the wife of Holt.'),
            ('Positive', # Negative
             'wife',
             'baronesses and baccarat and Josephine Baker singing.... Of '
             'course he had a cautious wife, with a small income of her own'),
            ('Neutral', # Negative
             'brother',
             "I suppose my brother must have died, for afterward I'm alone "
             "in the room."),
            ('Neutral', # Negative
             'sisters',
             '''you've betrayed your sisters' trust, " her mother said. "'''),
            ],
        'zho': [
            ('Negative', # Negative
             '爸爸',
             '彰化家扶中心輔導的男童小凱因爸爸入獄,媽媽離家,由70多歲的阿'
             '公扶養,阿公1人要照顧1家7口人,包括精神異常的伯父及91歲的曾'
             '祖母。'),
            ('Positive', # Positive
             '媽媽',
             '張薈茗表示,透過媒體看到第一線救災官兵的辛苦,相當心疼,'
             '因此今天特地前往水上空軍基地製作香噴噴、有媽媽味道的熱食,'
             '為他們加油打氣。'),
            ('Positive', # Neutral
             '父親',
             '片中的小女孩正是X、Y世代的象徵,穩重的父親則代表國民黨。'),
            ('Neutral', # Positive
             '女兒',
             '本身在市政府工作的強森,特地約好全家人在下班後參加開幕典禮,'
             '欣賞舞獅、緞帶舞、古箏、原住民舞蹈外,也讓兩個女兒聚精會神地'
             '坐在捏麵人前學著做雞造型的作品。'),
            ('Negative', # Neutral
             '兄弟',
             '于是一幕幕难忘的情景又在记者的眼前浮现:在盐湖城冬奥会上,率先'
             '冲过终点线的杨扬从冰面上站起身来,握紧拳头高声呐喊;申雪/赵宏博'
             '倾情演绎《图兰朵》,挑战世界最高难度的极限;孔令辉在悉尼奥运会'
             '上背水一战,获胜后狂吻胸前佩带的国徽,泪流满面;冰城与她的兄弟齐'
             '齐哈尔和佳木斯一起,悲壮地扛起中国冰球的所有艰难。'),
            ('Neutral', # Positive
             '丈夫',
             '前香港政務司司長陳方安生今天表示,香港政府應採取積極行動,協助'
             '被中國大陸扣押的新加坡海峽時報駐中國首席特派員程翔,使程翔妻子'
             '與丈夫會面。'),
            ('Neutral', # Negative
             '父親',
             '彭姓男子的女兒,原本和父親約在徐國禎律師事務所見面,因其父無'
             '故失蹤,懷疑遭人挾持,即向一分局北門派出所報案。'),
            ('Neutral', # Negative
             '儿子',
             '1998年我的大儿子受伤住院欠下不少外债,原本不富裕的生活变得举'
             '步维艰。'),
            ('Neutral', # Negative
             '女孩',
             '陳癸淼表示,九月四日有三個駐日美國大兵強暴日本女孩,結果美軍'
             '在日指揮官與美國國防部長立即向日本道歉,反觀我國部隊中死了那'
             '麼多人,國防部長卻從未表示任何歉意。'),
            ('Neutral', # Positive
             '妻子',
             '印度《瞭望》周刊的编辑夏尔马整场演出中都紧握着妻子的手,并不'
             '时用手和衣领拭去激动的泪水。'),
            ('Positive', # Negative
             '爸爸',
             '26日零时多,吴先生的三儿子吴乙丁打来电话,哭着说:“我爸爸走了!”'
             '听到噩耗的卢新华既吃惊又悲痛,没想到吴先生这么快就走了。'),
            ('Negative', # Negative
             '女兒',
             '被控在新加坡賭場偷籌碼的邱女今天上午出庭,由於偵訊中精神狀況'
             '不佳,法庭決先移送醫療評估;而邱母也趕赴法庭旁聽,並泣訴女兒病'
             '情不穩,早知道就不同意到新加坡工作。'),
            ('Neutral', # Neutral
             '母親',
             '全案中最無辜的就屬越籍的阮姓女子,因為她的家族在海防市是世家,'
             '母親曾移民法國,全家都受過高等教育,阮女並計畫赴法國深造,'
             '因為結識赴越工作的易某,不但放棄求學,還越洋嫁來台灣,沒想到'
             '卻落得婚姻無效,連承辦檢察官都相當同情。'),
        ]}


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


#def annotate(row):
#    target = row['Form']
#    text = row['Text'] if 'Text' in row else row['Sentence']
#
#    if target.casefold() not in text.casefold():
#        print(f'{target} not in {text}')
#        return False
#
#    if chat:
#        completion = client.chat.completions.create(
#            model=model,
#            temperature=temperature,
#            max_tokens=1,
#            messages=[
#                dict(
#                    role='system',
#                    content='You will guess the sentiment of the author '
#                            'towards a particular object in a number of '
#                            'sentences. Answer only with a single '
#                            'word, one of the following: '
#                            'Positive, Negative, Neutral. When in doubt, '
#                            'answer Neutral.'),
#                dict(
#                    role='user',
#                    content=f'Consider the following text:\n{text}\n'
#                            f'What sentiment does the author convey towards '
#                            f'the person/people referred to as "{target}"? '
#                            f'[{"/".join(options)}]:'),
#            ])
#        prediction = completion.choices[0].message.content.strip().strip('.').capitalize()
#    else:
#        completion = client.completions.create(
#                model=model,
#                temperature=temperature,
#                prompt='You will guess the sentiment of the author '
#                            'towards a particular object in a number of '
#                            'sentences. Answer only with a single '
#                            'word, one of the following: '
#                            'Positive, Negative, Neutral. When in doubt, '
#                            'answer Neutral.\n\n'
#                            f'Consider the following text:\n{text}\n'
#                            f'What sentiment does the author convey towards '
#                            f'the person referred to as "{target}"? '
#                            f'[{"/".join(options)}]:')
#        prediction = completion.choices[0].text.strip().strip('.').capitalize()
# 
#    if prediction not in options:
#        print(f'Invalid answer: {prediction}')
#        return False
#
#    row[model] = prediction
#    return True

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


    #for concept_gender, all_rows in sorted(concept_gender_samples.items(),
    #                                       key=itemgetter(0)):
    #    if n_samples >= len(all_rows):
    #        sample = all_rows
    #    else:
    #        sample = random.sample(all_rows, n_samples)

    #    for row in sample:
    #        success = annotate(row)
    #        if success:
    #            writer.writerow(row)
    #            print(row['Concept'], row[model])
    #        else:
    #            print(f'Failed!')


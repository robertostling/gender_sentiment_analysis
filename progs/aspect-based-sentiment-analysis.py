# Adapted from:
# install pyabsa beforehand : https://github.com/yangheng95/PyABSA
# file: ensemble_classification_inference.py
# time: 05/11/2022 19:48
# author: yangheng <hy345@exeter.ac.uk>
# github: https://github.com/yangheng95
# GScholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# ResearchGate: https://www.researchgate.net/profile/Heng-Yang-17/research
# Copyright (C) 2022. All Rights Reserved.
import pandas as pd
import re, json, os, logging
from glob import glob
import traceback
from pyabsa import AspectPolarityClassification as APC
# to check available models
from pyabsa import available_checkpoints
ckpts = available_checkpoints()

# loading model
# sent_classifier = APC.SentimentClassifier('fast_lcf_bert_Multilingual_acc_82.66_f1_82.06.zip')
sent_classifier = APC.SentimentClassifier('multilingual')
# sent_classifier = APC.SentimentClassifier('english')
# sent_classifier = APC.SentimentClassifier('chinese')

# load sentences from csv file (with Text field)
def get_sentences_csv(filepath):
    try:
        log.info(filepath)
        df = pd.read_csv(filepath, sep=",", on_bad_lines="skip", engine="python")
        #log.info(str(df.shape))
        #log.info(str(df.columns))
        #log.info(str(df.head()))
        #print(str(df.head()))
        return df['Text'].to_list()
    except Exception as e:
        var = traceback.format_exc()
        log.error("Error  while reading file with pandas. Error : " + var)  
        print("Error  while reading file with pandas. Error : " + var)  
        return False


def get_sentences_json(filepath):
    try:
        with open(filepath, mode="r") as fin:
            data= json.load(fin)
        return data
    except Exception as e:
        var = traceback.format_exc()
        log.error("Error  while reading file with json. Error : " + var)  
        print("Error  while reading file with json. Error : " + var)  
        return False

def generate_sentiment_csv_file_bk(fn, fn2, word):
        ''' This function will be removed when a id per sentence will be implmented in the sample file'''
        fn_final = fn2 + '.sentiment.csv'
        if os.path.isfile(fn2) is False:
            log.info(fn2 + " not existing. Check inputfile : " + fn + ', word : ' + word)
            print(fn2 + " not existing. Check inputfile : " + fn + ', word : ' + word)
            exit()
            #continue
        else:
            try:
                with open(fn)as fin:
                    contents = fin.read()# ast.literal_eval(fin.read())
                sentences = re.split('}, {', contents)
                res=[]
                print(len(sentences), ' sentences')
                for s in sentences:
                    data = {}
                    text = re.search(r"'text':\s(.+?), 'aspect':", s)
                    if text:
                        #print("MATCH : ", text.group(1))
                        t = re.sub(r"\\\"","'",text.group(1))
                        t = re.sub(r"\\\\'","'",t).strip()
                        t = re.sub(r"\\","",t)
                        t = re.sub(r"\s+,\s+",", ",t)
                        t = re.sub(r"(['’\(]) ",r"\1",t)
                        t = re.sub(r" ' | ',| '",r" ",t)
                        t = re.sub(r"''+","'",t)
                        t = re.sub(r"ex- ","ex-",t)

                        t = re.sub(r"[^\w\s]+", ' ',t)
                        t = re.sub(r"\s+"," ",t)
                        data['Text']= t[1:-1].strip()
                        #data['text_cmp']= data['Text'][0:50]
                    else:
                        print("No match for text : ", s)
                        exit()
                    aspect = re.search(r"'aspect':\s\['(.+?)'\],", s)
                    if aspect:
                        #print("MATCH : ", text.group(1))
                        data['aspect']= aspect.group(1)
                    else:
                        print("No match for aspect : ", s)
                        exit()
                    sentiment=  re.search(r"'sentiment':\s\['(.+?)'\],", s)
                    if sentiment:
                        #print("MATCH : ", text.group(1))
                        data['sentiment']= sentiment.group(1)
                    else:
                        print("No match for sentiment : ", s)
                        exit()
                    prob =  re.search(r"'confidence':\s\[(.+?)\],", s)
                    if prob:
                        #print("MATCH : ", text.group(1))
                        data['prob']= prob.group(1)
                    else:
                        print("No match for prob : ", s)
                        exit()
                    res.append(data)


                # generate csv file (one sentence per line)
                # dfinal = df1.merge(df2, on="movie_title", how = 'inner')
                df1 = pd.DataFrame(res)
                df1['strlen']= df1.Text.str.len()
                print(df1.head(10))
                print(df1.Text.to_list()[0:10])
                
                df2 = pd.read_csv(fn2)
                df2['Text'] = df2.Text.str.strip()
                df2['Text'] = df2.Text.str.replace(r'"',"'", regex=True)
                df2['Text'] = df2.Text.str.replace(r'\\\'',"'", regex=True)
                df2['Text'] = df2.Text.str.replace(r" ' | '",' ', regex=True)#.strip(punct)
                df2['Text'] = df2.Text.str.replace(r"([a-z])' ",r"\1 ", regex=True)#.strip(punct)
                df2['Text'] = df2.Text.str.replace(r" , ",", ", regex=True)#.strip(punct)
                df2['Text'] = df2.Text.str.replace(r"[^\w\s]+", ' ')
                df2['Text'] = df2.Text.str.replace(r"\s+", ' ')
                df2['Text'] = df2.Text.str.replace(word, word, flags=re.I)
                df2['Text'] = df2.Text.str.strip()
                #print(df2.info)
                df2['strlen']= df2.Text.str.len()
                #df2['text_cmp']= df2['Text'][0:50]
                print(df2.head(10))
                print(df2.Text.to_list()[0:10])
                dfinal =  df1.merge(df2, on="Text", how='outer',indicator=True) #, how = 'inner'
                print(dfinal.head(10))
                errors = dfinal[(dfinal._merge != 'both')].shape[0]
                if errors>0:
                    print(errors, ' errors, word : ', word, ' rows : ', dfinal[(dfinal._merge != 'both')])
                    dfinal[(dfinal._merge != 'both')][['Text','date','link','year','aspect','sentiment','prob']].to_csv(fn_final + '.errors.csv', index=False)
                    #exit()
                dfinal[(dfinal._merge == 'both')][['Text','link','year','aspect','sentiment','prob']].to_csv(fn_final, index=False)
                #print(dfinal.info)
                #exit()
            except Exception as e:
                var = traceback.format_exc()
                log.error("Error : " + var)  
                print("Error : " + var)  
                log.error("error : " + str(e))
                return False

def generate_sentiment_csv_file(fn, fn2, word):
        ''' This function will be removed when a id per sentence will be implmented in the sample file'''
        fn_final = fn2 + '.sentiment.csv'
        if os.path.isfile(fn2) is False:
            log.info(fn2 + " not existing. Check inputfile : " + fn + ', word : ' + word)
            print(fn2 + " not existing. Check inputfile : " + fn + ', word : ' + word)
            exit()
            #continue
        else:
            try:
                with open(fn)as fin:
                    contents = fin.read()# ast.literal_eval(fin.read())
                sentences = re.split('}, {', contents)
                res=[]
                print(len(sentences), ' sentences')
                for s in sentences:
                    data = {}
                    text = re.search(r"'text':\s(.+?), 'aspect':", s)
                    if text:
                        (id, Text) = text.group(1).split(' : ', 1)
                        data['Text']= Text.strip()
                        data['id']= id.strip()
                        #data['text_cmp']= data['Text'][0:50]
                    else:
                        print("No match for text : ", s)
                        exit()
                    aspect = re.search(r"'aspect':\s\['(.+?)'\],", s)
                    if aspect:
                        #print("MATCH : ", text.group(1))
                        data['aspect']= aspect.group(1)
                    else:
                        print("No match for aspect : ", s)
                        exit()
                    sentiment=  re.search(r"'sentiment':\s\['(.+?)'\],", s)
                    if sentiment:
                        #print("MATCH : ", text.group(1))
                        data['sentiment']= sentiment.group(1)
                    else:
                        print("No match for sentiment : ", s)
                        exit()
                    prob =  re.search(r"'confidence':\s\[(.+?)\],", s)
                    if prob:
                        #print("MATCH : ", text.group(1))
                        data['prob']= prob.group(1)
                    else:
                        print("No match for prob : ", s)
                        exit()
                    res.append(data)


                df1 = pd.DataFrame(res) 
                df1.set_index('id')
                # second file               
                df2 = pd.read_csv(fn2)

                #dfinal =  df1.merge(df2, on="Text", how='outer',indicator=True) #, how = 'inner'
                dfinal = df1.merge(df2, left_index=True, right_index=True,indicator=True)
                print(dfinal.head(10))
                errors = dfinal[(dfinal._merge != 'both')].shape[0]
                if errors>0:
                    print(errors, ' errors, word : ', word, ' rows : ', dfinal[(dfinal._merge != 'both')])
                    dfinal[(dfinal._merge != 'both')][['Text','date','link','year','aspect','sentiment','prob']].to_csv(fn_final + '.errors.csv', index=False)
                    #exit()
                dfinal[(dfinal._merge == 'both')][['Text','link','year','aspect','sentiment','prob']].to_csv(fn_final, index=False)
                #print(dfinal.info)
                #exit()
            except Exception as e:
                var = traceback.format_exc()
                log.error("Error : " + var)  
                print("Error : " + var)  
                log.error("error : " + str(e))
                return False



inputdir = '../corpora/'

# English
filetype='csv'
filenb='one'
fn = inputdir + 'English_fiction_woman_forR.txt'
fn2 = fn+'.asp.txt'
w = 'woman'


# French (json)

filetype='csv'
filenb='multiple'
files = glob(inputdir+ 'lemonde_1945_2020.*.sample.30.csv') 
words = ["femme","homme","fille","garçon","épouse","mari","mère","père","fils","soeur","frère","tante","oncle","femmes","hommes","filles","garçons","épouses","époux","maris","mères","pères","soeurs","frères","tantes","oncles"]


def main():
    try:
        if filetype=='csv' and filenb=='one':
            examples = get_sentences_csv(fn)
            examples = [re.sub(r"\b" + w + r"\b", "[B-ASP]" + w + "[E-ASP]", s, flags=re.I) for s in examples]
            with open(fn2, mode="w") as fout:
                for i, s in enumerate(examples):
                    if re.search('[B-ASP]',s):
                        fout.write(str(i) + " : " + s + "\n")
            #with open(fn2, mode="w") as fout:
            #    fout.write("\n".join(examples))

            # generate prediction file in apc_inference.result.json
            sent_classifier.batch_predict(fn2, save_result=True)
            # convert json file into format for regression analysis and visual exploration
            with open('apc_inference.result.json')as fin:
                contents = fin.read()
                data = json.loads(contents)
                print(data)
                os.rename('apc_inference.result.json',fn + '.sentiment.json')
                generate_sentiment_csv_file(fn + '.sentiment.json',fn, word)

        elif filetype=='csv' and filenb=='multiple':
            for fn in files:
                word = fn.split('.')[1]
                if os.path.isfile(inputdir+'apc_inference.result.json.'+ word + '.json'):
                    log.info(inputdir+'apc_inference.result.json.'+ word + '.json already generated')
                    continue
                fn2 = fn+'.asp.txt'
                examples = get_sentences_csv(fn)
                if examples is False:
                    log.info("error with this word :" + word + ', file : ' + fn)
                    exit()
                examples = [re.sub(r"\b" + word + r"\b", "[B-ASP]" + word + "[E-ASP]", s, flags=re.I) for s in examples]
                with open(fn2, mode="w") as fout:
                    for i, s in enumerate(examples):
                        if re.search('[B-ASP]',s):
                            fout.write(str(i) + " : " + s + "\n")
                # generate prediction file in apc_inference.result.json
                sent_classifier.batch_predict(fn2, save_result=True)
                with open('apc_inference.result.json')as fin:
                    contents = fin.read()
                    data = json.loads(contents)
                    print(data)
                    os.rename('apc_inference.result.json',inputdir+'apc_inference.result.json.'+ word + '.json')
                    generate_sentiment_csv_file(inputdir + 'apc_inference.result.json.'+ word + '.json',fn, word)
    except Exception as e:
        var = traceback.format_exc()
        log.error("Error : " + var)  
        print("Error : " + var)  
        log.error("error : " + str(e))
        return False


######### main
if __name__ == '__main__':
    log_dir = '../log/'
    os.makedirs(log_dir, exist_ok=True) 
    logstream = 'file'
    if logstream == 'file':
        print("messages sent to log file : " + log_dir +  os.path.basename(__file__) + ".log")
        FORMAT = "%(levelname)s:%(asctime)s:%(message)s[%(filename)s:%(lineno)s - %(funcName)s()]"
        logging.basicConfig(format=FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p', filename=log_dir + os.path.basename(__file__) + ".log",filemode="w", level=logging.INFO)    
        log = logging.getLogger(__name__)
    else:
        FORMAT = "%(levelname)s:%(asctime)s:%(message)s[%(filename)s:%(lineno)s - %(funcName)s()]"
        logging.basicConfig(format=FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p',stream=sys.stdout, level=logging.INFO)
        log = logging.getLogger(__name__)
    main()




import pysolr, json, requests, os,sys
import traceback
import logging
import logging.config
import pickle, re
import pandas as pd
from glob import glob
#import stanza
#nlp = stanza.Pipeline(lang='fr', processors='tokenize')

# get sentence from stanza => too long
def get_sentence_from_doc(word, contents):
    doc = nlp(contents)
    #res = []
    res = [sentence.text for sentence in doc.sentences if re.search(word,sentence.text,flags=re.I) ]
    #for sentence in doc.sentences:
    #    if re.search(word,sentence.text,flags=re.I):
    #        res.append(sentence.text)
    return res

# get sentences from regex => quite robust and fast : USE IT!
def get_sentences_from_doc(word, contents):
    sentences = re.split(r' *[\.\?!][\'"\)\]]* *', re.sub(r"\s+", " ", contents)) # replace \n with " " from input (meaningless in HTML source file)
    res = [s for s in sentences if re.search(word,s,flags=re.I) ]
    return res

# SOLR functions
def get_SOLR_collection_info(solr_host,solr_collection):
    ''' get solr collection info with pysolr'''
    try:
        solr = pysolr.Solr(solr_host+ solr_collection, search_handler='/schema/fields', use_qt_param=False)
        resp = solr._send_request('get', '/schema/fields')
        #print(resp)
        json_resp = json.loads(resp)
        #print(json_resp)
        for field in json_resp['fields']:
            print(field['name'], field['type'])
            if 'multiValued' in field:
                print('multiValued')
    except Exception as e:
        print("Error searching schema info -  Apache Solr :" + str(e))



def query_solr(solr, query, params):
   '''
   Query Solr with given query and parameters
   '''
   try:
       res = solr.search(query, **params)
       #print(res)
       return res
   except Exception as e:
        print("Error Apache Solr  search query :" + str(e))
        return False

def query_solr_all_results(solr,query, params):
    totalres = []
    totalhl={}
    # first check number of results (<50 == discard)
    done = False
    while done is False:
        results = query_solr(solr, query, params)
        #print(params['cursorMark'], ' / ', results.hits)
        #exit()
        for doc in results.docs:
            totalres.append(doc)
        totalhl.update(results.highlighting)
        #for doc in results.highlighting:
        #    totalhl.append(doc)
        if params['cursorMark'] == results.nextCursorMark:
            done = True
        params['cursorMark'] = results.nextCursorMark
    return totalres, totalhl

def query_solr_all_results_nohl(solr,query, params,word):
    totalres = []
    # first check number of results (<50 == discard)
    done = False
    while done is False:
        results = query_solr(solr, query, params)
        #print(params['cursorMark'], ' / ', results.hits)
        #exit()
        for doc in results.docs:
            #res = get_sentences_from_doc(word, doc['contents'][0])
            #log.info(str(len(res)) + " sentences in this doc")
            #print(res)
            #doc['sentences'] = res
            #del(doc['contents'])
            totalres.append(doc)
        if params['cursorMark'] == results.nextCursorMark:
            done = True
        params['cursorMark'] = results.nextCursorMark
    log.info("All docs are retrieved")
    return totalres

def read_csv_file_sample_sentences(filepath, timefield="date", sample=30):
    try:
        df = pd.read_csv(filepath, sep="\t", on_bad_lines="skip", engine="python")
        df[timefield]=pd.to_datetime(df[timefield],format='%Y-%m-%dT00:00:00Z') # 2016-07-19T00:00:00Z
        df['year'] =  df[timefield].dt.year
        df2 = df.groupby('year').head(sample).reset_index(drop=True)
        df2.to_csv(filepath+'.sample.'+str(sample)+'.csv', index=False)
        log.info("sample done for file : " + filepath + '. final Size : ' + str(df2.shape))
        #print()#nth(100)
        #res = df.resample(rule='3Y', on='date', label="right")
        #print(type(res))
        #print(res.groupby('date').nth(10))
        return True
    except Exception as e:
        var = traceback.format_exc()
        log.error("Error  while reading file with pandas. Error : " + var)  
        print("Error  while reading file with pandas. Error : " + var)  
        return False

def main():
    # Apache Solr parameters
    solr_host = 'https://tal.lipn.univ-paris13.fr/solr8/'
    solr_collection = 'lemonde_1945_2020'
    solr =  pysolr.Solr(solr_host+ solr_collection, always_commit=True)
    # check solr
    try : 
        solr.ping()
    except Exception as e:
        print("Problem with Apache Solr Server. Check error message : " + str(e))
        exit()

    # language
    #lang = 'es'
    # define task(s) and words
    #tasks = ['sentiment','emotion','hate_speech','all']
    task = 'all' # solr_query, get_sentences, sample_sentences
    outputdir = './corpora/'
    os.makedirs(outputdir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    words = ["femme","homme","fille","garçon","épouse","mari","mère","père","fils","soeur","frère","tante","oncle","femmes","hommes","filles","garçons","épouses","époux","maris","mères","pères","soeurs","frères","tantes","oncles"]


    # load sentences for each word from apache collection
    if task in ['all','solr_query']:
        print("*"*10 + "retrieving sentences from Solr Collection", ", check outputdir : " + outputdir)
        log.info("retrieving sentences from Solr Collection"+ ", check outputdir : " + outputdir)
        word_errors={}
        error_file = log_dir + os.path.basename(__file__) + '.solr_load_sentences.errors.json'
        for word in words:
                if isinstance(words, list):
                    word = word.strip()
                    if os.path.isfile(outputdir +solr_collection + '.'  +word+'.json'):
                        print("already retrieved. Skipping. (" + outputdir +solr_collection + '.' + word +'.json')
                        log.info("already retrieved. Skipping. (" + outputdir + solr_collection + '.' + word +'.json')
                        continue
                        
                    params = {
                            'sort':'link asc',
                            'rows':50,
                            'cursorMark':'*',
                            'fl':'contents,link,published'
                    }
                    print("retrieving data for : " + word)        
                    query = 'contents:"'+word+'"' 
                    try:
                        docs = query_solr_all_results_nohl(solr,query, params,word)
                        if docs:
                            json.dump(docs, open(outputdir +solr_collection + '.'+ word+'.json', mode='w'), indent=4)
                            print("Data stored in " + outputdir +solr_collection + '.'+ word+'.json')
                        else:
                            print("Error with this word (no sentences retrieved) " + word)
                    except Exception as e:
                        print("error with this word : " + word + '. Error : ' + str(e))
                        word_errors[word]=str(e)
                        continue

                # word family
                elif isinstance(words,dict) and isinstance(words[word], list):
                    for w in words[word]:
                        w = w.strip()
                        if os.path.isfile(outputdir +solr_collection + '.'  +w+'.json'):
                            print("already retrieved. Skipping. (" + outputdir  +solr_collection + '.' + w +'.json')
                            log.info("already retrieved. Skipping. (" + outputdir +solr_collection + '.'  + w +'.json')
                            continue
                            
                        params = {
                                'sort':'link asc',
                                'rows':50,
                                'cursorMark':'*',
                                'fl':'contents,link,published'
                        }
                        print("retrieving data for : " + w)        
                        query = 'contents:"'+word+'"' 
                        try:
                            docs = query_solr_all_results_nohl(solr,query, params,word)
                            if docs:
                                json.dump(docs, open(outputdir +solr_collection + '.'+ w+'.json', mode='w'), indent=4)
                                print("Data stored in " + outputdir +solr_collection + '.'+ w+'.json')
                            else:
                                print("Error with this word (no sentence retrieved) : " + w)
                        except Exception as e:
                            print("error with this word : " + w + '. Error : ' + str(e))
                            word_errors[w]=str(e)
                            continue

        if len(word_errors)>0:
            print("All is done but some errors occurred. Check error file : " + error_file)
            json.dump(word_errors,open(error_file, mode="w"))
        else:
            print("All is done. No errors")
            if os.path.isfile(error_file):
                os.remove(error_file)

    # retrieve just sentences from json files
    if task in ['all','get_sentences']:
        print("*"*10 + "retrieving sentences from json files, check outputdir : " + outputdir)
        log.info("retrieving sentences from json files"+ ", check outputdir : " + outputdir)
        for word in words:
            if isinstance(words, list):
                word = word.strip()
                inputfile = outputdir +solr_collection + '.'  +word+'.json'
                if os.path.isfile(inputfile):
                    print("retrieving sentences for : " + word + ' in file : ' + inputfile)        
                    results = json.load(open(inputfile))
                    res2 =[]

                    for doc in results:
                        doc2={}
                        doc2['date']= doc['published']
                        doc2['link']= doc['link']
                        doc2['sentences']= get_sentences_from_doc(word, doc['contents'][0])

                        log.info(str(len(doc2['sentences'])) + " sentence(s) in this doc")
                        res2.append(doc2)
                    try:
                        if len(res2)>0:
                            json.dump(res2, open(inputfile+'.sentences.json', mode='w'), indent=4)
                            print("Data stored in " +inputfile+'.sentences.json')
                            os.remove(inputfile)
                            #exit()
                        else:
                            print("Error with this word (no sentences retrieved) " + word + '(input file : ' + inputfile + ')')
                    except Exception as e:
                        print("error with this word : " + word + '. Error : ' + str(e))
                        continue

    # retrieve just sample sentences from json files
    if task in ['all','sample_sentences']:
        print("*"*10 + "Sample sentences from json files, check outputdir : " + outputdir)
        log.info("Sample sentences from json files"+ ", check outputdir : " + outputdir)

        files = glob('corpora/lemonde_1945_2020.*.json') 
        for fn in files:
            word = fn.split('.')[1]
            fn2 = fn+'.asp.txt'
                    # generate csv file (one sentence per line)
            with open(fn+'.csv', mode="w") as fncsv:
                fncsv.write("Text\tdate\tlink\n")
                print("parsing " + fn + "(word:" + word + ')')
                with open(fn) as fin:
                    data = json.load(fin)
                    for doc in data:
                        for s in doc['sentences']:
                            if re.search(word, s, flags=re.I) is not None:
                                fncsv.write(re.sub(r"\s+", " ",s)+"\t"+doc['date']+"\t"+doc['link'].strip()+"\n")
            res = read_csv_file_sample_sentences(fn+'.csv', timefield="date", sample=30)
            if res :
                os.unlink(fn)

######### main
if __name__ == '__main__':
    log_dir = './log/'
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



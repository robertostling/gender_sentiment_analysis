from pyabsa import available_checkpoints

# The results of available_checkpoints() depend on the PyABSA version
with open('checkpoint_map.json', mode="w") as fout:
    checkpoint_map = available_checkpoints(from_local=False)  # show available checkpoints of PyABSA of current version 
    fout.write(str(checkpoint_map))

#exit()
import pandas as pd
#from pyabsa.functional import ABSADatasetList
#from pyabsa.functional import ATEPCCheckpointManager
from pyabsa import AspectTermExtraction as ATEPC



def get_sentences(filepath):
    df = pd.read_csv(filepath, sep="\t")
    return df.Text.to_list()


examples = ['But the staff was so nice to us .',
            'But the staff was so horrible to us .',
            r'Not only was the food outstanding , but the little ` perks \' were great .',
            'It took half an hour to get our check , which was perfect since we could sit , have drinks and talk !',
            'It was pleasantly uncrowded , the service was delightful , the garden adorable , '
            'the food -LRB- from appetizers to entrees -RRB- was delectable .',
            'How pretentious and inappropriate for MJ Grill to claim that it provides power lunch and dinners !'
            ]
examples = get_sentences('./English_fiction_woman_forR.txt')
print(examples[0:5], len(examples))

aspect_extractor = ATEPC.AspectExtractor('multilingual',
                                         auto_device=True,  # False means load model on CPU
                                         cal_perplexity=True,
                                         )

inference_source = ATEPC.ATEPCDatasetList.SemEval
atepc_result = aspect_extractor.batch_predict(inference_source=examples, #inference_source,
                                              save_result=True,
                                              print_result=True,  # print the result
                                              pred_sentiment=True,  # Predict the sentiment of extracted aspect terms
                                              )

print(atepc_result)

#inference_source = ABSADatasetList.Restaurant14
#aspect_extractor = ATEPCCheckpointManager.get_aspect_extractor(checkpoint='multilingual')
#atepc_result = aspect_extractor.extract_aspect(inference_source=examples,
#                                               save_result=True,
#                                               print_result=True,  # print the result
#                                               pred_sentiment=True,  # Predict the sentiment of extracted aspect terms
#                                               )
#print(atepc_result)
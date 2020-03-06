import json


QA_json_path = '/mnt/data2/brd/textKVQA_Data/QA-scene.json'
KB_json_path = '/mnt/data2/brd/textKVQA_Data/KB-business.json'

with open(QA_json_path, 'r') as json_f:
    qa_dict = json.load(json_f)

with open(KB_json_path, 'r') as json_f:
    kb_dict = json.load(json_f)

print(len(qa_dict))
print(len(kb_dict))

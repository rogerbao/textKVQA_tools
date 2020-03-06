import json
import os
import os.path as osp
import editdistance
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


def get_ned(s1, s2):
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()
    ned = editdistance.eval(s1, s2) / max(len(s1), len(s2))
    return ned
    # iou = 1 - editdistance.eval(s1, s2) / max(len(s1), len(s2))
    # anls = iou if iou >= .5 else 0.
    # return anls


def split_carefully(text, splitter=',', delimiters=['"', "'"]):
    # assertion
    assert isinstance(splitter, str)
    assert not splitter in delimiters
    if not (isinstance(delimiters, list) or isinstance(delimiters, tuple)):
        delimiters = [delimiters]
    for cur_del in delimiters:
        assert len(cur_del) == 1

    cur_ind = 0
    prev_ind = 0
    splitted = []
    is_in_delimiters = False
    cur_del = None
    while cur_ind < len(text):
        if text[cur_ind] in delimiters:
            if text[cur_ind] == cur_del:
                is_in_delimiters = False
                cur_del = None
                cur_ind += 1
                continue
            elif not is_in_delimiters:
                is_in_delimiters = True
                cur_del = text[cur_ind]
                cur_ind += 1
                continue
        if not is_in_delimiters and text[cur_ind] ==  splitter:
            splitted.append(text[prev_ind:cur_ind])
            cur_ind += 1
            prev_ind = cur_ind
            continue
        cur_ind += 1
    splitted.append(text[prev_ind:cur_ind])
    return splitted


def sent_to_word_list(des_str):
    import string
    des_str = des_str.lower().replace('_', ' ').replace(',', ' ').replace('-', ' ')
    for c in string.punctuation:
        des_str = des_str.replace(c, '')
    return split_carefully(
        des_str.lower().replace('_', ' ').replace('.', '').replace(',', '').replace("\'", '').replace('-',
                                                                                                      '').replace(
            '\n', '').replace('\r', '').replace('\"', '').rstrip().replace("\\", '').replace('?', '').replace('/',
                                                                                                              '').replace(
            '#', '').replace('(', '').replace(')', '').replace(';', '').replace('!', '').replace('/', ''), ' ')


if __name__ == '__main__':
    txt_path = '/home/brd/projects/MM2020/deep-text-recognition-benchmark/ocr_result.txt'
    json_save_path = '/home/brd/projects/MM2020/deep-text-recognition-benchmark/OCR-scene.json'
    KB_path = '/mnt/data2/brd/textKVQA_Data/KB-business.json'

    with open(txt_path, 'r') as txt_f:
        lines = txt_f.readlines()

    with open(KB_path, 'r') as kb_f:
        json_KB = json.load(kb_f)

    json_dict = {}
    for line in lines:
        line = line.split(',')
        img_path = line[0]
        ocr_str = line[1]
        score = line[2]

        img_name = img_path.split('/')[-1]
        img_pure_name, _ = osp.splitext(img_name)

        if img_pure_name not in json_dict.keys():
            json_dict[img_pure_name] = {'ocr_str': [], 'ocr_ned': []}
            json_dict[img_pure_name]['ocr_str'].append(ocr_str)
        else:
            json_dict[img_pure_name]['ocr_str'].append(ocr_str)

        # print(img_pure_name)

    for key in json_dict:
        entity_id = key.split('_')[0]
        kb_entity_raw = json_KB[entity_id]['has title'].lower()
        # kb_entity_list = word_tokenize(kb_entity_raw)
        # kb_entity_list = kb_entity_raw.split()
        kb_entity_list = sent_to_word_list(kb_entity_raw)

        kb_entity_list = [w for w in kb_entity_list if w not in stopwords.words('english')]

        print(kb_entity_raw)
        print(kb_entity_list)
        print(json_dict[key]['ocr_str'])
        for ocr_word in json_dict[key]['ocr_str']:
            ned_value = 1
            for kb_entity in kb_entity_list:
                ned_value = min(get_ned(kb_entity, ocr_word), ned_value)
            json_dict[key]['ocr_ned'].append(ned_value)
        print(json_dict[key]['ocr_ned'])

    recall = 0.0
    recall_ned50 = 0.0
    for key in json_dict:
        if min(json_dict[key]['ocr_ned']) == 0:
            recall += 1
        if min(json_dict[key]['ocr_ned']) < 0.5:
            recall_ned50 += 1

    recall = recall/len(json_dict)
    recall_ned50 = recall_ned50/len(json_dict)

    print(recall, recall_ned50)

    # with open(json_save_path, 'w') as outfile:
    #     json.dump(json_dict, outfile)

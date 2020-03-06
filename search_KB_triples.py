import json
import os
import os.path as osp
import editdistance
from nltk.tokenize import word_tokenize
import pdb
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
    scene_json_save_path = '/home/brd/projects/MM2020/deep-text-recognition-benchmark/OCR-scene.json'
    KB_path = '/mnt/data2/brd/textKVQA_Data/KB-business.json'

    with open(scene_json_save_path, 'r') as ocr_f:
        json_dict = json.load(ocr_f)

    with open(KB_path, 'r') as kb_f:
        json_KB = json.load(kb_f)

    curr_ind = 0
    correct_num = 0
    for img_name in json_dict:
        curr_ind += 1
        if curr_ind % 100 == 0:
            print('processing {}/{}'.format(curr_ind, len(json_dict)))

        # json_dict[img_name]['retrieved'] = set()
        # json_dict[img_name]['min_ned_value'] = 1.0
        json_dict[img_name]['retrieved'] = []
        json_dict[img_name]['retrieved_ned_value'] = []
        entity_id_ocr = img_name.split('_')[0]
        ocr_word_list = json_dict[img_name]['ocr_str']
        ocr_word_list = [w for w in ocr_word_list if w not in stopwords.words('english')]

        kb_matching_results = dict()
        min_matching_score = 1.0
        for entity_id_kb in json_KB:
            kb_entity_raw = json_KB[entity_id_kb]['has title'].lower()
            kb_entity_list = sent_to_word_list(kb_entity_raw)
            kb_entity_list = [w for w in kb_entity_list if w not in stopwords.words('english')]
            curr_kb_word_matching_score = []

            for kb_entity_word in kb_entity_list:
                curr_ned_value = 1
                for ocr_word in ocr_word_list:
                    curr_ned_value = min(get_ned(kb_entity_word, ocr_word), curr_ned_value)
                curr_kb_word_matching_score.append(curr_ned_value)
            curr_kb_entity_matching_score = sum(curr_kb_word_matching_score) / len(curr_kb_word_matching_score)
            if min_matching_score > curr_kb_entity_matching_score:
                min_matching_score = curr_kb_entity_matching_score
                json_dict[img_name]['retrieved'] = entity_id_kb
                json_dict[img_name]['retrieved_ned_value'] = min_matching_score

        if json_dict[img_name]['retrieved'] == entity_id_ocr:
            correct_num += 1
        # if curr_ind == 500:
        #     break
    print(correct_num / len(json_dict))
    # print(correct_num / 500)

            # kb_matching_results[entity_id_kb] = sum(curr_kb_word_matching_score) / len(curr_kb_word_matching_score)

            # if min(curr_kb_word_matching_score) < 0.5:
            #     json_dict[img_name]['retrieved'].append(entity_id_kb)
            #     mean_score = sum(curr_kb_word_matching_score) / len(curr_kb_word_matching_score)
            #     json_dict[img_name]['retrieved_ned_value'].append([mean_score, curr_kb_word_matching_score])

        # kb_matching_results_sorted = sorted(kb_matching_results.items(), key=lambda d: d[1])
        # maxlen = min(10, len(kb_matching_results_sorted))
        # keys = [item[0] for item in kb_matching_results_sorted[:maxlen]]
        # values = [item[1] for item in kb_matching_results_sorted[:maxlen]]
        # json_dict[img_name]['retrieved'] = keys
        # json_dict[img_name]['retrieved_ned_value'] = values

    # correct_num = 0
    # for img_name in json_dict:
    #     entity_id_ocr = img_name.split('_')[0]
    #     if json_dict[img_name]['retrieved'] == entity_id_ocr:
    #         correct_num += 1
    # print(correct_num / len(json_dict))


        # for e_index in range(len(kb_matching_results['entity_id_kb'])):
        #     tmp_matching_score = kb_matching_results['matching_score'][e_index]


            # for ocr_word in ocr_word_list:
            #     ned_value = 1
            #     for kb_entity in kb_entity_list:
            #         ned_value = min(get_ned(kb_entity, ocr_word), ned_value)
            #     if ned_value < 0.5:
            #         # json_dict[img_name]['retrieved'].add(entity_id_kb)
            #         json_dict[img_name]['retrieved'].append(entity_id_kb)
            #         json_dict[img_name]['retrieved_ned_value'].append(ned_value)



        # print('img_name: ', img_name)
        # print('ocr_str: ', json_dict[img_name]['ocr_str'])
        # print('ocr_word_list: ', ocr_word_list)
        # print('retrieved entity: ', json_dict[img_name]['retrieved'])
        # print('retrieved entity ned value: ', json_dict[img_name]['retrieved_ned_value'])
        # print('retrieved entity title: ')
        # for retrieved_entity_id in json_dict[img_name]['retrieved']:
        #     print(json_KB[retrieved_entity_id]['has title'].lower())
        # pdb.set_trace()

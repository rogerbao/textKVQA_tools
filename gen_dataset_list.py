import os
import os.path as osp
import json
import glob

img_root = '/mnt/data2/brd/textKVQA_Data/text-KVQA-scene/images/'
json_path = '/mnt/data2/brd/textKVQA_Data/QA-scene.json'


img_list = glob.glob(img_root + '*/*')
image_path_list = []
with open('/mnt/data2/brd/textKVQA_Data/text-KVQA-scene/scene_list.txt', 'w') as f:
    for img_path in img_list:
        sub_folder = img_path.split('/')[-2]
        img_name = img_path.split('/')[-1]
        _, ext = os.path.splitext(img_name)
        ext = ext.lower()
        if ext == '.jpg' or ext == '.jpeg' or ext == '.png':
            sub_path = osp.join(sub_folder, img_name)
            image_path_list.append(sub_path)
            f.write('{}\n'.format(sub_path))
print(len(image_path_list))

'''
with open(json_path, 'r') as json_f:
    json_dict = json.load(json_f)
    
img_list = []
missing_cnt = 0
for ind, item in enumerate(json_dict.items()):
    # print(ind, item)
    img_id = item[0]
    entity_id = img_id.split('_')[0]

    img_info = item[1]
    img_list.append(img_info['Image_File'])

    img_path = osp.join(img_root, entity_id, img_info['Image_File'])
    if not osp.exists(img_path):
        img_path = img_path.replace('.jpg', '.jpeg')
        if not osp.exists(img_path):
            img_path = img_path.replace('.jpeg', '.png')
            if not osp.exists(img_path):
                print(img_path)
                missing_cnt += 1

print(len(img_list))
print(missing_cnt)
'''


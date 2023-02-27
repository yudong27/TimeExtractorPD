#encoding:utf-8
import os
import sys
resposity = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

if sys.path[0] != resposity:
    sys.path.insert(0, resposity)
from urllib import parse
from pymongo import MongoClient

def get_id():
    mongo_uri = 'mongodb://{}:{}@172.17.0.1:27018'.format("admin", parse.quote_plus("gz123@people!@#"))
    mongo = MongoClient(host=mongo_uri, connect=False).leader
    if mongo.ids.count_documents({}) == 0:
        mongo.ids.insert_one({"id": 1})
    res = mongo.ids.find_one_and_update({},{'$inc':{'id':1}})
    return res['id']
gnum = get_id()
print('ggggggggggggggggggggg',gnum)
os.environ["CUDA_VISIBLE_DEVICES"] = str(gnum%4)

import torch
from models.modeling_multitask import GlyceBertForMultiTask
from torch.nn import functional as F
from csc_with_ner import *
from flask import Flask,request


model = GlyceBertForMultiTask.from_pretrained(ckpt_path)
print(model.device, torch.cuda.is_available())
model.to(device)

stop_marks = '。？！：，；……\?!:;,.'

def correct_sentence(texts: List[str], prediction_prob_threshold = 0.9):
    # 异常检测结果，每种异常对应一个列表，列表里是异常实例的index
    exception_case = {'inconsistent_tokenize_len': [], 'inconsistent_str_len': []}
    # 过滤非中文字符过多的句子
    filter_texts, texts = filter_non_chinese_sent(texts)

    if texts != []:
        # 预处理
        sub_pos, texts = preprocess(texts)

        # ner模型预测
        ner_result = nerservice.predict_for_csc(texts)
        is_entity= ner_result['is_entity']
        # csc数据准备
        encoded_batch = chinesebertdataset.tokenizer.encode_batch(texts)
        # 记录unk的token的offset
        unk_token_batch = [[(offset[0], text[offset[0]:offset[1]]) for (token, offset) in zip(encoded.tokens, encoded.offsets) if token == '[UNK]'] for (text, encoded) in zip(texts, encoded_batch)]
        pinyin_ids = [chinesebertdataset.convert_sentence_to_pinyin_ids(text, encoded) for (text, encoded) in zip(texts, encoded_batch)]
        input_ids = torch.LongTensor([encoded.ids for encoded in encoded_batch]).to(device)
        pinyin_ids = torch.LongTensor(pinyin_ids).view(-1).to(device)
        is_single_str = torch.BoolTensor([[True if len(token) == 1 else False for token in encoded.tokens] for encoded in encoded_batch]).to(device)
        token_list = [[token for token in encoded.tokens] for encoded in encoded_batch]
        mask = (input_ids != 0) * (input_ids != 101) * (input_ids != 102).long()
        batch_size, length = input_ids.shape
        pinyin_ids = pinyin_ids.view(batch_size, length, 8)
        attention_mask = (input_ids != 0).long()

        # csc模型预测
        logits = model(
                input_ids,
                pinyin_ids,
                attention_mask=attention_mask,
                ).logits
        predict_scores = F.softmax(logits, dim=-1)
        predict_labels = torch.argmax(predict_scores, dim=-1) * mask

        # 过滤token长度大于1的纠错
        predict_labels = torch.where(is_single_str, predict_labels, input_ids)
        # print(predict_labels[0])

        # 设置预测概率阈值，降低误检率
        predict_labels = torch.where(torch.max(predict_scores, dim=-1)[0] > prediction_prob_threshold, predict_labels, input_ids)

        # 异常处理
        # 异常一：ner，csc模型的tokenize后的token长度不一致
        if (ner_result['tokenizer_result']['attention_mask'] != attention_mask).sum() == 0:
            predict_labels = torch.where(is_entity, input_ids, predict_labels)
        else:
            not_equal_tokenize_len = torch.nonzero((ner_result['tokenizer_result']['attention_mask'] != attention_mask).sum(axis=1)).reshape(-1).tolist()
            exception_case['inconsistent_tokenize_len'] = not_equal_tokenize_len
        
        # csc解码
        decoded_results = [decode_sentence(predict_result, unk_token, _token_list, pos_dict_list, origin_sent) for predict_result, unk_token, _token_list, pos_dict_list, origin_sent in zip(predict_labels.tolist(), unk_token_batch, token_list, sub_pos, texts)]
        sents = [r[0] for r in decoded_results]

        sents_without_postprocess = [r[1] for r in decoded_results]
        # print(sents[0], sents_without_postprocess[0])

        # 异常二：csc纠错后str长度不一样
        origin_len = torch.tensor([len(text) for text in texts])
        corrected_len = torch.tensor([len(sent) for sent in sents_without_postprocess])
        not_equal_str_len = torch.nonzero(origin_len != corrected_len).reshape(-1).tolist()
        exception_case['inconsistent_str_len'] = not_equal_str_len
    else:
        sents = []

    # 还原未经修改的句子
    sents = recover_non_chinese_sent(filter_texts, sents)

    return sents, exception_case

def cut_sent(sentence):  
    #获取定位词所在的句子
    #返回新的起始位置start, 子句sent
    for s in stop_marks:
        sentence = sentence.replace(s, '#')
    sent_list = sentence.split('#')
    return sent_list

def check(text):
    status = 'GOOD'
    res = []
    text_list = cut_sent(text)
    corrected_text_list, _exception = correct_sentence(text_list)
   
    corrected_text = '#'.join(corrected_text_list)
    for error_type in _exception: #出现异常时，无法对应offset，放弃修改
        if _exception[error_type]:
            status = 'Exception'

    if status != 'GOOD': # 异常处理，输出原句
        print('Exception')
        return {}
    else:
        for i, c in enumerate(corrected_text):
            if c != text[i] and text[i] not in stop_marks:
                res.append({"offset":i, "length":1, "reference":c})
    if res:
        return {"type":8, "hitinfos":res }   
    else:
        return {}    


app = Flask(__name__)

@app.route('/spell_check')
def spell_check():
    json_data = request.json
    sentence = json_data['sentence']
    try:
        all_res = check(sentence)    
    except:
        all_res = {}    
    torch.cuda.empty_cache()
    return all_res

if __name__=='__main__':
    port_num = sys.argv[1]
    app.run(host='0.0.0.0', port=int(port_num), debug=True)
    # text = '我爱背京天安门。'
    # print(check(text))
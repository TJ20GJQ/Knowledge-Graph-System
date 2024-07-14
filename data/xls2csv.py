import requests
import xlrd
import pandas as pd
import re
import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
from tqdm import tqdm
import yaml
import numpy as np
import math

# 定义API接口
KDXF_url = "http://ltpapi.xfyun.cn/v1/ke"  # 科大讯飞接口地址
KDXF_x_appid = "4eb243ef"  # 开放平台应用ID
KDXF_api_key = "56995734d5bf4a239c7c4ac6298440bf"  # 开放平台应用接口秘钥
texsmart_mt_url = "https://texsmart.qq.com/api/match_text"
baiduNLP_API_KEY = "xdk4PoFmZeajVSOzkMOLXGk2"
baiduNLP_SECRET_KEY = "E88KL0T2gfXA6GjH3mKnQXqRllEucCQp"
baiduQF_API_KEY = "P0YJizGzqgaSkgiepLauh6Yi"
baiduQF_SECRET_KEY = "EVsoLSVTH9wEalN93U63FCLFUfaHvS74"


def get_access_token(api_key, secret_key):
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials",
              "client_id": api_key, "client_secret": secret_key}
    return str(requests.post(url, params=params).json().get("access_token"))


baiduNLP_we_url = "https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_vec?charset=UTF-8&access_token=" + \
    get_access_token(baiduNLP_API_KEY, baiduNLP_SECRET_KEY)
we_dem = 1024
baiduBGE_we_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/bge_large_zh?access_token=" + \
    get_access_token(baiduQF_API_KEY, baiduQF_SECRET_KEY)


# 工具函数
def TexSmartSimText(text, topic, alg="esim"):
    if isinstance(topic, str):
        obj = {
            "text_pair_list": [{"str1": f"{text}", "str2": f"{topic}"}],
            "options": {"alg": alg},
            "echo_data": {"id": 123}
        }
    elif isinstance(topic, list):
        pair_list = [{"str1": f"{text}", "str2": f"{t}"} for t in topic]
        obj = {
            "text_pair_list": pair_list,
            "options": {"alg": alg},
            "echo_data": {"id": 123}
        }

    reg_str = json.dumps(obj).encode()

    res = requests.post(texsmart_mt_url, data=reg_str).json()
    ret_code = res["header"]["ret_code"]
    while ret_code != "succ":
        res = requests.post(texsmart_mt_url, data=reg_str).json()
        ret_code = res["header"]["ret_code"]

    return [s['score'] for s in res['res_list']]


def KDXFKeywordExtract(TEXT):
    body = urllib.parse.urlencode({'text': TEXT}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(
        param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(KDXF_api_key.encode(
        'utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': KDXF_x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    while True:  # 防止请求失败
        try:
            req = urllib.request.Request(KDXF_url, body, x_header)
            result = urllib.request.urlopen(req)
            break
        except:
            pass
    result = result.read()
    try:
        # print(json.loads(result.decode('utf-8'))['data']['ke'])
        result = json.loads(result.decode('utf-8'))['data']['ke']
        return result
    except:
        return '无'


def baiduNLPWordEmbedding(TEXT):  # 有可能返回失败
    payload = json.dumps({'word': TEXT, 'dem': we_dem})
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    while True:
        response = requests.request(
            "POST", baiduNLP_we_url, headers=headers, data=payload)
        time.sleep(0.2)
        if 'error_code' in json.loads(response.text):
            # 并发限制/服务不可用
            if json.loads(response.text)['error_code'] == 18 or json.loads(response.text)['error_code'] == 2:
                continue
        break
    return json.loads(response.text)


def baiduBGEWordEmbedding(TEXT):
    payload = json.dumps({"input": [TEXT]})
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    while True:
        response = requests.request(
            "POST", baiduBGE_we_url, headers=headers, data=payload)
        time.sleep(0.2)
        if 'error_code' in json.loads(response.text):
            print(json.loads(response.text)['error_code'])
            continue
        break
    return json.loads(response.text)['data'][0]['embedding']


def computeCosSim(vec1, vec2):  # 计算余弦相似度
    return np.sum(np.array(vec1) * np.array(vec2)) / (np.linalg.norm(np.array(vec1)) * np.linalg.norm(np.array(vec2)))


def minmax(scores):  # 由于相似度数值较大，在每个关键词对应进行min-max归一化(不包括0)
    for kw in scores:
        index0 = []
        temp = []
        for si, s in enumerate(scores[kw]):
            if s:
                temp.append(s)
            else:
                index0.append(si)
        temp = np.array(temp)
        temp_max = temp.max()
        temp_min = temp.min()
        for ti in range(len(temp)):
            temp[ti] = (temp[ti]-temp_min)/(temp_max-temp_min)
        temp = list(temp)
        for id in index0:
            temp.insert(id, 0)
        scores[kw] = temp
    return scores


def keywordMatchA(data, keywords):  # 方案一：Texsmart文本匹配-项目简介与自定义关键词直接匹配得分
    scores = {}
    for kw in keywords:
        scores[kw] = []
    for i in tqdm(range(len(data))):
        score = TexSmartSimText(data.loc[i, '项目简介'], keywords)
        for k in range(len(keywords)):
            scores[keywords[k]].append(score[k])
    return scores


# 方案二：关键词提取+embedding+向量中心化+计算相似度得分(关键词不能是组合词，如人工智能)!!可改进embedding为大模型
def keywordMatchB(data, keywords):
    target_vec = {}
    scores = {}
    for kw in keywords:
        # WEres = baiduNLPWordEmbedding(kw)
        WEres = baiduBGEWordEmbedding(kw)  # 改进
        if 'error_code' not in WEres:  # error表示库中没有收录某个词语
            # target_vec[kw] = WEres['vec']
            target_vec[kw] = WEres  # 改进
            scores[kw] = []
        else:
            print(kw, WEres)
    print('关键词：', list(target_vec.keys()))

    for i in tqdm(range(len(data))):
        # 科大讯飞关键词提取
        if data.loc[i, '项目简介'] != '无':
            res = KDXFKeywordExtract(data.loc[i, '项目简介'])
        else:
            res = '无'
        if res != '无':
            res_score = []
            res_keyword = []
            for kw in res:  # 获得得分和关键词
                try:
                    res_score.append(float(kw['score']))
                except:
                    res_score.append(float(kw['final']))
                res_keyword.append(kw['word'])

            # 百度中文词向量
            res_vec = []
            for ki in reversed(range(len(res_keyword))):
                # WEres = baiduNLPWordEmbedding(res_keyword[ki])
                WEres = baiduBGEWordEmbedding(res_keyword[ki])  # 改进
                if 'error_code' in WEres:  # error表示库中没有收录某个词语
                    res_score.pop(ki)
                    print(res_keyword[ki], WEres)
                else:
                    # res_vec.append(WEres['vec'])
                    res_vec.append(WEres)  # 改进

            # 中心化
            scoreSum = sum(res_score)
            res_weight = [s/scoreSum for s in res_score]  # 根据置信度归一化设置权重
            centerVec = sum(
                list(map(lambda x, y: x*np.array(y), res_weight, res_vec)))

            # 与目标词向量计算相似度[-1,1]
            for kw in target_vec:
                scores[kw].append(computeCosSim(target_vec[kw], centerVec))
        else:
            for kw in target_vec:
                scores[kw].append(0)
    scores = minmax(scores)  # 改进
    return scores


def keywordMatchC(data, keywords):  # 方案三：关键词提取+文本（词语）匹配得分+加权计算相似度
    scores = {}
    for kw in keywords:
        scores[kw] = []
    for i in tqdm(range(len(data))):
        # 科大讯飞关键词提取
        if data.loc[i, '项目简介'] != '无':
            res = KDXFKeywordExtract(data.loc[i, '项目简介'])
        else:
            res = '无'
        if res != '无':
            res_score = []
            res_keyword = []
            for kw in res:  # 获得得分和关键词
                try:
                    res_score.append(float(kw['score']))
                except:
                    res_score.append(float(kw['final']))
                res_keyword.append(kw['word'])

            # 计算权重加权求和
            threshhold = 1e-3  # 判断两词是否属于关联的阈值
            sim_score2d = []
            sim_bool2d = []
            for ki, kw in enumerate(res_keyword):
                sim = TexSmartSimText(kw, keywords, alg='linkage')
                sim_score2d.append(sim)
                sim_bool = list(map(lambda x: x > threshhold, sim))
                sim_bool2d.append(sim_bool)

            sim_score2d = np.array(sim_score2d)  # shape：提取关键词*目标关键词
            sim_bool2d = np.array(sim_bool2d)
            sim_num = np.sum(sim_bool2d, 0)  # 与每个目标关键词相似个数，越多越重要
            sim_num_sqrt = np.array([math.sqrt(s) for s in sim_num])

            # 计算注意力，改变权重，关键词得分越高越重要，与目标关键词越关联越重要
            for ki in range(len(res_keyword)):
                sim_sum = np.dot(sim_score2d[ki], sim_num_sqrt)
                res_score[ki] = res_score[ki] * sim_sum

            score_sum = sum(res_score)
            if score_sum < 1e-5:  # 如果没有匹配的关键词，score_sum将为0
                for kw in keywords:
                    scores[kw].append(0)
                continue

            res_weight = [s/score_sum for s in res_score]  # 归一化设置权重

            sim_score = [0]*len(keywords)
            for ki in range(len((res_keyword))):
                for ti in range(len(keywords)):
                    sim_score[ti] += sim_score2d[ki][ti]*res_weight[ki]

            for ki, kw in enumerate(keywords):
                scores[kw].append(sim_score[ki])
        else:
            for kw in keywords:
                scores[kw].append(0)
    return scores


def keywordMatchD(data, keywords):  # 方案四：整个句子embedding+目标关键词embedding+计算余弦相似度
    target_vec = {}
    scores = {}
    for kw in keywords:
        WEres = baiduBGEWordEmbedding(kw)
        if 'error_code' not in WEres:  # error表示库中没有收录某个词语
            target_vec[kw] = WEres
            scores[kw] = []
        else:
            print(kw, WEres)
    print('关键词：', list(target_vec.keys()))

    for i in tqdm(range(len(data))):
        if data.loc[i, '项目简介'] != '无':
            WEres = baiduBGEWordEmbedding(data.loc[i, '项目简介'])  # 句子embedding
            if 'error_code' in WEres:
                for kw in target_vec:
                    scores[kw].append(0)

            # 与目标词向量计算相似度[-1,1]
            for kw in target_vec:
                scores[kw].append(computeCosSim(target_vec[kw], WEres))
        else:
            for kw in target_vec:
                scores[kw].append(0)
    scores = minmax(scores)

    return scores


def xls2csv(filename, newFilename, save=True):
    data_xls = xlrd.open_workbook(filename)
    table = data_xls.sheets()[0]
    csv_columns = ['批次', '所属学院', '项目编号', '项目名称', '项目类型', '项目负责人姓名', '负责人学号', '负责人手机', '负责人邮箱',
                   '参与学生人数', '项目其他成员信息', '指导教师姓名', '教师工号', '教师职称', '教师所属学院', '项目总经费(元)',
                   '财政拨款/企业资助(元)', '学校拨款(元)', '项目所属一级学科', '项目所属二级学科', '项目所属专业类代码', '中期状态',
                   '结题状态', '延期状态', '终止状态', '是否终止项目', '项目简介']
    data_csv = {}
    for i in range(len(csv_columns)):
        data_csv[csv_columns[i]] = table.col_values(i+1, start_rowx=5)

    data_csv = pd.DataFrame(data_csv)

    # 设置数据类型
    data_csv['负责人学号'] = data_csv['负责人学号'].astype(str)
    data_csv['负责人手机'] = data_csv['负责人手机'].astype(str)
    data_csv['教师工号'] = data_csv['教师工号'].astype(str)
    data_csv['项目所属专业类代码'] = data_csv['项目所属专业类代码'].astype(str)
    # 补充年份信息
    year = []
    for i in range(len(data_csv)):
        year.append(re.findall(r"\d+", data_csv.loc[i, '批次'])[0])
    data_csv.insert(loc=0, column='年份', value=year)
    # 补充缺失项目编号
    fail_proj = data_csv['项目编号'] == ''
    fail_num = 0
    for i in reversed(range(len(data_csv))):
        if fail_proj.loc[i]:
            data_csv.loc[i, '项目编号'] = 'F' + \
                data_csv.loc[i, '年份'] + str(fail_num+1).zfill(3)
            fail_num += 1
    # 补充项目级别信息
    level = []
    for i in range(len(data_csv)):
        if data_csv.loc[i, '项目编号'][0] == 'X':
            level.append('校级')
        elif data_csv.loc[i, '项目编号'][0] == 'S':
            level.append('市级')
        elif data_csv.loc[i, '项目编号'][0] == 'F':
            level.append('未获批')
        elif '0' <= data_csv.loc[i, '项目编号'][0] <= '9':
            level.append('国家级')
    data_csv.insert(loc=2, column='级别', value=level)
    # 修正项目简介，去除<>，处理&nbsp;、换行
    for i in range(len(data_csv)):
        data_csv.loc[i, '项目简介'] = data_csv.loc[i,
                                               '项目简介'].replace('&nbsp;', ' ')
        data_csv.loc[i, '项目简介'] = re.sub(
            r'<[^>]*>', '', data_csv.loc[i, '项目简介'])
        data_csv.loc[i, '项目简介'] = data_csv.loc[i, '项目简介'].replace('\n', ' ')
        data_csv.loc[i, '项目简介'] = data_csv.loc[i, '项目简介'].strip()  # 去除前后空格
        data_csv.loc[i, '项目简介'] = data_csv.loc[i,
                                               '项目简介'].replace(chr(65279), '')  # 65279代表某个特殊字符，不显示
    # 填充空值
    data_csv['财政拨款/企业资助(元)'] = data_csv['财政拨款/企业资助(元)'].replace('', 0)
    data_csv['学校拨款(元)'] = data_csv['学校拨款(元)'].replace('', 0)
    data_csv = data_csv.replace('', '无')

    # 进阶预处理：预置关键词匹配
    with open("./data.yaml", "r", encoding="utf-8") as f:
        myTopics = yaml.safe_load(f)['myKeyword']
    scores = keywordMatchA(data_csv, myTopics)
    # scores = keywordMatchB(data_csv, myTopics)
    # scores = keywordMatchC(data_csv, myTopics)
    # scores = keywordMatchD(data_csv, myTopics)
    for kw in scores:
        data_csv[kw] = scores[kw]

    if save:
        data_csv.to_csv(newFilename, index=False, sep=',')

    return data_csv


emb_num = 1024


def csvEmbedding(filename, newFilename):
    data = pd.read_csv(filename, sep=',')
    print("embedding...")

    emb = []
    for i in tqdm(range(len(data))):
        emb.append(baiduBGEWordEmbedding(data.loc[i, "项目简介"]))

    # emb = np.array(emb)
    # emb_data = pd.DataFrame(emb)
    # emb_data.columns = ["d"+str(i+1) for i in range(emb_num)]
    # data = pd.concat([data, emb_data], axis=1)
    data["项目简介向量表示"] = emb

    data.to_csv(newFilename, index=False, sep=',')


if __name__ == '__main__':
    # data2022 = xls2csv('2022年项目立项信息表.xls', '2022.csv')
    # data2023 = xls2csv('2023年项目立项信息表.xls', '2023.csv')

    # 调试用
    # data2022 = pd.read_csv('2022.csv')
    # data2023 = pd.read_csv('2023.csv')

    # data = pd.concat([data2022, data2023])
    # data.to_csv('project_data.csv', index=False, sep='|')

    # 测试相似度
    # data2022 = pd.read_csv('2022.csv')
    # vec1 = baiduBGEWordEmbedding(
    #     "本项目是基于负责人的第五届创新体验竞赛主题一的国赛作品来开展的，对作品中的30个的创新萌芽想法进行更深入的提炼和修改。目的是对这30个创新萌芽想法的价值和可行性进行深入分析，提炼出其中值得深入考究的想法并将其系统性地修改。")
    # sims = []
    # for i in tqdm(range(len(data2022))):
    #     str2 = data2022.loc[i, '项目简介']
    #     vec2 = baiduBGEWordEmbedding(str2)
    #     sim = computeCosSim(vec1, vec2)
    #     sims.append(sim)
    #     time.sleep(0.2)
    # data2022['相似'] = sims
    # data2022.to_csv('new.csv', index=False, sep=',')
    # data2022 = pd.read_csv('new.csv')
    # data2022.sort_values("相似", inplace=True, ascending=False)
    # print(data2022.head(10)['项目简介'])

    # 加入项目简介embedding
    # csvEmbedding("2022.csv", "2022_emb.csv")
    # csvEmbedding("2023.csv", "2023_emb.csv")

    # data2022 = pd.read_csv('2022_emb.csv')
    # data2023 = pd.read_csv('2023_emb.csv')
    # data = pd.concat([data2022, data2023])
    # data.to_csv('project_emb_data.csv', index=False, sep='|')

    # *****************github demo*********************
    data2022 = xls2csv('./test/2022年项目立项信息表_test.xls', './test/2022_test.csv')
    data2023 = xls2csv('./test/2023年项目立项信息表_test.xls', './test/2023_test.csv')

    data = pd.concat([data2022, data2023])
    data.to_csv('./test/project_data_test.csv', index=False, sep='|')

    # 加入项目简介embedding
    csvEmbedding("./test/2022_test.csv", "./test/2022_emb_test.csv")
    csvEmbedding("./test/2023_test.csv", "./test/2023_emb_test.csv")

    data2022 = pd.read_csv('./test/2022_emb_test.csv')
    data2023 = pd.read_csv('./test/2023_emb_test.csv')
    data = pd.concat([data2022, data2023])
    data.to_csv('./test/project_emb_data_test.csv', index=False, sep='|')

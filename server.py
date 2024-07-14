from flask import Flask
from flask_cors import cross_origin
from datetime import datetime, timedelta
import time
import requests
import json
import random
from flask import request
import pandas as pd
import numpy as np
from query_projectgraph import QueryProjectGraph

app = Flask(__name__, static_url_path='/s',
            static_folder='static', template_folder='templates')

qpg = QueryProjectGraph()


@app.route('/queryInfo', methods=['GET'])
@cross_origin()
def queryInfo():
    return {'node_count': qpg.node_count, 'presetKeywords': qpg.presetKeywords,
            'searchCondition': {'教师所属学院': qpg.college_entity,
                                '项目年份': qpg.year_entity,
                                '项目级别': qpg.level_entity,
                                '项目类型': qpg.type_entity,
                                '项目所属学院': qpg.college_entity,
                                '项目一级学科': qpg.discipline1_entity,
                                '项目二级学科': qpg.discipline2_entity,
                                }}


@app.route('/queryNodeOnly', methods=['POST'])
@cross_origin()
def queryNode():
    return qpg.querySubgraphByDistance(request.json.get('type'), request.json.get('id'), k=1)


@app.route('/queryNodeByType', methods=['POST'])
@cross_origin()
def queryNodeByType():
    return qpg.queryNodeByType(request.json.get('type'))


@app.route('/queryNodeByKeywords', methods=['POST'])
@cross_origin()
def queryNodeByKeywords():
    return qpg.queryNodeByKeywords(request.json.get('keywords'), searchRange=request.json.get('range'), condition=request.json.get('condition'))


@app.route('/queryProjectByKeywordSim', methods=['POST'])
@cross_origin()
def queryProjectByKeywordSim():
    return qpg.queryProjectByKeywordSim(request.json.get('keyword'), request.json.get('threshhold'))


@app.route('/querySimilarProject', methods=['POST'])
@cross_origin()
def querySimilarProject():
    return qpg.querySimilarProject(request.json.get('id'), request.json.get('threshhold'))


@app.route('/editNode', methods=['POST'])
@cross_origin()
def editNode():
    return qpg.editNode(request.json.get('id'), request.json.get('properties'))


@app.route('/queryStatisticsMenu', methods=['GET'])
@cross_origin()
def queryStatisticsMenu():
    return qpg.queryStatisticsMenu()


@app.route('/queryStatistics', methods=['POST'])
@cross_origin()
def queryStatistics():
    if request.json.get('title') == '各学院情况饼图统计':
        res = qpg.queryCollegePieByYear(
            target=request.json.get('查询目标'),
            year=request.json.get('年份'),
            level=request.json.get('级别'),
            union_threshhold=request.json.get('其余阈值（%）')/100,
            show_plot=False, save_plot=False, rdict=True)
    elif request.json.get('title') == '历年各级别类型项目数量':
        res = qpg.queryProjectBarOfYear(
            target=request.json.get('查询目标'),
            show_plot=False, save_plot=False, rdict=True)
    elif request.json.get('title') == '历年项目参与度折线图统计':
        res = qpg.queryNumLineOfYear(
            targets=request.json.get('查询目标'),
            college=request.json.get('学院'),
            show_plot=False, save_plot=False, rdict=True)
    elif request.json.get('title') == '各级别项目成员组成':
        res = qpg.queryMemberBarOfLevel(
            target=request.json.get('查询目标'),
            show_plot=False, save_plot=False, rdict=True)
    elif request.json.get('title') == '项目各领域分布饼图统计':
        res = qpg.queryProjectPieByCollege(
            target=request.json.get('查询目标'),
            college=request.json.get('学院'),
            threshhold=request.json.get('阈值'),
            union_threshhold=request.json.get('其余阈值（%）')/100,
            show_plot=False, save_plot=False, rdict=True)
    elif request.json.get('title') == '历年参与学生年级统计':
        res = qpg.queryGradeBarByYear(
            year=request.json.get('年份'),
            show_plot=False, save_plot=False, rdict=True)
    elif request.json.get('title') == '各学院最受欢迎教师排行榜':
        res = qpg.queryPopularTeacherBarByCollege(
            year=request.json.get('年份'),
            college=request.json.get('学院'),
            rule=request.json.get('评判依据'),
            topk=request.json.get('TopN'),
            show_plot=False, save_plot=False, rdict=True)
    return res  # 需要返回数据，v-html不能处理js


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

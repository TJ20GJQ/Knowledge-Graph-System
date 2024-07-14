from tqdm import tqdm
from py2neo import Graph, Node, Relationship
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import random
import yaml
import numpy as np


class QueryProjectGraph:
    def __init__(self):
        self.__graph = Graph("http://localhost:7474",
                             auth=("neo4j", "GJQ1030n4j"))
        self.node_count = {}
        self.rel_count = {}
        self.countNode()
        self.countRel()
        with open("./data/data.yaml", "r", encoding="utf-8") as f:
            self.presetKeywords = yaml.safe_load(f)['myKeyword']
        with open("./entity_data/year.txt", "r") as f:
            self.year_entity = f.read().split('\n')
            self.year_entity.reverse()
        with open("./entity_data/level.txt", "r") as f:
            self.level_entity = f.read().split('\n')
            self.level_entity.reverse()
        with open("./entity_data/type.txt", "r") as f:
            self.type_entity = f.read().split('\n')
            self.type_entity.reverse()
        with open("./entity_data/college.txt", "r") as f:
            self.college_entity = f.read().split('\n')
            self.college_entity.reverse()
        with open("./entity_data/discipline1.txt", "r") as f:
            self.discipline1_entity = f.read().split('\n')
            self.discipline1_entity.reverse()
        with open("./entity_data/discipline2.txt", "r") as f:
            self.discipline2_entity = f.read().split('\n')
            self.discipline2_entity.reverse()

    def __query(self, query):
        try:
            return self.__graph.run(query)  # 执行语句
        except Exception as e:
            print(e)

    def countNode(self):
        query = '''MATCH (n)
        RETURN labels(n) AS labels, COUNT(*) AS count
        ORDER BY count DESC'''
        result = self.__query(query)
        if result is not None:
            for record in result:
                self.node_count[record["labels"][0]] = record["count"]
                # print(record["labels"][0], record["count"])
        else:
            print('Query Operation Error.')

    def countRel(self):
        query = '''MATCH ()-[r]->()
        RETURN type(r) AS relationshipType, COUNT(*) AS count
        ORDER BY count DESC'''
        result = self.__query(query)
        if result is not None:
            for record in result:
                self.rel_count[record["relationshipType"]] = record["count"]
                # print(record["relationshipType"], record["count"])
        else:
            print('Query Operation Error.')

    """ 统计分析模块 函数"""

    def queryStatisticsMenu(self):
        return [{'title': '各学院情况饼图统计',
                 'option': [
                     {
                         'type': 'select',
                         'label': '查询目标',
                         'value': ['经费', '项目数量', '老师数量', '跨学院项目数量'],
                         'default': ''
                     },
                     {
                         'type': 'select',
                         'label': '年份',
                         'value': ['全部']+self.year_entity,
                         'default': '全部'
                     },
                     {
                         'condition': {
                             'label': '查询目标',
                             'value': '项目数量'
                         },
                         'type': 'select',
                         'label': '级别',
                         'value': ['全部']+self.level_entity,
                         'default': '全部'
                     },
                     {
                         'type': 'number',
                         'label': '其余阈值（%）',
                         'min': 0,
                         'max': 10,
                         'step': 0.1,
                         'default': 1.5
                     }
                 ]},
                {'title': '历年各级别类型项目数量',
                 'option': [
                     {
                         'type': 'select',
                         'label': '查询目标',
                         'value': ['级别', '类型'],
                         'default': '级别'
                     }
                 ]},
                {'title': '历年项目参与度折线图统计',
                 'option': [
                     {
                         'type': 'multiSelect',
                         'label': '查询目标',
                         'value': ['学生', '老师', '项目'],
                         'default': []
                     },
                     {
                         'type': 'select',
                         'label': '学院',
                         'value': ['全部']+self.college_entity,
                         'default': '全部'
                     },
                 ]},
                {'title': '各级别项目成员组成',
                 'option': [
                     {
                         'type': 'select',
                         'label': '查询目标',
                         'value': ['成员人数', '指导教师人数'],
                         'default': '成员人数'
                     }
                 ]},
                {'title': '项目各领域分布饼图统计',
                 'option': [
                     {
                         'type': 'select',
                         'label': '查询目标',
                         'value': ['关键词', '一级学科', '二级学科'],
                         'default': '关键词'
                     },
                     {
                         'type': 'select',
                         'label': '学院',
                         'value': ['全部']+self.college_entity,
                         'default': '全部'
                     },
                     {
                         'condition': {
                             'label': '查询目标',
                             'value': '关键词'
                         },
                         'type': 'number',
                         'label': '阈值',
                         'min': 0,
                         'max': 1,
                         'step': 0.1,
                         'default': 0.5
                     },
                     {
                         'type': 'number',
                         'label': '其余阈值（%）',
                         'min': 0,
                         'max': 10,
                         'step': 0.1,
                         'default': 1.5
                     }
                 ]},
                {'title': '历年参与学生年级统计',
                 'option': [
                     {
                         'type': 'select',
                         'label': '年份',
                         'value': ['全部']+self.year_entity,
                         'default': '全部'
                     }
                 ]},
                {'title': '各学院最受欢迎教师排行榜',
                 'option': [
                     {
                         'type': 'select',
                         'label': '年份',
                         'value': ['全部']+self.year_entity,
                         'default': '全部'
                     },
                     {
                         'type': 'select',
                         'label': '学院',
                         'value': ['全部']+self.college_entity,
                         'default': '全部'
                     },
                     {
                         'type': 'select',
                         'label': '评判依据',
                         'value': ['指导项目等级', '指导项目数量', '指导学生人数'],
                         'default': '指导项目等级'
                     },
                     {
                         'type': 'number',
                         'label': 'TopN',
                         'min': 1,
                         'max': 15,
                         'step': 1,
                         'default': 5
                     }
                 ]}]

    def __pie_process(self, df, proc, label, threshhold=0.015):
        labels_copy = list(df[label].values).copy()
        targets_copy = list(df[proc].values).copy()
        df_temp = pd.DataFrame()
        for i, (l, t) in reversed(list(enumerate(zip(df[label], df[proc])))):
            if t/sum(df[proc]) < threshhold:
                labels_copy.pop(i)
                targets_copy.pop(i)
        if len(targets_copy) < len(df[proc]):
            labels_copy.append('其余')
            targets_copy.append(sum(df[proc])-sum(targets_copy))
            df_temp[label] = labels_copy
            df_temp[proc] = targets_copy
        else:
            df_temp = df
        return df_temp

    def queryCollegePieByYear(self, target='', year='全部', level='全部', union_threshhold=0.015, show_plot=False, save_plot=True, rdict=False):
        if target == '经费':
            # 属性名带括号要用``转义
            if year == '全部':
                query = f'''MATCH (p:project)-[r:belong_to]->(c:college)
                RETURN c.name AS college,SUM(p.`经费(元)`) AS target
                ORDER BY target DESC'''
            else:
                query = f'''MATCH (p:project)-[r:belong_to]->(c:college),(p)-[r1:start_year]->(y:year)
                WHERE y.name='{year}'
                RETURN c.name AS college,SUM(p.`经费(元)`) AS target
                ORDER BY target DESC'''
        elif target == '项目数量':
            if year == '全部':
                if level == '全部':
                    query = f'''MATCH (p:project)-[r:belong_to]->(c:college)
                    RETURN c.name AS college,COUNT(p) AS target
                    ORDER BY target DESC'''
                else:
                    query = f'''MATCH (p:project)-[r:belong_to]->(c:college),(p)-[r1:project_level]->(l:level)
                    WHERE l.name='{level}'
                    RETURN c.name AS college,COUNT(p) AS target
                    ORDER BY target DESC'''
            else:
                if level == '全部':
                    query = f'''MATCH (p:project)-[r:belong_to]->(c:college),(p)-[r1:start_year]->(y:year)
                    WHERE y.name='{year}'
                    RETURN c.name AS college,COUNT(p) AS target
                    ORDER BY target DESC'''
                else:
                    query = f'''MATCH (p:project)-[r:belong_to]->(c:college),(p)-[r1:start_year]->(y:year),(p)-[r2:project_level]->(l:level)
                    WHERE y.name='{year}' AND l.name='{level}'
                    RETURN c.name AS college,COUNT(p) AS target
                    ORDER BY target DESC'''
        elif target == '老师数量':
            if year == '全部':
                query = f'''MATCH (t:teacher)-[r:work_in]->(c:college)
                RETURN c.name AS college,COUNT(t) AS target
                ORDER BY target DESC'''
            else:
                query = f'''MATCH (t:teacher)-[r:work_in]->(c:college),(t)-[r1:conduct]->(p:project),(p)-[r2:start_year]->(y:year)
                WHERE y.name='{year}'
                RETURN c.name AS college,COUNT(t) AS target
                ORDER BY target DESC'''
        elif target == '跨学院项目数量':
            if year == '全部':
                query = f'''MATCH (t:teacher)-[r:conduct]->(p:project)-[r1:belong_to]->(c1:college),(t)-[r2:work_in]->(c2:college)
                WHERE c1 <> c2
                RETURN c1.name AS college,COUNT(p) AS target
                ORDER BY target DESC'''
            else:
                query = f'''MATCH (t:teacher)-[r:conduct]->(p:project)-[r1:belong_to]->(c1:college),(t)-[r2:work_in]->(c2:college),(p)-[r3:start_year]->(y:year)
                WHERE y.name='{year}' AND c1 <> c2
                RETURN c1.name AS college,COUNT(t) AS target
                ORDER BY target DESC'''
        # 疑问？如果year设成int，怎么写都查不出来
        result = self.__query(query)
        if result is not None:
            colleges = []
            targets = []
            for record in result:
                college = record["college"]
                tar = record["target"]
                colleges.append(college)
                targets.append(tar)
                print(college, tar)

            df = pd.DataFrame()
            df["college"] = colleges
            df["target"] = targets

            # 合并饼图很小的部分
            df_temp = self.__pie_process(
                df, 'target', 'college', threshhold=union_threshhold)

            # 绘图
            if save_plot or show_plot:
                fig = px.pie(df_temp, values='target', names='college',
                             title=f'各学院{target}情况统计')
                if save_plot:
                    fig.write_html(
                        f'./query_result/queryCollegePieByYear.html')
                if show_plot:
                    fig.show()

            if rdict:  # 用于js绘图
                res_data = [{'values': df_temp['target'].values.tolist(),
                            'labels': df_temp['college'].values.tolist(),
                             'type': 'pie'}]
                res_layout = {
                    'title': f'各学院{target}情况统计（共计{sum(targets)}）'}
                return [res_data, res_layout]
            else:
                return df
        else:
            print('Query Operation Error.')

    def queryProjectBarOfYear(self, target='', show_plot=False, save_plot=True, rdict=False):
        if target == '级别':
            query = f'''MATCH (p:project)-[r:start_year]->(y:year),(p)-[r1:project_level]->(l:level)
            RETURN y.name AS year,l.name AS target,COUNT(p) AS num
            ORDER BY year'''
        elif target == '类型':
            query = f'''MATCH (p:project)-[r:start_year]->(y:year),(p)-[r1:project_type]->(t:type)
            RETURN y.name AS year,t.name AS target,COUNT(p) AS num
            ORDER BY year'''
        result = self.__query(query)
        if result is not None:
            years = []
            targets = []
            nums = []
            for record in result:
                year = str(record["year"])+'年'
                tar = record["target"]
                num = record["num"]
                years.append(year)
                targets.append(tar)
                nums.append(num)

            df = pd.DataFrame()
            df["year"] = years
            df["target"] = targets
            df["num"] = nums
            project_nums = df.groupby("year").sum(numeric_only=True)
            df["percent"] = ["{:.2g}%".format(100*df.loc[i, "num"]/project_nums.loc[df.loc[i, "year"], "num"])
                             for i in range(len(df))]
            # 绘图
            if save_plot or show_plot:
                fig = px.bar(df, x="year", y="num",
                             color="target", text='percent', title=f'历年各{target}项目数量')
                if save_plot:
                    fig.write_html(
                        f'./query_result/queryProjectBarOfYear.html')
                if show_plot:
                    fig.show()

            if rdict:  # 用于js绘图
                res_data = []
                for t in df["target"].unique():
                    trace = {'x': df.loc[df["target"] == t, 'year'].values.tolist(),
                             'y': df.loc[df['target'] == t, 'num'].values.tolist(),
                             'text': df.loc[df['target'] == t, 'percent'].values.tolist(),
                             'name': t, 'type': 'bar'}
                    res_data.append(trace)
                res_layout = {'title': f'历年各{target}项目数量',
                              'barmode': 'stack'}
                return [res_data, res_layout]
            else:
                return df
        else:
            print('Query Operation Error.')

    def queryNumLineOfYear(self, targets=[], college='全部', show_plot=False, save_plot=True, rdict=False):
        df = pd.DataFrame()
        for target in targets:
            if college == '全部':
                if target == '学生':
                    query = f'''MATCH (s:student)-[r:join_in|responsible_for]->(p:project),(p)-[r1:start_year]->(y:year)
                            RETURN y.name AS year,COUNT(s) AS target
                            ORDER BY year'''
                elif target == '老师':
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(p)-[r1:start_year]->(y:year)
                            RETURN y.name AS year,COUNT(t) AS target
                            ORDER BY year'''
                elif target == '项目':
                    query = f'''MATCH (p:project)-[r:start_year]->(y:year)
                            RETURN y.name AS year,COUNT(p) AS target
                            ORDER BY year'''
            else:
                if target == '学生':
                    query = f'''MATCH (s:student)-[r:join_in|responsible_for]->(p:project),(p)-[r1:start_year]->(y:year),(p)-[r2:belong_to]->(c:college)
                            WHERE c.name='{college}'
                            RETURN y.name AS year,COUNT(s) AS target
                            ORDER BY year'''
                elif target == '老师':
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(p)-[r1:start_year]->(y:year),(p)-[r2:belong_to]->(c:college)
                            WHERE c.name='{college}'
                            RETURN y.name AS year,COUNT(t) AS target
                            ORDER BY year'''
                elif target == '项目':
                    query = f'''MATCH (p:project)-[r:start_year]->(y:year),(p)-[r1:belong_to]->(c:college)
                            WHERE c.name='{college}'
                            RETURN y.name AS year,COUNT(p) AS target
                            ORDER BY year'''
            result = self.__query(query)
            if result is not None:
                years = []
                tars = []
                for record in result:
                    year = str(record["year"])+'年'
                    years.append(year)
                    tar = record["target"]
                    tars.append(tar)

                df["year"] = years
                df[target] = tars
            else:
                print('Query Operation Error.')
        # 绘图
        if save_plot or show_plot:
            fig = go.Figure()
            for col in df:
                if col == 'year':
                    continue
                fig.add_trace(go.Scatter(x=df['year'].values.tolist(
                ), y=df[col].values.tolist(), mode='lines+markers', name=col))
            fig.update_layout(title=f"历年{''.join(targets)}参与数量")
            if save_plot:
                fig.write_html(
                    './query_result/queryLineOfYear.html')
            if show_plot:
                fig.show()

        if rdict:  # 用于js绘图
            res_data = []
            for col in df:
                if col == 'year':
                    continue
                trace = {'x': df['year'].values.tolist(),
                         'y': df[col].values.tolist(),
                         'mode': 'lines+markers', 'name': col, 'type': 'scatter'}
                res_data.append(trace)
            res_layout = {'title': f"历年{''.join(targets)}参与数量"}
            return [res_data, res_layout]
        else:
            return df

    def queryMemberBarOfLevel(self, target='', show_plot=False, save_plot=True, rdict=False):
        if target == '成员人数':
            query = f'''MATCH (p:project)-[r:project_level]->(l:level)
            RETURN p.成员人数 AS target,l.name AS level,COUNT(p) AS num
            ORDER BY target'''
        elif target == '指导教师人数':
            query = f'''MATCH (p:project)-[r:project_level]->(l:level)
            RETURN p.指导教师人数 AS target,l.name AS level,COUNT(p) AS num
            ORDER BY target'''
        result = self.__query(query)
        if result is not None:
            targets = []
            levels = []
            nums = []
            for record in result:
                tar = record["target"]
                level = record["level"]
                num = record["num"]
                targets.append(tar)
                levels.append(level)
                nums.append(num)

            df = pd.DataFrame()
            df["target"] = targets
            df["level"] = levels
            df["num"] = nums
            project_nums = df.groupby("level").sum(numeric_only=True)
            df["percent"] = ["{:.2g}%".format(100*df.loc[i, "num"]/project_nums.loc[df.loc[i, "level"], "num"])
                             for i in range(len(df))]

            # 绘图
            if save_plot or show_plot:
                fig = px.bar(df, x="level", y="num",
                             color="target", text="percent", title=f"各级别项目{target}组成")
                if save_plot:
                    fig.write_html(
                        './query_result/queryBarOfLevel.html')
                if show_plot:
                    fig.show()

            if rdict:  # 用于js绘图
                res_data = []
                for m in df["target"].unique():
                    trace = {'x': df.loc[df["target"] == m, 'level'].values.tolist(),
                             'y': df.loc[df['target'] == m, 'num'].values.tolist(),
                             'text': df.loc[df['target'] == m, 'percent'].values.tolist(),
                             'name': str(m)+'人', 'type': 'bar'}
                    res_data.append(trace)
                res_layout = {'title': f"各级别项目{target}组成",
                              'barmode': 'stack'}
                return [res_data, res_layout]
            else:
                return df
        else:
            print('Query Operation Error.')

    def queryProjectPieByCollege(self, target='', college='全部', threshhold=0.5, union_threshhold=0.015, show_plot=False, save_plot=True, rdict=False):
        if target == '关键词':
            targets = self.presetKeywords
            nums = []
            for keyword in targets:
                if college == '全部':
                    query = f'''MATCH (p:project)
                    WHERE p.{keyword}>={threshhold}
                    RETURN COUNT(p) AS num'''
                else:
                    query = f'''MATCH (p:project)-[r:belong_to]->(c:college)
                    WHERE p.{keyword}>={threshhold} AND c.name='{college}'
                    RETURN COUNT(p) AS num'''
                result = self.__query(query)
                # print(result)
                if result is not None:
                    for record in result:
                        num = record["num"]
                        nums.append(num)
                else:
                    nums.append(0)
        elif target == '一级学科' or target == '二级学科':
            d = 'd1' if target == '一级学科' else 'd2'
            if college == '全部':
                query = f'''MATCH (p:project)-[r:project_discipline]->(d2:discipline2)-[r1:subordinate]->(d1:discipline1)
                RETURN {d}.name AS target,COUNT(p) AS num
                ORDER BY num'''
            else:
                query = f'''MATCH (p:project)-[r:project_discipline]->(d2:discipline2)-[r1:subordinate]->(d1:discipline1),(p)-[r2:belong_to]->(c:college)
                WHERE c.name='{college}'
                RETURN {d}.name AS target,COUNT(p) AS num
                ORDER BY num'''
            result = self.__query(query)
            if result is not None:
                targets = []
                nums = []
                for record in result:
                    tar = record["target"]
                    num = record["num"]
                    targets.append(tar)
                    nums.append(num)

        if result is not None:
            df = pd.DataFrame()
            df["target"] = targets
            df["num"] = nums

            # 合并饼图很小的部分
            df_temp = self.__pie_process(
                df, 'num', 'target', threshhold=union_threshhold)

            # 绘图
            if save_plot or show_plot:
                fig = px.pie(df_temp, values='num', names='target',
                             title=f'项目各领域分布')
                if save_plot:
                    fig.write_html(
                        f'./query_result/queryProjectPieByCollege.html')
                if show_plot:
                    fig.show()

            if rdict:  # 用于js绘图
                res_data = [{'values': df_temp['num'].values.tolist(),
                            'labels': df_temp['target'].values.tolist(),
                             'type': 'pie'}]
                res_layout = {'title': f'项目各领域分布'}
                return [res_data, res_layout]
            else:
                return df
        else:
            print('Query Operation Error.')

    def queryGradeBarByYear(self, year='全部', show_plot=False, save_plot=True, rdict=False):
        if year == '全部':
            query = f'''MATCH (s:student)
            RETURN s.年级 AS grade,COUNT(s) AS num
            ORDER BY grade'''
        else:
            query = f'''MATCH (s:student)-[r:join_in|responsible_for]->(p:project),(p)-[r1:start_year]->(y:year)
            WHERE y.name='{year}'
            RETURN s.年级 AS grade,COUNT(s) AS num
            ORDER BY grade'''
        result = self.__query(query)
        if result is not None:
            grades = []
            nums = []
            for record in result:
                grade = record["grade"]
                num = record["num"]
                grades.append(grade)
                nums.append(num)

            df = pd.DataFrame()
            df["grade"] = grades
            df["num"] = nums

            # 绘图
            if save_plot or show_plot:
                fig = px.bar(df, x="grade", y="num", title=f"参与学生年级分布")
                if save_plot:
                    fig.write_html(
                        f'./query_result/queryGradeBarByYear.html')
                if show_plot:
                    fig.show()

            if rdict:  # 用于js绘图
                res_data = [{'x': df['grade'].values.tolist(),
                            'y': df['num'].values.tolist(),
                             'type': 'bar'}]
                res_layout = {'title': f'参与学生年级分布'}
                return [res_data, res_layout]
            else:
                return df
        else:
            print('Query Operation Error.')

    def queryPopularTeacherBarByCollege(self, year='全部', college='全部', rule='', topk=5, show_plot=False, save_plot=True, rdict=False):
        if rule == '指导项目等级':
            if year == '全部':
                if college == '全部':
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(p)-[r1:project_level]->(l:level)
                    RETURN t.name AS teacher,l.name AS level,COUNT(p) AS num'''
                else:
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(p)-[r1:project_level]->(l:level), (t)-[r2:work_in]->(c:college)
                    WHERE c.name='{college}'
                    RETURN t.name AS teacher,l.name AS level,COUNT(p) AS num'''
            else:
                if college == '全部':
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(p)-[r1:project_level]->(l:level),(p)-[r2:start_year]->(y:year)
                    WHERE y.name='{year}'
                    RETURN t.name AS teacher,l.name AS level,COUNT(p) AS num'''
                else:
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(p)-[r1:project_level]->(l:level),(t)-[r2:work_in]->(c:college),(p)-[r3:start_year]->(y:year)
                    WHERE c.name='{college}' AND y.name='{year}'
                    RETURN t.name AS teacher,l.name AS level,COUNT(p) AS num'''
            result = self.__query(query)
            if result is not None:
                teachers = []
                levels = []
                nums = []
                for record in result:
                    teacher = record["teacher"]
                    level = record["level"]
                    num = record["num"]
                    teachers.append(teacher)
                    levels.append(level)
                    nums.append(num)
                teacher_score = {}
                for t in set(teachers):
                    teacher_score[t] = 0
                for t, l, n in zip(teachers, levels, nums):
                    if l == '国家级':
                        teacher_score[t] += n*3
                    elif l == '市级':
                        teacher_score[t] += n*2
                    elif l == '校级':
                        teacher_score[t] += n*1
        elif rule == '指导项目数量':
            if year == '全部':
                if college == '全部':
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project)
                    RETURN t.name AS teacher,COUNT(p) AS num'''
                else:
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(t)-[r1:work_in]->(c:college)
                    WHERE c.name='{college}'
                    RETURN t.name AS teacher,COUNT(p) AS num'''
            else:
                if college == '全部':
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(p)-[r1:start_year]->(y:year)
                    WHERE y.name='{year}'
                    RETURN t.name AS teacher,COUNT(p) AS num'''
                else:
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(t)-[r1:work_in]->(c:college),(p)-[r2:start_year]->(y:year)
                    WHERE c.name='{college}' AND y.name='{year}'
                    RETURN t.name AS teacher,COUNT(p) AS num'''
            result = self.__query(query)
            if result is not None:
                teachers = []
                nums = []
                for record in result:
                    teacher = record["teacher"]
                    num = record["num"]
                    teachers.append(teacher)
                    nums.append(num)
                teacher_score = {}
                for t, n in zip(teachers, nums):
                    teacher_score[t] = n
        elif rule == '指导学生人数':
            if year == '全部':
                if college == '全部':
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(s:student)-[r1:responsible_for|join_in]->(p)
                    RETURN t.name AS teacher,COUNT(s) AS num'''
                else:
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(t)-[r1:work_in]->(c:college),(s:student)-[r2:responsible_for|join_in]->(p)
                    WHERE c.name='{college}'
                    RETURN t.name AS teacher,COUNT(s) AS num'''
            else:
                if college == '全部':
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(p)-[r1:start_year]->(y:year),(s:student)-[r2:responsible_for|join_in]->(p)
                    WHERE y.name='{year}'
                    RETURN t.name AS teacher,COUNT(s) AS num'''
                else:
                    query = f'''MATCH (t:teacher)-[r:conduct]->(p:project),(t)-[r1:work_in]->(c:college),(p)-[r2:start_year]->(y:year),(s:student)-[r3:responsible_for|join_in]->(p)
                    WHERE c.name='{college}' AND y.name='{year}'
                    RETURN t.name AS teacher,COUNT(s) AS num'''
            result = self.__query(query)
            if result is not None:
                teachers = []
                nums = []
                for record in result:
                    teacher = record["teacher"]
                    num = record["num"]
                    teachers.append(teacher)
                    nums.append(num)
                teacher_score = {}
                for t, n in zip(teachers, nums):
                    teacher_score[t] = n
        if result is not None:
            df = pd.DataFrame()
            df["teacher"] = list(teacher_score.keys())
            df["score"] = list(teacher_score.values())
            df = df.sort_values(by='score', ascending=False)
            df = df[:topk]
            # 绘图
            if save_plot or show_plot:
                fig = px.bar(df, x="teacher", y="score",
                             title=f"“网红”教师排行榜")
                if save_plot:
                    fig.write_html(
                        f'./query_result/queryPopularTeacherBarByCollege.html')
                if show_plot:
                    fig.show()

            if rdict:  # 用于js绘图
                res_data = [{'x': df['teacher'].values.tolist(),
                            'y': df['score'].values.tolist(),
                             'type': 'bar'}]
                res_layout = {'title': f'“网红”教师排行榜'}
                return [res_data, res_layout]
            else:
                return df
        else:
            print('Query Operation Error.')

    """ 数据查询模块 函数"""

    # 查询一个节点距离k以内所有的节点和关系
    def querySubgraphByDistance(self, type, id=None, k=1):
        if k == 1:
            if id is None:  # 若没有指定ID，则随机展示一个
                k = random.randint(0, self.node_count[type]-1)
                query = f'''MATCH (p:{type})
                            WITH p SKIP {k} LIMIT 1
                            RETURN id(p) AS id'''
                result = self.__query(query)
                for record in result:
                    id = record['id']

            query = f'''MATCH (p:{type})-[r]-(q) 
            WHERE id(p)={id}
            WITH p+COLLECT(q) AS nodelist
            MATCH (start)-[rel]->(end)
            WHERE start IN nodelist AND end IN nodelist
            RETURN start AS startnode,rel AS relation,end AS endnode,id(start) AS startID,id(rel) AS relationID,id(end) AS endID'''
            result = self.__query(query)
            # print(result)
            res = []
            for record in result:
                startnode = {"identity": record['startID'],
                             "labels": record['startnode'].labels.__repr__().split(':')[1:],
                             "properties": dict(record['startnode'].items())}
                endnode = {"identity": record['endID'],
                           "labels": record['endnode'].labels.__repr__().split(':')[1:],
                           "properties": dict(record['endnode'].items())}
                relationship = {"identity": record['relationID'],
                                "start": startnode["identity"],
                                "end": endnode["identity"],
                                "type": list(record['relation'].types())[0],
                                "properties": dict(record['relation'].items())}
                subres = {"start": startnode, "end": endnode, "segments": [
                    {"start": startnode, "relationship": relationship, "end": endnode}]}
                res.append(subres)
                # print(record['startnode'].labels.__repr__().split(':')[1:],
                #       record['startID'], dict(record['startnode'].items()))
                # print(list(record['relation'].types()),
                #       record['relationID'], dict(record['relation'].items()))
                # print(record['endnode'].labels.__repr__().split(':')[1:],
                #       record['endID'], dict(record['endnode'].items()))
            return res

    # 查询某一类型的节点
    def queryNodeByType(self, type):
        query = f'''MATCH (p:{type})
        RETURN p AS node,id(p) AS nodeID'''
        result = self.__query(query)
        # print(result)
        res = []
        for record in result:
            node = {"identity": record['nodeID'],
                    "labels": record['node'].labels.__repr__().split(':')[1:],
                    "properties": dict(record['node'].items())}
            subres = {"node": node}
            res.append(subres)
        return res

    # 关键字查询，支持多个关键词，以空格划分
    def queryNodeByKeywords(self, keywords, searchRange=[], condition={}):
        # 还可加入学生年级、项目领域等
        resAll = []
        def process_name(x): return f"'{x}'"  # 处理条件查询传入列表中的名字
        if keywords:
            keywords = keywords.split(' ')
            re = ''
            for k in keywords:
                re += f'(?=.*{k}.*)'  # ?=正向预查，检查子模式是否存在
            re += '^.*$'  # 从开头到结尾
            for r in searchRange:
                if '学生' == r:
                    query = f'''MATCH (s:student)
                    WHERE s.name =~ '{re}'
                    RETURN s AS node,id(s) AS nodeID'''
                elif '教师' == r:
                    condition_where = []
                    if condition['教师所属学院']:
                        restrict = list(map(process_name, condition['教师所属学院']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"c.name IN {restrict}")
                    condition_where.append('')
                    condition_where = ' AND '.join(condition_where)
                    query = f'''MATCH (t:teacher)-[r:work_in]->(c:college)
                    WHERE {condition_where} t.name =~ '{re}'
                    RETURN t AS node,id(t) AS nodeID'''
                elif '项目名称' == r or '项目简介' == r:
                    condition_where = []
                    if condition['项目所属学院']:
                        restrict = list(map(process_name, condition['项目所属学院']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"c.name IN {restrict}")
                    if condition['项目级别']:
                        restrict = list(map(process_name, condition['项目级别']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"l.name IN {restrict}")
                    if condition['项目类型']:
                        restrict = list(map(process_name, condition['项目类型']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"t.name IN {restrict}")
                    if condition['项目年份']:
                        restrict = list(map(process_name, condition['项目年份']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"y.name IN {restrict}")
                    if condition['项目一级学科']:
                        restrict = list(map(process_name, condition['项目一级学科']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"d1.name IN {restrict}")
                    if condition['项目二级学科']:
                        restrict = list(map(process_name, condition['项目二级学科']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"d2.name IN {restrict}")
                    condition_where.append('')
                    condition_where = ' AND '.join(condition_where)
                    if '项目名称' == r:
                        query = f'''MATCH (p:project)-[r:belong_to]->(c:college),(p)-[r1:project_level]->(l:level),(p)-[r2:project_type]->(t:type),(p)-[r3:start_year]->(y:year),(p)-[r4:project_discipline]->(d2:discipline2)-[r5:subordinate]->(d1:discipline1)
                        WHERE {condition_where}p.name =~ '{re}'
                        RETURN p AS node,id(p) AS nodeID'''
                    elif '项目简介' == r:
                        query = f'''MATCH (p:project)-[r:belong_to]->(c:college),(p)-[r1:project_level]->(l:level),(p)-[r2:project_type]->(t:type),(p)-[r3:start_year]->(y:year),(p)-[r4:project_discipline]->(d2:discipline2)-[r5:subordinate]->(d1:discipline1)
                        WHERE {condition_where}p.简介 =~ '{re}'
                        RETURN p AS node,id(p) AS nodeID'''
                result = self.__query(query)
                res = []
                for record in result:
                    node = {"identity": record['nodeID'],
                            "labels": record['node'].labels.__repr__().split(':')[1:],
                            "properties": dict(record['node'].items())}
                    subres = {"node": node}
                    res.append(subres)
                resAll += res
        else:  # 若没有输入关键词，则基于条件查询所有项目
            for r in searchRange:
                if '学生' == r:
                    query = f'''MATCH (s:student)
                    RETURN s AS node,id(s) AS nodeID'''
                if '教师' == r:
                    condition_where = []
                    if condition['教师所属学院']:
                        restrict = list(map(process_name, condition['教师所属学院']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"c.name IN {restrict}")
                    condition_where = ' AND '.join(condition_where)
                    if condition_where:
                        condition_where = 'WHERE ' + condition_where
                    query = f'''MATCH (t:teacher)-[r:work_in]->(c:college)
                    {condition_where}
                    RETURN t AS node,id(t) AS nodeID'''
                elif '项目名称' == r or '项目简介' == r:
                    condition_where = []
                    if condition['项目所属学院']:
                        restrict = list(map(process_name, condition['项目所属学院']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"c.name IN {restrict}")
                    if condition['项目级别']:
                        restrict = list(map(process_name, condition['项目级别']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"l.name IN {restrict}")
                    if condition['项目类型']:
                        restrict = list(map(process_name, condition['项目类型']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"t.name IN {restrict}")
                    if condition['项目年份']:
                        restrict = list(map(process_name, condition['项目年份']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"y.name IN {restrict}")
                    if condition['项目一级学科']:
                        restrict = list(map(process_name, condition['项目一级学科']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"d1.name IN {restrict}")
                    if condition['项目二级学科']:
                        restrict = list(map(process_name, condition['项目二级学科']))
                        restrict = '['+','.join(restrict)+']'
                        condition_where.append(f"d2.name IN {restrict}")
                    condition_where = ' AND '.join(condition_where)
                    if condition_where:
                        condition_where = 'WHERE ' + condition_where
                    query = f'''MATCH (p:project)-[r:belong_to]->(c:college),(p)-[r1:project_level]->(l:level),(p)-[r2:project_type]->(t:type),(p)-[r3:start_year]->(y:year),(p)-[r4:project_discipline]->(d2:discipline2)-[r5:subordinate]->(d1:discipline1)
                    {condition_where}
                    RETURN p AS node,id(p) AS nodeID'''
                result = self.__query(query)
                res = []
                for record in result:
                    node = {"identity": record['nodeID'],
                            "labels": record['node'].labels.__repr__().split(':')[1:],
                            "properties": dict(record['node'].items())}
                    subres = {"node": node}
                    res.append(subres)
                resAll += res

        return resAll

    # 预置关键词，基于相似度过滤匹配
    def queryProjectByKeywordSim(self, topic, threshhold=0.5):
        query = f'''MATCH (p:project)
        WHERE p.{topic}>={threshhold}
        RETURN p AS node,id(p) AS nodeID
        ORDER BY p.{topic} DESC'''
        result = self.__query(query)
        # print(result)
        res = []
        for record in result:
            node = {"identity": record['nodeID'],
                    "labels": record['node'].labels.__repr__().split(':')[1:],
                    "properties": dict(record['node'].items())}
            subres = {"node": node}
            res.append(subres)
        return res

    # 查询相似项目
    def querySimilarProject(self, id, threshhold=0.85):
        def computeCosSim(vec1, vec2):  # 计算余弦相似度工具函数
            return np.sum(np.array(vec1) * np.array(vec2)) / (np.linalg.norm(np.array(vec1)) * np.linalg.norm(np.array(vec2)))

        query = f'''MATCH (p:project)
        RETURN id(p) AS id, p.简介向量表示 AS vec'''
        result = self.__query(query)
        res = {}
        for record in result:
            identity = record['id']
            vec = record['vec']
            res[identity] = vec

        thFilter = {}
        target_vec = res[id]
        for pj in res:
            sim = computeCosSim(target_vec, res[pj])
            if sim >= threshhold:
                thFilter[str(pj)] = sim

        query = f'''MATCH (p:project)
        WHERE id(p) IN [{','.join(thFilter.keys())}]
        RETURN p AS node,id(p) AS nodeID'''
        result = self.__query(query)
        res = []
        for record in result:
            properties = dict(record['node'].items())
            properties.update({'相似度': thFilter[str(record['nodeID'])]})
            node = {"identity": record['nodeID'],
                    "labels": record['node'].labels.__repr__().split(':')[1:],
                    "properties": properties}
            subres = {"node": node}
            res.append(subres)
        return res

    # 编辑节点
    def editNode(self, id, properties):
        update_prop = ""
        for k in properties:
            if k == "简介向量表示":
                continue
            try:
                float(properties[k])
                update_prop += f"SET n.`{k}`={properties[k]} "
            except:
                update_prop += f"SET n.`{k}`='{properties[k]}' "
        query = f'''MATCH (n)
        WHERE id(n)={id}
        {update_prop}'''
        result = self.__query(query)
        if result is None:
            return 'error'
        else:
            return 'success'


if __name__ == '__main__':
    handler = QueryProjectGraph()
    # handler.queryBudgetForCollege()
    # handler.queryBudgetForCollege(year=2022)
    # handler.queryBudgetForCollege(year=2023)
    # handler.queryLevelOfYear(show_plot=False, save_plot=False, rdict=True)
    # handler.queryNumLineOfYear()
    # handler.queryProjectMemberOfLevel()
    # handler.queryProject()
    # num = len(handler.queryProjectByTopicKeyword('深度学习'))
    # print(num)
    # num = len(handler.queryProjectByTopicKeyword('机器学习'))
    # print(num)
    # num = len(handler.queryProjectByTopicKeyword('强化学习'))
    # print(num)
    # num = len(handler.queryProjectByTopicKeyword('人工智能'))
    # print(num)
    # handler.queryProjectNumOfPresetKeyword()
    # handler.queryStudentNumOfGradeByYear(save_plot=True)
    # with open("./entity_data/year.txt", "r", encoding="utf-8") as f:
    #     year_entity = f.read().split('\n')
    #     year_entity.reverse()
    #     print(year_entity)

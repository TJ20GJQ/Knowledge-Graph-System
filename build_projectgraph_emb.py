import pandas as pd
from tqdm import tqdm
from py2neo import Graph, Node
import yaml
import numpy as np
import re


class BuildProjectGraph:
    """
    BuildProjectGraph类对外提供四个方法: (构建实体, 构建关系) -> 构建整体KG, 导出实体名称
    """

    def __init__(self, data_path, init=True):
        """
        :param data_path: 数据路径
        :param init: 是否需要初始化数据库
        """
        self.data_path = data_path
        self.__graph = Graph("http://localhost:7474",
                             auth=("neo4j", "GJQ1030n4j"))
        self.entities = ['project', 'student', 'teacher', 'college',
                         'year', 'level', 'type', 'discipline1', 'discipline2']
        self.rels = ['belong_to', 'work_in', 'join_in', 'responsible_for', 'conduct',
                     'start_year', 'project_level', 'project_type', 'project_discipline', 'subordinate']
        if init:
            self.__graph.delete_all()  # 清空数据库
            # 清除唯一性约束
            for e in self.entities:
                for c in self.__graph.schema.get_uniqueness_constraints(e):
                    self.__graph.schema.drop_uniqueness_constraint(e, c)

        self.__read_flag = False  # 是否已读取实体和关系信息

    def __read_nodes(self):  # __私有
        """
        读取数据，解析实体和关系节点
        :return:
        """
        # 9类实体
        self.projects = []
        self.students = []
        self.teachers = []
        self.colleges = []
        self.years = []
        self.levels = []
        self.types = []
        self.disciplines1 = []
        self.disciplines2 = []

        # 保存属性信息
        self.project_infos = []  # 项目实体属性
        self.student_infos = []  # 学生实体属性
        self.teacher_infos = []  # 老师实体属性
        self.disciplines2_infos = []  # 二级学科实体属性

        # 实体关系
        self.rels_belongto = []  # 项目-学院关系
        self.rels_workin = []  # 老师-学院关系
        self.rels_participant = []  # 学生-项目关系
        self.rels_responsible = []  # 负责人-项目关系
        self.rels_conductor = []  # 老师-项目关系
        self.rels_startyear = []  # 项目-年份关系
        self.rels_level = []  # 项目-级别关系
        self.rels_type = []  # 项目-类型关系
        self.rels_discipline = []  # 项目-二级学科关系
        self.rels_subordinate = []  # 二级学科-一级学科关系
        # self.rels_similar = []  # 项目-项目关系（带属性）

        all_data = pd.read_csv(
            self.data_path, sep='|').to_dict(orient='records')
        for data in all_data:  # 读取CSV后向量为字符串，需要转成list
            data['项目简介向量表示'] = list(
                map(lambda x: float(x), data['项目简介向量表示'][1:-1].split(', ')))

        emb_num = 1024  # 项目简介向量表示维度
        # similarity_threshhold = 0.85  # 项目相似关系阈值

        # def computeCosSim(vec1, vec2):  # 计算余弦相似度工具函数
        #     return np.sum(np.array(vec1) * np.array(vec2)) / (np.linalg.norm(np.array(vec1)) * np.linalg.norm(np.array(vec2)))

        with open("./data/data.yaml", "r", encoding="utf-8") as f:  # 读取配置文件中的关键词类别
            myTopics = yaml.safe_load(f)['myKeyword']

        print('加载节点信息中...')
        for data in tqdm(all_data):  # 遍历所有项目
            project_dict = {}

            # 定义项目节点属性
            project = str(data['项目编号'])  # 为了防止项目重名，实体id设为项目编号
            if project in self.projects:  # 前面有同一个项目则跳过
                continue
            project_dict['编号'] = project
            self.projects.append(project)  # 添加项目实体
            project_dict['批次'] = data['批次']
            project_dict['名称'] = data['项目名称']
            project_dict['成员人数'] = int(data['参与学生人数'])
            # project_dict['经费(元)'] = str(int(data['项目总经费(元)']))+'(' + \
            #     str(int(data['财政拨款/企业资助(元)'])) + \
            #     '/'+str(int(data['学校拨款(元)']))+')'
            project_dict['经费(元)'] = int(data['项目总经费(元)'])
            project_dict['中期状态'] = data['中期状态']
            project_dict['结题状态'] = data['结题状态']
            project_dict['延期状态'] = data['延期状态']
            project_dict['终止状态'] = data['终止状态']
            project_dict['是否终止'] = data['是否终止项目']
            project_dict['简介'] = data['项目简介']
            for t in myTopics:  # 关键词相似度
                project_dict[t] = data[t]
            project_dict['简介向量表示'] = data['项目简介向量表示']
            # for data0 in all_data:  # embedding
            #     if str(data0['项目编号']) != project:
            #         sim = computeCosSim(
            #             project_dict['简介向量表示'], data0['项目简介向量表示'])
            #         if sim >= similarity_threshhold:
            #             self.rels_similar.append(
            #                 [project, data0['项目编号'], {'相似度': sim}])

            self.rels_discipline.append([project, data['项目所属二级学科']])
            self.disciplines1.append(data['项目所属一级学科'])
            if data['项目所属二级学科'] not in self.disciplines2:
                self.disciplines2.append(data['项目所属二级学科'])
                disciplines2_dict = {}
                disciplines2_dict['二级学科'] = data['项目所属二级学科']
                disciplines2_dict['专业类代码'] = str(data['项目所属专业类代码'])
                self.rels_subordinate.append(
                    [data['项目所属二级学科'], data['项目所属一级学科']])
                self.disciplines2_infos.append(disciplines2_dict)

            if data['年份']:
                self.years.append(str(data['年份']))  # 添加年份实体
                self.rels_startyear.append(
                    [project, str(data['年份'])])  # 项目起始年份关系

            if data['级别']:
                self.levels.append(data['级别'])  # 添加项目级别实体，4种
                self.rels_level.append(
                    [project, data['级别']])  # 项目所属级别关系

            if data['项目类型']:
                self.types.append(data['项目类型'])  # 添加项目类型实体，3种
                self.rels_type.append(
                    [project, data['项目类型']])  # 项目所属类型关系

            if data['所属学院']:
                self.colleges.append(data['所属学院'])  # 添加学院实体
                self.rels_belongto.append(
                    [project, data['所属学院']])  # 项目所属学院关系

            if data['项目负责人姓名'] != '无':
                student_info = {}
                student = str(data['负责人学号'])  # 为了防止学生重名，实体id设为学生学号
                exist_flag = False
                if student in self.students:  # 前面已存在该信息，记录，比较信息全面性
                    exist_flag = True
                student_info['学号'] = student
                student_info['年级'] = '20'+student[:2]+'级'
                self.students.append(student)  # 添加学生实体
                student_info['姓名'] = data['项目负责人姓名']
                if data['负责人手机'] != '无':
                    student_info['手机号'] = str(data['负责人手机'])
                if data['负责人邮箱'] != '无':
                    student_info['邮箱'] = data['负责人邮箱']
                if exist_flag:  # 筛选出同一份信息，综合信息保存更新的
                    existed = list(filter(lambda val: val != '', [
                        si if si['学号'] == student else '' for si in self.student_infos]))[0]
                    for k in existed.keys():
                        if k not in student_info.keys():
                            student_info[k] = existed[k]
                    self.student_infos.remove(existed)  # 删除原有的信息
                self.student_infos.append(student_info)  # 保存综合后的信息
                # self.rels_participant.append(
                #     [student, project])  # 学生参与项目关系(先不算了)
                self.rels_responsible.append(
                    [student, project])  # 学生负责项目关系

            if data['项目其他成员信息'] != '无':
                for stu in data['项目其他成员信息'].split('，'):
                    student_info = {}
                    student = str(stu.split('(')[1].split(')')[0])  # 提取学号
                    exist_flag = False
                    if student in self.students:  # 前面已存在该信息，记录，比较信息全面性
                        exist_flag = True
                    student_info['学号'] = student
                    student_info['年级'] = '20'+student[:2]+'级'
                    self.students.append(student)  # 添加学生实体
                    student_info['姓名'] = stu.split('(')[0]  # 提取姓名
                    if exist_flag:  # 筛选出同一份信息，综合信息保存更新的
                        existed = list(filter(lambda val: val != '', [
                            si if si['学号'] == student else '' for si in self.student_infos]))[0]
                        for k in existed.keys():
                            if k not in student_info.keys():
                                student_info[k] = existed[k]
                        self.student_infos.remove(existed)  # 删除原有的信息
                    self.student_infos.append(student_info)  # 保存综合后的信息
                    self.rels_participant.append(
                        [student, project])  # 学生参与项目关系

            if data['指导教师姓名'] != '无':
                project_dict['指导教师人数'] = len(data['教师工号'].split('，'))
                for i in range(len(data['教师工号'].split('，'))):
                    teacher_info = {}
                    teacher = str(data['教师工号'].split('，')[i])  # 提取工号
                    exist_flag = False
                    if teacher in self.teachers:  # 前面已存在该信息，记录，比较信息全面性
                        exist_flag = True
                    teacher_info['工号'] = teacher
                    self.teachers.append(teacher)
                    teacher_info['姓名'] = data['指导教师姓名'].split('，')[i]
                    teacher_info['职称'] = data['教师职称'].split('，')[i]
                    if exist_flag:  # 筛选出同一份信息，综合信息保存更新的
                        existed = list(filter(lambda val: val != '', [
                            ti if ti['工号'] == teacher else '' for ti in self.teacher_infos]))[0]
                        for k in existed.keys():
                            if k not in teacher_info.keys():
                                teacher_info[k] = existed[k]
                        self.teacher_infos.remove(existed)  # 删除原有的信息
                    self.teacher_infos.append(teacher_info)  # 保存综合后的信息
                    self.rels_conductor.append(
                        [teacher, project])  # 老师指导项目关系
                    college = data['教师所属学院'].split('，')[i]
                    self.colleges.append(college)  # 添加学院实体
                    self.rels_workin.append(
                        [teacher, college])  # 老师工作于学院关系
            else:
                project_dict['指导教师人数'] = 0

            # 添加项目属性
            self.project_infos.append(project_dict)

        # 去重
        self.projects = list(set(self.projects))
        self.students = list(set(self.students))
        self.teachers = list(set(self.teachers))
        self.colleges = list(set(self.colleges))
        self.years = list(set(self.years))
        self.levels = list(set(self.levels))
        self.types = list(set(self.types))
        self.disciplines1 = list(set(self.disciplines1))
        self.disciplines2 = list(set(self.disciplines2))
        self.rels_workin = [list(t) for t in set(tuple(element)
                                                 for element in self.rels_workin)]
        self.rels_subordinate = [list(t) for t in set(
            tuple(element) for element in self.rels_subordinate)]

        self.__read_flag = True

    def __create_node(self, label, nodes, uniconstraint=None, name=None):
        """
        创建neo4j实体节点
        :param label: 实体类型
        :param nodes: 两种情况: list, 无属性的节点信息; dict, 带属性的节点信息
        :param uniconstraint: 添加唯一性约束(不允许重名)
        :param name: 指定dict哪一个属性为节点name(用于在neo4j中显示)
        :return:
        """
        print(f'创建{label}实体中...')
        if uniconstraint is not None:
            try:
                self.__graph.schema.create_uniqueness_constraint(
                    label, uniconstraint)  # 添加唯一性约束，只需要添加一次
            except:
                pass

        if isinstance(nodes[0], dict):  # 建立带有属性的实体节点
            for node_info in tqdm(nodes):
                attrs = list(node_info.keys())
                if name is not None:
                    node = Node(label, name=node_info[name])
                    attrs.remove(name)
                else:
                    node = Node(label)
                for attr in attrs:
                    node.update({attr: node_info[attr]})
                self.__graph.create(node)
        else:  # 建立不带有属性的实体节点
            for node_name in tqdm(nodes):
                node = Node(label, name=node_name)
                self.__graph.create(node)

    def create_graphnodes(self):
        """
        创建所有实体节点
        :return:
        """
        if not self.__read_flag:
            self.__read_nodes()

        self.__create_node('project', nodes=self.project_infos,
                           uniconstraint="编号", name='名称')  # 创建项目节点
        self.__create_node('student', nodes=self.student_infos,
                           uniconstraint="学号", name='姓名')  # 创建学生节点
        self.__create_node('teacher', nodes=self.teacher_infos,
                           uniconstraint="工号", name='姓名')  # 创建老师节点
        self.__create_node('college', nodes=self.colleges,
                           uniconstraint='name')  # 创建学院节点
        self.__create_node('year', nodes=self.years,
                           uniconstraint='name')  # 创建年份节点
        self.__create_node('level', nodes=self.levels,
                           uniconstraint='name')  # 创建级别节点
        self.__create_node('type', nodes=self.types,
                           uniconstraint='name')  # 创建类型节点
        self.__create_node('discipline1', nodes=self.disciplines1,
                           uniconstraint='name')  # 创建一级学科节点
        self.__create_node('discipline2', nodes=self.disciplines2_infos,
                           uniconstraint='专业类代码', name='二级学科')  # 创建二级学科节点

    def __create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        """
        创建neo4j实体关联边
        :param start_node: (起点节点,id)
        :param end_node: (终点节点,id)
        :param edges: list, 关系信息
        :param rel_type: 关系类型
        :param rel_name: 关系名字
        :return:
        """
        print(f'创建{rel_name}关系中...')
        for edge in tqdm(edges):
            p = edge[0]
            q = edge[1]
            # match语法，p，q分别为标签，rel_type关系类别，rel_name关系名字
            if len(edge) == 2:
                query = f'''MATCH (p:{start_node[0]}),(q:{end_node[0]})
                        WHERE p.{start_node[1]}='{p}'AND q.{end_node[1]}='{q}'
                        CREATE (p)-[rel:{rel_type}{{name:'{rel_name}'}}]->(q)'''
            elif len(edge) == 3:  # 创建带属性的关系
                attr = edge[2]
                attr_list = []
                for i in attr:
                    attr_list.append(str(i)+':'+str(attr[i]))
                attr_cypher = ','.join(attr_list)
                query = f'''MATCH (p:{start_node[0]}),(q:{end_node[0]})
                        WHERE p.{start_node[1]}='{p}'AND q.{end_node[1]}='{q}'
                        CREATE (p)-[rel:{rel_type}{{name:'{rel_name}',{attr_cypher}}}]->(q)'''
            try:
                self.__graph.run(query)  # 执行语句
            except Exception as e:
                print(e)

    def create_graphrels(self):
        """
        创建所有实体关联边
        :return:
        """
        if not self.__read_flag:
            self.__read_nodes()

        # self.__create_relationship(
        #     ('project', '编号'), ('project', '编号'), self.rels_similar, 'similar_project', '相似项目')
        self.__create_relationship(
            ('project', '编号'), ('college', 'name'), self.rels_belongto, 'belong_to', '项目所属学院')
        self.__create_relationship(
            ('teacher', '工号'), ('college', 'name'), self.rels_workin, 'work_in', '老师工作学院')
        self.__create_relationship(
            ('student', '学号'), ('project', '编号'), self.rels_responsible, 'responsible_for', '学生负责项目')
        self.__create_relationship(
            ('student', '学号'), ('project', '编号'), self.rels_participant, 'join_in', '学生参与项目')
        self.__create_relationship(
            ('teacher', '工号'), ('project', '编号'), self.rels_conductor, 'conduct', '老师指导项目')
        self.__create_relationship(
            ('project', '编号'), ('year', 'name'), self.rels_startyear, 'start_year', '项目起始年份')
        self.__create_relationship(
            ('project', '编号'), ('level', 'name'), self.rels_level, 'project_level', '项目所属级别')
        self.__create_relationship(
            ('project', '编号'), ('type', 'name'), self.rels_type, 'project_type', '项目所属类型')
        self.__create_relationship(
            ('project', '编号'), ('discipline2', 'name'), self.rels_discipline, 'project_discipline', '项目所属学科')
        self.__create_relationship(
            ('discipline2', 'name'), ('discipline1', 'name'), self.rels_subordinate, 'subordinate', '学科隶属关系')

    def constructKG(self):
        """
        构建KG, 实体和关系
        :return:
        """
        self.create_graphnodes()
        self.create_graphrels()

    def export_data(self, export_folder='./entity_data/'):
        """
        导出实体数据为txt, 用于记录
        :param export_folder: 导出文件夹路径
        :return:
        """
        if not self.__read_flag:
            self.__read_nodes()

        entities = dict(zip(self.entities, [self.projects, self.students, self.teachers, self.colleges,
                                            self.years, self.levels, self.types, self.disciplines1, self.disciplines2]))
        for e in entities:
            with open(export_folder+e+'.txt', 'w+') as f:
                f.write('\n'.join(entities[e]))

        print(f'Export entity data to {export_folder}....')


if __name__ == '__main__':
    handler = BuildProjectGraph(
        './data/project_emb_data.csv', init=True)  # 创建图数据库
    # handler.export_data()  # 输出数据，可以选择不执行
    handler.constructKG()  # 构建知识图谱
    # handler.create_graphnodes()  # 创建节点
    # handler.create_graphrels()  # 创建关系

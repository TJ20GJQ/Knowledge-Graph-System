<template>
  <div class="gContainer" v-loading="data_loading" element-loading-text="Loading..."
    element-loading-background="rgba(157,173,193,0)">
    <d3graph :data="data" :names="names" :labels="labels" :sizes="sizes" :linkTypes="linkTypes"
      @queryExpandEvent="queryExpand" @queryNodeEvent="queryNode" @queryNodeOfTypeEvent="queryNodeOfType"
      @queryNodeOfKeywordsEvent="queryNodeOfKeywords"
      @queryProjectOfPresetKeywordSimEvent="queryProjectOfPresetKeywordSim"
      @querySimilarProjectEvent="querySimilarProject" @editNodeEvent="editNode" />
  </div>
</template>

<script>
import d3graph from '@/components/d3graph.vue'
import axios from 'axios'
import { ref } from 'vue'
export default {
  components: {
    d3graph
  },
  data() {
    return {
      queryNodeServer: "http://127.0.0.1:5000/queryNodeOnly",
      queryNodeOfTypeServer: "http://127.0.0.1:5000/queryNodeByType",
      queryNodeOfKeywordsServer: "http://127.0.0.1:5000/queryNodeByKeywords",
      queryProjectOfKeywordSimServer: "http://127.0.0.1:5000/queryProjectByKeywordSim",
      querySimilarProjectServer: "http://127.0.0.1:5000/querySimilarProject",
      editNodeServer: "http://127.0.0.1:5000/editNode",
      org_data: null,
      data_loading: ref(true),
      data: {
        nodes: [],
        links: []
      },
      names: ['项目', '学生', '老师', '学院', '年份', '项目级别', '项目类型', '一级学科', '二级学科'],
      labels: ['project', 'student', 'teacher', 'college', 'year', 'level', 'type', 'discipline1', 'discipline2'],
      sizes: [40, 26, 28, 30, 32, 32, 32, 36, 32],  // 节点大小
      linkTypes: ['belong_to', 'work_in', 'join_in', 'responsible_for',
        'conduct', 'start_year', 'project_level', 'project_type', 'project_discipline', 'subordinate'],
    }
  },
  created() {
    this.loadFirstData()
  },
  methods: {
    // 视图更新
    update(json) {
      // console.log('update', json)
      this.d3jsonParser(json)
    },
    // 解析json数据，主要负责数据的去重、标准化
    d3jsonParser(json) {
      const nodes = []
      const links = [] // 存放节点和关系
      const nodeSet = [] // 存放去重后nodes的id

      for (let item of json) {
        if (item.segments) {  // 如果有关系，解析关系
          for (let segment of item.segments) {
            // 重新更改data格式
            if (nodeSet.indexOf(segment.start.identity) == -1) {
              nodeSet.push(segment.start.identity)
              nodes.push({
                id: segment.start.identity,
                label: segment.start.labels[0],
                properties: segment.start.properties
              })
            }
            if (nodeSet.indexOf(segment.end.identity) == -1) {
              nodeSet.push(segment.end.identity)
              nodes.push({
                id: segment.end.identity,
                label: segment.end.labels[0],
                properties: segment.end.properties
              })
            }
            links.push({
              source: segment.relationship.start,
              target: segment.relationship.end,
              type: segment.relationship.type,
              properties: segment.relationship.properties
            })
          }
        }
        else {  // 否则解析节点
          if (nodeSet.indexOf(item.node.identity) == -1) {
            nodeSet.push(item.node.identity)
            nodes.push({
              id: item.node.identity,
              label: item.node.labels[0],
              properties: item.node.properties
            })
          }
        }
      }
      this.data = { nodes, links }
      console.log("🚀 ~ d3jsonParser ~ this.data:", this.data)
    },
    // 加载首次数据
    loadFirstData() {
      // 随机加载一个项目信息
      axios.post(this.queryNodeServer, { 'type': 'project' })
        .then(response => {
          this.org_data = response.data;
          this.data_loading = false
          this.update(this.org_data)
        })
        .catch(error => {
          console.error(error);
        });
    },
    // 扩展一个节点
    queryExpand(label, id) {
      console.log('expandNode', label, id);
      axios.post(this.queryNodeServer, { 'type': label, 'id': id })
        .then(response => {
          this.org_data = response.data.concat(this.org_data);
          // console.log('expandNode data', this.org_data);
          this.update(this.org_data)
        })
        .catch(error => {
          console.error(error);
        });
    },
    // 展开某节点的关联图
    queryNode(label, id) {
      console.log('queryNode', label, id);
      axios.post(this.queryNodeServer, { 'type': label, 'id': id })
        .then(response => {
          this.org_data = response.data;
          // console.log('queryNode data', this.org_data);
          this.update(this.org_data)
        })
        .catch(error => {
          console.error(error);
        });
    },
    // 查询某类型的节点
    queryNodeOfType(label) {
      console.log('queryNodeOfType', label);
      axios.post(this.queryNodeOfTypeServer, { 'type': label })
        .then(response => {
          this.org_data = response.data;
          // console.log('queryNodeOfType data', this.org_data);
          this.update(this.org_data)
        })
        .catch(error => {
          console.error(error);
        });
    },
    // 关键词匹配
    queryNodeOfKeywords(keywords, range, condition) {
      console.log('queryNodeOfKeywords', keywords);
      axios.post(this.queryNodeOfKeywordsServer, { 'keywords': keywords, 'range': range, 'condition': condition })
        .then(response => {
          if (response.data.length != 0) {
            this.org_data = response.data;
            // console.log('queryNodeOfKeywords data', response.data);
            this.update(this.org_data)
            this.$message({
              message: '查询成功，共查询到' + this.data.nodes.length + '条',
              type: 'success',
            })
          }
          else {
            this.$message({
              message: '未查询到结果',
              type: 'warning',
            })
          }
        })
        .catch(error => {
          console.error(error);
        });
    },
    // 使用预置关键词相似度过滤项目
    queryProjectOfPresetKeywordSim(keyword, threshhold) {
      console.log('queryProjectOfPresetKeywordSim', keyword);
      axios.post(this.queryProjectOfKeywordSimServer, { 'keyword': keyword, 'threshhold': threshhold })
        .then(response => {
          if (response.data.length != 0) {
            this.org_data = response.data;
            this.update(this.org_data)
            this.$message({
              message: '查询成功，共查询到' + this.data.nodes.length + '条',
              type: 'success',
            })
          }
          else {
            this.$message({
              message: '未查询到结果',
              type: 'warning',
            })
          }
        })
        .catch(error => {
          console.error(error);
        });
    },
    // 查询相似项目
    querySimilarProject(label, id, threshhold) {
      console.log('querySimilarProject', label, id);
      if (label != 'project') {
        this.$message({
          message: '仅支持查询相似项目',
          type: 'warning',
        })
        return
      }
      axios.post(this.querySimilarProjectServer, { 'id': id, 'threshhold': threshhold })
        .then(response => {
          if (response.data.length != 0) {
            this.org_data = response.data;
            this.update(this.org_data)
            this.$message({
              message: '查询成功，共查询到' + this.data.nodes.length + '条',
              type: 'success',
            })
          }
          else {
            this.$message({
              message: '未查询到结果',
              type: 'warning',
            })
          }
        })
        .catch(error => {
          console.error(error);
        });
    },
    // 管理员编辑节点
    editNode(update) {
      console.log('editNode', update);
      axios.post(this.editNodeServer, { 'id': update.id, 'properties': update.properties })
        .then(response => {
          if (response.data == 'success')
            this.$message({
              message: '更新成功',
              type: 'success'
            })
          else
            this.$message({
              message: '更新失败',
              type: 'error'
            })
        })
        .catch(error => {
          console.error(error);
        });
    }
  }
}
</script>

<style scoped>
.gContainer {
  height: 99%;
  position: relative;
  border: 2px #000 solid;
  background-color: #9dadc1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
</style>

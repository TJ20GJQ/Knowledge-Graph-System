<template>
  <!-- 绘制关键词搜索 -->
  <div id="keyword">
    <el-button @click="wannaSearch = !wannaSearch" circle>
      <el-icon>
        <Search />
      </el-icon>
    </el-button>
    <el-input v-show="wannaSearch" v-model="keywordsAll" @keyup.enter="keywordsSearchAll"
      style="width: 300px;margin-left: 15px;" placeholder="多关键词查找，如：多智能体 小车" />
  </div>
  <!-- 绘制预置关键词搜索 -->
  <div id="presetKeyword">
    <el-button @click="wannaSearchPreset = !wannaSearchPreset" circle>
      <el-icon>
        <Star />
      </el-icon>
    </el-button>
    <el-select v-show="wannaSearchPreset" v-model="presetKeyword" placeholder="选择预置关键词"
      style="width: 300px;margin-left: 15px;" @change="presetKeywordSimFilter">
      <el-option v-for="(item, i) in presetKeywordList" :key="i" :label="item" :value="item" />
    </el-select>
  </div>
  <!-- 已查询到的结果内部关键词搜索 -->
  <div id="innerkeyword">
    <el-button @click="wannaInnerSearch = !wannaInnerSearch" circle>
      <el-icon>
        <Aim />
      </el-icon>
    </el-button>
    <el-input v-show="wannaInnerSearch" v-model="keywords" @keyup.enter="searchKeyWords"
      style="width: 300px;margin-left: 15px;" placeholder="请输入文字搜索内容" />
  </div>
  <!-- 绘制设置选择 -->
  <div id="setting">
    <el-button @click="wannaSetting = !wannaSetting" circle>
      <el-icon>
        <Setting />
      </el-icon>
    </el-button>
    <div class="settingState" v-show="wannaSetting" style="max-width: 600px">
      <el-scrollbar height="460px">
        <el-form :model="settings" label-width="auto" label-position='right'>
          <el-form-item label="关系名称显示">
            <el-switch v-model="settings.textState" active-text="显示" inactive-text="隐藏" @click="changeTextState" />
          </el-form-item>
          <el-form-item label="关键词查找范围">
            <el-select v-model="settings.searchRange" multiple collapse-tags placeholder="Select">
              <el-option v-for="(item, i) in searchRangeList" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="预置关键词相似度阈值">
            <el-input-number v-model="settings.keywordThreshhold" :step="0.05" :min="0" :max="1" />
          </el-form-item>
          <el-form-item label="项目相似度阈值">
            <el-input-number v-model="settings.similarityThreshhold" :step="0.01" :min="0" :max="1" />
          </el-form-item>
        </el-form>
        <el-divider>条件查询</el-divider>
        <el-form :model="settings" label-width="auto" label-position='right'>
          <el-form-item v-for="(item, i) in Object.keys(searchConditions)" :label="item">
            <el-select v-model="settings.condition[item]" placeholder="Select" multiple collapse-tags
              collapse-tags-tooltip>
              <el-option v-for="(opt, i) in searchConditions[item]" :key="opt" :label="opt" :value="opt" />
            </el-select>
          </el-form-item>
        </el-form>
      </el-scrollbar>
    </div>

  </div>
  <!-- 绘制图例 -->
  <div id="indicator">
    <el-button @click="wannaInfo = !wannaInfo" circle style="margin-top: 8px;">
      <el-icon>
        <InfoFilled />
      </el-icon>
    </el-button>
    <div class="indicatorInfo" v-show="wannaInfo">
      <!-- 利用item 遍历一个数组 利用index 遍历另外一个数组 -->
      <div v-for="(name, index) in names" :key="index" @click="queryNodeOfType(index)" style="cursor: pointer;">
        <span :style="{ backgroundColor: colors[index] }"></span>
        {{ name + '（' + labelNums[index] + '）' }}
      </div>
    </div>
    <div class="graphInfo" v-show="wannaInfo">
      <el-row>
        <el-statistic title="节点个数" :value="nodes.length" />
      </el-row>
      <el-row>
        <el-statistic title="关系个数" :value="links.length" />
      </el-row>
    </div>
  </div>
  <!-- 绘制知识图谱 -->
  <svg id="svg" width="1400" height="750"></svg>
  <!-- 刷新加载节点 -->
  <div id="refresh" v-if="data.nodes.length > maxNodeShow">
    <el-button type="primary" @click="refreshNodes">换一批
      <el-icon style="margin-left: 8px;">
        <Refresh />
      </el-icon>
    </el-button>
  </div>
  <!-- 绘制右边显示结果 -->
  <div id="info" v-show="selectNodeData.name !== undefined">
    <el-card class="node-card" :style="{ backgroundColor: selectNodeData.color }">
      <div slot="header" class="clearfix">
        <el-button @click="btnEdit" style="float: right; padding: 3px 0;color: #409EFB;font-size: 15px;" link>编辑<el-icon
            style="margin-left: 5px;">
            <Edit />
          </el-icon></el-button>
      </div>
      <div v-for="(item, key) in selectNodeData.properties" :key="key">
        <span style="margin-right: 8px;">{{ (nodeObjMap[key] ? nodeObjMap[key] : key) + ':' }}</span>
        <span style="font-weight: bold;">{{ item }}</span>
      </div>
    </el-card>
  </div>
  <!-- 编辑框 -->
  <el-dialog v-model="dialogFormVisible">
    <el-form :model="temp" label-position="right" label-width="86px" style="width: 500px; margin-left:50px;">
      <el-form-item v-for="(value, key) in temp" :key="key" :label="nodeObjMap[key] ? nodeObjMap[key] : key">
        <el-input v-model="temp[key]" :readonly="!isEdit" />
      </el-form-item>
    </el-form>
    <div slot="footer" class="dialog-footer">
      <el-button @click="cancelEdit">
        取消
      </el-button>
      <el-button type="primary" @click="doEdit">
        确定
      </el-button>
    </div>
  </el-dialog>
</template>

<script>
import * as d3 from 'd3'
import install from '@/plugins/d3-context-menu'
import axios from 'axios'
import { reactive, ref } from 'vue'
import { Search, Aim, Setting, InfoFilled, Edit, Star, Refresh } from '@element-plus/icons-vue'
install(d3) // 为d3注册右键菜单插件
export default {
  name: 'd3graph',
  emits: ['queryExpandEvent',
    'queryNodeEvent',
    'queryNodeOfTypeEvent',
    'queryNodeOfKeywordsEvent',
    'queryProjectOfPresetKeywordSimEvent',
    'querySimilarProjectEvent',
    'editNodeEvent'],
  components: {
    Search,
    Aim,
    Setting,
    InfoFilled,
    Edit,
    Star,
    Refresh
  },
  props: {  // 验证传入的 props 参数的数据规格，如果不符合数据规格，Vue 会发出警告
    data: {
      type: Object,
      default: function () {
        return {
          nodes: [],
          links: []
        }
      }
    },
    // 自定义图例（数组保证一一对应）
    // names		图例名称变量制作图标
    // labels		节点的标签名称
    names: Array,
    labels: Array,
    sizes: Array,  // 节点大小
    linkTypes: Array,  // 关系的标签名称
  },
  data() {
    return {
      svgDom: null, // svg的DOM元素 => d3.select('#svg1')
      wannaSearch: ref(true),  // 为true显示搜索框
      searchRangeList: ['学生', '教师', '项目名称', '项目简介'],  // 关键字查询范围
      searchConditions: {},  // 关键词查询可设置的条件
      keywordsAll: '',  // 数据库进行关键词匹配
      wannaSearchPreset: ref(false),  // 为true显示预置关键词搜索框
      presetKeywordList: [],  // 预置关键词
      presetKeyword: '',  // 数据库进行预置关键词查询和排序
      wannaInnerSearch: ref(false),  // 为true显示内部搜索框
      keywords: '',  // 当前查询的节点中进行关键词查找
      wannaSetting: ref(false),  // 为true显示设置
      settings: reactive({
        textState: true,  // 文本状态，表示是否显示文本信息（true：显示/false：不显示）
        keywordThreshhold: 0.5,  // 预置关键词查询阈值
        similarityThreshhold: 0.85,  // 项目相似度阈值
        searchRange: ['项目名称', '项目简介'],  // 选择关键字查询范围
        condition: {}
      }),
      wannaInfo: ref(true),  // 为true显示节点、关系等信息
      labelNums: [],  // 各标签节点数量
      // d3render()最终展示到页面上的数据（节点隐藏功能）
      nodes: [],
      links: [],
      // 自定义图例及颜色（数组保证一一对应）
      // colors		图例颜色（9个颜色）
      colors: ['#55cccc', '#aaaaff', '#4e88af', '#ca635f', '#FFC0CB', '#BA55D3', '#1E90FF', '#7F5FD4', '#FF4F00'],
      selectNodeData: reactive({}), // 选中节点的详细信息展示
      isNodeClicked: false, // 是否点击（选中）节点
      // 用于位置、大小矫正（暂不使用）
      // svgTranslate: [240, 130],
      // svgScale: 0.5,
      // 右击事件的菜单栏
      menu: [
        {
          title: '隐藏节点',
          action: (elm, d) => {
            console.log('隐藏节点', d)
            // 遍历删除节点
            this.nodes = this.nodes.filter(node => {
              if (node.id === d.id) return false
              else return true
            })
            // 遍历删除关系
            this.links = this.links.filter(link => {
              if (link.source.id === d.id || link.target.id === d.id) return false
              else return true
            })
            this.d3render() // 重新渲染图
            this.stateInit()
          },
          disabled: false // optional, defaults to false
        },
        {
          title: '显示节点关联图',
          action: (elm, d) => {
            console.log('显示节点关联图', d)
            // 遍历保留对应节点
            this.nodes = this.data.nodes.filter(node => {
              if (node.id === d.id) return true
              else {
                for (var i = 0; i < this.data.links.length; i++) {
                  if (this.data.links[i].source.id === node.id && this.data.links[i].target.id === d.id) {
                    return true
                  }
                  if (this.data.links[i].target.id === node.id && this.data.links[i].source.id === d.id) {
                    return true
                  }
                }
                return false
              }
            })
            // 遍历保留节点的关联关系
            this.links = this.data.links.filter(link => {
              if (link.source.id === d.id || link.target.id === d.id) return true
              else return false
            })
            this.d3render() // 重新渲染图
            this.stateInit()
          },
          disabled: false
        },
        {
          title: '显示所有查询节点',
          action: (elm, d) => {
            this.nodes = this.data.nodes
            this.links = this.data.links
            this.d3render() // 重新渲染图
            this.stateInit()
          },
          disabled: false
        },
        {
          title: '展开节点',
          action: (elm, d) => {
            this.$emit("queryExpandEvent", d.label, d.id)  // 发起事件，获取新数据
          },
          disabled: false
        },
        {
          title: '查询节点关联图',
          action: (elm, d) => {
            this.$emit("queryNodeEvent", d.label, d.id)  // 发起事件，获取新数据
          },
          disabled: false
        },
        {
          title: '查找相似',
          action: (elm, d) => {
            this.$emit("querySimilarProjectEvent", d.label, d.id, this.settings.similarityThreshhold)  // 发起事件，获取新数据
          },
          disabled: false
        },
      ],
      temp: {}, // 临时存储编辑时的节点信息
      dialogFormVisible: ref(false),  // 是否显示编辑框
      isEdit: false,  // 是否允许编辑
      nodeObjMap: {  // 节点属性对应的标签名称
        'name': '名称'
      },
      // 设置超参数
      delay: 200,  // 鼠标进入节点后的选择延迟，防止选择乱跳，提高稳定性
      maxNodeShow: 30,  // 最多展示的节点数
      nodeIDPointer: 0  // 标记目前节点展示到哪里
    }
  },
  computed: {
    //图密度
    gDensity() {
      return this.nodes.length <= 1 ? 0 : (this.links.length / (this.nodes.length * (this.nodes.length - 1))).toFixed(2)
    },
    //平均度数
    gDegree() {
      return (this.links.length / this.nodes.length).toFixed(2)
    },
    // 稀疏度
    gSparsity() {
      return (this.links.length / (this.nodes.length * Math.log(this.nodes.length))).toFixed(2)
    }
  },
  watch: {
    // 当请求到新的数据时，重新渲染
    data(newData, oldData) {
      console.log('@newData:', newData)
      console.log('@oldData', oldData);
      // 移除svg和元素注册事件，防止内存泄漏
      this.svgDom.on('.', null)
      this.svgDom.selectAll('*').on('.', null)
      this.d3init()
    }
  },
  created() {
    // 加载绘制页面需要的信息
    axios.get("http://127.0.0.1:5000/queryInfo")
      .then(response => {
        this.labelNums = this.labels.map(item => response.data.node_count[item])
        this.presetKeywordList = response.data.presetKeywords
        this.searchConditions = response.data.searchCondition
        for (let i in this.searchConditions) {
          this.settings.condition[i] = []
        }
      })
      .catch(error => {
        console.error(error);
      });
    // 管理员可进行编辑
    if (localStorage.getItem('ms_username') === 'admin')
      this.isEdit = true
  },
  mounted() {
    this.d3init()
  },
  beforeDestroy() {
    // 移除svg和元素注册事件，防止内存泄漏
    this.svgDom.on('.', null)
    this.svgDom.selectAll('*').on('.', null)
  },
  methods: {
    // 编辑当前选中节点
    btnEdit() {
      this.temp = Object.assign({}, this.selectNodeData.properties) // copy obj
      this.dialogFormVisible = true
      console.log('selectEditNodeData:', this.selectNodeData)
    },
    doEdit() {
      if (this.isEdit) {
        // 更新selectNodeData、this的data和props的data
        this.selectNodeData.name = this.temp.name
        this.selectNodeData.properties = this.temp
        for (let i = 0; i < this.nodes.length; i++) {
          if (this.nodes[i].id == this.selectNodeData.id) {
            this.nodes[i].properties = this.temp
            break
          }
        }
        for (let i = 0; i < this.data.nodes.length; i++) {
          if (this.data.nodes[i].id == this.selectNodeData.id) {
            this.data.nodes[i].properties = this.temp
            break
          }
        }
        this.$emit("editNodeEvent", this.selectNodeData)
        this.dialogFormVisible = false
        this.d3init()
        console.log('doEdit', this.selectNodeData);
      }
      else {
        this.$message({
          message: '无管理员权限',
          type: 'warning'
        })
      }
    },
    cancelEdit() {
      this.dialogFormVisible = false
    },
    // 隐藏文字
    changeTextState() {
      // state发生变化时才进行更新、处理
      const text = d3.selectAll('.linkTexts text')
      console.log(text)
      // 根据新的节点状态，在节点上展示不同的文本信息
      if (!this.settings.textState) {
        text.style('display', 'none')
        // 暂不作校准
        // // transform属性数值化
        // // 原：translate(40, 8) scale(1)
        // // 现：[40, 8, 1]
        // let transform = d3.select('#svg1 g').attr('transform')
        // transform = transform
        //   ? transform.match(/\d.?/g).map(item => parseInt(item))
        //   : [0, 0, 1]
        // // 校准
        // transform[0] = transform[0] + this.svgTranslate[0]
        // transform[1] = transform[1] + this.svgTranslate[1]
        // transform[2] = transform[2] * this.svgScale

        // console.log(transform)
        // // 隐藏节点后，svg自动缩放
        // d3.select('#svg1 g').attr('transform', 'translate(' + transform[0] + ', ' + transform[1] + ') scale(' + transform[2] + ')')
      } else {
        text.style('display', 'block')
        // 暂不作校准
        // 显示节点后，svg自动还原
        // d3.select('#svg1 g').attr('transform', '')
      }
    },
    // 刷新加载其他节点
    refreshNodes() {
      let obj = this.deepClone(this.data)  // 深拷贝
      if (this.nodeIDPointer == this.data.nodes.length) {
        this.nodeIDPointer = this.maxNodeShow
      }
      else if (this.nodeIDPointer + this.maxNodeShow > this.data.nodes.length) {
        this.nodeIDPointer = this.data.nodes.length
        this.$message({
          message: '已经查询到底啦 ~',
          type: 'warning',
        })
      }
      else {
        this.nodeIDPointer = this.nodeIDPointer + this.maxNodeShow
      }
      this.nodes = obj.nodes.slice(this.nodeIDPointer - this.maxNodeShow, this.nodeIDPointer)
      var nodes_id = this.nodes.map(item => item.id)
      this.links = []
      for (let i = 0; i < this.data.links.length; i++) {
        if (nodes_id.includes(this.data.links[i].source) && nodes_id.includes(this.data.links[i].target)) {
          this.links.push(this.data.links[i])
        }
      }
      this.d3render()
    },
    // 查询某一类型的节点
    queryNodeOfType(index) {
      this.$emit("queryNodeOfTypeEvent", this.labels[index])
    },
    // 查询关键词
    keywordsSearchAll() {
      this.$emit("queryNodeOfKeywordsEvent", this.keywordsAll, this.settings.searchRange, this.settings.condition)
    },
    // 根据预置关键词相似度查询项目
    presetKeywordSimFilter() {
      if (this.presetKeyword != '')
        this.$emit("queryProjectOfPresetKeywordSimEvent", this.presetKeyword, this.settings.keywordThreshhold)
    },
    // 搜索包含关键字的节点
    searchKeyWords() {
      // 如果Input值是空的显示所有的圆和线(没有进行筛选)
      if (this.keywords === '') {
        this.clearGraphStyle()
      }
      // 否则判断判断三个元素是否等于name值，等于则显示该值
      else {
        var name = this.keywords
        // 搜索所有的节点
        this.svgDom.select('.nodes').selectAll('circle').attr('class', d => {
          // 输入节点id的小写等于name则显示，否则隐藏
          if (d.properties.name.indexOf(name) >= 0) {
            return 'fixed'
          } else {
            // 优化：与该搜索节点相关联的节点均显示
            // links链接的起始节点进行判断,如果其id等于name则显示这类节点
            // 注意: graph=data
            for (var i = 0; i < this.links.length; i++) {
              // 如果links的起点等于name，并且终点等于正在处理的则显示
              if ((this.links[i]['source'].properties.name.indexOf(name) >= 0) &&
                (this.links[i]['target'].id == d.id)) {
                return 'active'
              }
              // 如果links的终点等于name，并且起点等于正在处理的则显示
              if ((this.links[i]['target'].properties.name.indexOf(name) >= 0) &&
                (this.links[i]['source'].id == d.id)) {
                return 'active'
              }
            }
            return 'inactive' // 隐藏
          }
        })
        // 搜索texts
        this.svgDom.select('.texts').selectAll('text').attr('class', d => {
          if (d.properties.name.indexOf(name) >= 0) {
            return ''
          } else {
            // 优化：与该搜索节点相关联的节点均显示
            // links链接的起始节点进行判断,如果其id等于name则显示这类节点
            for (var i = 0; i < this.links.length; i++) {
              // 如果links的起点等于name，并且终点等于正在处理的则显示
              if ((this.links[i]['source'].properties.name.indexOf(name) >= 0) &&
                (this.links[i]['target'].id == d.id)) {
                return ''
              }
              //如果links的终点等于name，并且起点等于正在处理的则显示
              if ((this.links[i]['target'].properties.name.indexOf(name) >= 0) &&
                (this.links[i]['source'].id == d.id)) {
                return ''
              }
            }
            return 'inactive'
          }
        })
        // 搜索links
        // 显示相的邻边 注意 || 
        this.svgDom.select(".links").selectAll('line').attr('class', d => {
          if ((d.source.properties.name.indexOf(name) >= 0) ||
            (d.target.properties.name.indexOf(name) >= 0)
          ) {
            return ''
          } else {
            return 'inactive' //隐藏
          }
        })
        // 搜索linkTexts
        this.svgDom.select(".linkTexts").selectAll('text').attr('class', d => {
          if ((d.source.properties.name.indexOf(name) >= 0) ||
            (d.target.properties.name.indexOf(name) >= 0)
          ) {
            return ''
          } else {
            return 'inactive' //隐藏
          }
        })
      }
    },
    // d3初始化，包括数据解析、数据渲染
    d3init() {  // 若节点数量少于max，则直接赋值
      let obj = this.deepClone(this.data)  // 深拷贝
      if (this.data.nodes.length <= this.maxNodeShow) {
        this.links = obj.links
        this.nodes = obj.nodes
        this.nodeIDPointer = this.data.nodes.length
      }
      else {  // 若节点数量多于max，则取前max个节点，并找到这些节点之间的关系
        this.nodes = obj.nodes.slice(0, this.maxNodeShow)
        var nodes_id = this.nodes.map(item => item.id)
        this.links = []
        for (let i = 0; i < this.data.links.length; i++) {
          if (nodes_id.includes(this.data.links[i].source) && nodes_id.includes(this.data.links[i].target)) {
            this.links.push(this.data.links[i])
          }
        }
        this.nodeIDPointer = this.maxNodeShow
      }
      this.svgDom = d3.select('#svg')  // 获取id为svg的DOM元素
      this.d3render()
      this.stateInit()  // 数据状态初始化
    },
    // 数据状态初始化
    stateInit() {
      this.textState = true
    },
    d3render() {
      var _this = this // 临时获取Vue实例，避免与d3的this指针冲突

      // 渲染前清空svg内的元素
      _this.svgDom.selectAll('*').remove()

      var svg = _this.svgDom
        .on('click', () => {
          this.isNodeClicked = false
          console.log('svg is clicked')
          this.clearGraphStyle()  // 移除所有样式
          this.selectNodeData = {}
          // 如果此时有搜索关键字，则鼠标离开时保留原搜索选中的节点
          if (this.keywords !== '') {
            this.searchKeyWords()
          }
        })
        // 给画布绑定zoom事件（缩放、平移）
        .call(d3.zoom().on('zoom', event => {
          // console.log('zoom:', event)
          var scale = event.transform.k,
            translate = [event.transform.x, event.transform.y]

          // if (this.svgTranslate) {
          //     translate[0] += this.svgTranslate[0]
          //     translate[1] += this.svgTranslate[1]
          // }

          // if (this.svgScale) {
          //     scale *= this.svgScale
          // }

          svg.attr('transform', 'translate(' + translate[0] + ', ' + translate[1] + ') scale(' + scale + ')');
        }))
        .append('g')  // 在SVG中添加一个<g>元素
        .attr('width', '100%')
        .attr('height', '100%')

      this.addMarkers()
      // console.log(svg)
      // 动态变化时，不再固定宽高
      // var width = svg.attr("width"),
      //     height = svg.attr("height")

      // 定义碰撞检测模型
      var forceCollide = d3.forceCollide()
        .radius(d => { return 16 * 3 })  // 设置每个节点的排斥半径
        .iterations(0.15)  // 设置每次应用力导向图布局算法时的迭代次数
        .strength(0.75)  // 设置排斥力的强度

      // 利用d3.forceSimulation()定义关系图 包括设置边link、排斥电荷charge、关系图中心点
      var simulation = d3.forceSimulation(this.nodes)
        .force("link", d3.forceLink().id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-100))
        .force("center", d3.forceCenter(svg.node().parentElement.clientWidth / 2, svg.node().parentElement.clientHeight / 2))
        .force("collision", forceCollide)

      // D3映射数据至HTML中
      // g用于绘制所有边,selectALL选中所有的line,并绑定数据data(graph.links),enter().append("line")添加元素
      // 数据驱动文档,设置边的粗细
      var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(this.links).enter()
        .append("line")
        .attr("stroke-width", function (d) {
          // 每次访问links的一项数据
          return 2 //所有线宽度均为2
        })
        // .join("path")
        .attr("marker-end", "url(#posMarker)")

      var linksName = svg.append("g")
        .attr("class", "linkTexts")
        .selectAll("text")
        .data(this.links)
        .join("text")  // .join()提供了一种更简洁和一致的方式来处理这些阶段，而不需要显式地调用.enter(), .update(), 和 .exit()
        .style('text-anchor', 'middle')
        .style('fill', '#fff')
        .style('font-size', '12px')
        // .style('font-weight', 'bold')
        .text(d => d.properties.name)

      // 添加所有的点
      var timer_node_mouseenter, timer_node_mouseleave;  // 优化延时
      // selectAll("circle")选中所有的圆并绑定数据,圆的直径为d.size
      // 再定义圆的填充色,同样数据驱动样式,圆没有描边,圆的名字为d.id
      // call()函数：拖动函数,当拖动开始绑定dragstarted函数，拖动进行和拖动结束也绑定函数
      var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(this.nodes).enter()
        .append("circle").attr("r", function (d) {
          // 每次访问nodes的一项数据
          return _this.sizes[_this.labels.indexOf(d.label)]
        })
        .attr("fill", d => {
          for (let i = 0; i < this.labels.length; i++) {
            if (d.label === this.labels[i]) return this.colors[i]
          }
        })  // 指定节点填充颜色
        .attr("stroke", "none")  // 轮廓颜色
        .attr("name", d => d.properties.name)
        .attr("id", d => d.id)
        .call(this.drag(simulation))  // 将拖拽操作应用到整个选择集所有元素上
        .on("click", nodeClick)
        .on('mouseenter', function (event) {
          clearTimeout(timer_node_mouseleave)
          const node = d3.select(this)
          console.log('mouseenternode:', node.attr("name"));
          // node.attr("class", "fixed")
          // node.classed("fixed", true)
          // console.log(node)
          //获取被选中元素的名字
          let name = node.attr("name")
          let id = node.attr("id")
          let color = node.attr('fill')
          let properties = null
          //遍历查找id对应的属性
          for (let item of _this.nodes) {
            if (item.id == id) {
              properties = item.properties
              break
            }
          }
          timer_node_mouseenter = setTimeout(function () {
            //设置#info h4样式的颜色为该节点的颜色，文本为该节点name
            _this.selectNodeData['id'] = id
            _this.selectNodeData['name'] = name
            _this.selectNodeData['color'] = color
            _this.selectNodeData['properties'] = properties
            console.log('test', properties);
          }, _this.delay)
          // 遍历节点，并调整图的样式
          _this.changeGraphStyle(id)
        })
        .on('mouseleave', event => {
          clearTimeout(timer_node_mouseenter)
          console.log('mouseleavenode:', _this.selectNodeData['name'])
          if (!this.isNodeClicked) {
            this.clearGraphStyle()
            timer_node_mouseleave = setTimeout(function () {
              _this.selectNodeData = {}
            }, _this.delay)
            // 如果此时有搜索关键字，则鼠标离开时保留原搜索选中的节点
            if (this.keywords !== '') {
              this.searchKeyWords()
            }
          }
        })
        .on('contextmenu', d3.contextMenu(this.menu))
      // .on('contextmenu', function (d, i) {
      //   // 阻止默认右键菜单的弹出
      //   d3.event.preventDefault()
      // })

      // 显示所有的文本
      var timer_text_mouseenter, timer_text_mouseleave;
      // 设置大小、填充颜色、名字、text()设置文本
      // 使用 attr("text-anchor", "middle")设置文本居中
      var text = svg.append("g")
        .attr("class", "texts")
        .selectAll("text")
        .data(this.nodes)
        .enter()
        .append("text").attr("font-size", () => 13)
        .attr("fill", () => '#fff')  // 节点字体颜色
        .attr('name', d => d.properties.name)
        .attr("id", d => d.id)
        .attr("text-anchor", "middle")
        .attr('x', function (d) {
          return textBreaking(d3.select(this), d.properties.name)
        })
        .call(this.drag(simulation))
        .on("click", nodeClick)
        .on('mouseenter', function (event) {
          clearTimeout(timer_text_mouseleave)
          const text = d3.select(this)
          console.log("mouseentertext:", text.attr("name"))
          // 获取被选中元素的名字
          let name = text.attr("name")
          let id = text.attr('id')
          let color = null
          let properties = null

          for (let item of _this.nodes) {
            if (item.id == id) {
              properties = item.properties
              // 根据节点类型label获取节点颜色
              for (let i = 0; i < _this.labels.length; i++) {
                if (item.label === _this.labels[i]) {
                  color = _this.colors[i]
                  break
                }
              }
              break
            }
          }
          timer_text_mouseenter = setTimeout(function () {
            _this.selectNodeData['name'] = name
            _this.selectNodeData['id'] = id
            _this.selectNodeData['properties'] = properties
            _this.selectNodeData['color'] = color
          }, _this.delay)
          _this.changeGraphStyle(id)
        })
        .on('mouseleave', (event) => {
          clearTimeout(timer_text_mouseenter)
          console.log("mouseleavetext:", _this.selectNodeData['name'])
          if (!this.isNodeClicked) {  // 鼠标离开后立即清除样式，而属性信息清除添加延时
            this.clearGraphStyle()
            timer_text_mouseleave = setTimeout(function () {
              _this.selectNodeData = {}
            }, _this.delay)
            // 如果此时有搜索关键字，则鼠标离开时保留原搜索选中的节点
            if (this.keywords !== '') {
              this.searchKeyWords()
            }
          }
        })
        .on('contextmenu', d3.contextMenu(this.menu))

      // 圆增加title
      node.append("title").text(d => d.properties.name)

      // simulation中ticked数据初始化并生成图形
      simulation.on("tick", ticked)

      // 添加链接力
      simulation.force("link")
        .links(this.links)
        .distance(d => { // 每一边的长度
          let distance = 20
          switch (d.source.label) {
            case _this.labels[0]: distance += 30; break;
            case _this.labels[1]: distance += 25; break;
            case _this.labels[2]: distance += 22; break;
            default: distance += 20; break;
          }
          switch (d.target.label) {
            case _this.labels[0]: distance += 30; break;
            case _this.labels[1]: distance += 25; break;
            case _this.labels[2]: distance += 22; break;
            default: distance += 20; break;
          }
          return distance * 2
        })

      /****************************************** 
       * 内部功能函数
       * 包括：ticked、文本分隔、节点和文本的点击事件
       */
      // ticked()函数确定link线的起始点x、y坐标 node确定中心点 文本通过translate平移变化
      function ticked() {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y)

        linksName
          .attr('transform', d => {
            let x = Math.min(d.source.x, d.target.x) + Math.abs(d.source.x - d.target.x) / 2
            let y = Math.min(d.source.y, d.target.y) + Math.abs(d.source.y - d.target.y) / 2 - 1
            // tanA = a / b
            // A = arctan(tanA)
            let tanA = Math.abs(d.source.y - d.target.y) / Math.abs(d.source.x - d.target.x)
            let angle = Math.atan(tanA) / Math.PI * 180
            // let angle = Math.atan2(1,1)/Math.PI*180
            // console.log(angle)
            // 第一、二象限额外处理
            if (d.source.x > d.target.x) {
              // 第二象限
              if (d.source.y <= d.target.y) {
                angle = -angle
              }
              // else {  // 第三象限
              //   angle = angle
              // }
            } else if (d.source.y > d.target.y) {
              // 第一象限
              angle = -angle
            }
            return 'translate(' + x + ',' + y + ')' + 'rotate(' + angle + ')'
          })

        node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y)

        text.attr('transform', function (d) {
          let size = 15
          switch (d.label) {
            case _this.labels[0]: break;
            case _this.labels[1]: size = 14; break;
            case _this.labels[2]: size = 13; break;
            default: size = 12; break;
          }
          size -= 5
          return 'translate(' + (d.x - size / 2 + 3) + ',' + (d.y + size / 2) + ')'
        })
      }

      /**
       * 文本分隔（根据字数在当前选择器中分隔三行，超过10字省略）
       * @method textBreaking
       * @param {d3text} 文本对应的DOM对象
       * @param {text} 节点名称的文本值
       * @return {void}
       */
      function textBreaking(d3text, text) {
        const len = text.length
        if (len <= 3) {
          d3text.append('tspan')
            .attr('x', 0)
            .attr('y', 2)
            .text(text)
        } else {
          const topText = text.substring(0, 3)
          const midText = text.substring(3, 7)
          let botText = text.substring(7, len)
          let topY = -16
          let midY = 0
          let botY = 16
          if (len <= 7) {
            topY += 10
            midY += 10
          } else if (len > 10) {
            botText = text.substring(7, 9) + '...'
          }

          d3text.text('')
          d3text.append('tspan')
            .attr('x', 0)
            .attr('y', topY)
            .text(function () {
              return topText
            })
          d3text.append('tspan')
            .attr('x', 0)
            .attr('y', midY)
            .text(function () {
              return midText
            })
          d3text.append('tspan')
            .attr('x', 0)
            .attr('y', botY)
            .text(function () {
              return botText
            })
        }
      }
      // 分别定义节点和文本的点击事件
      // 优化：由于点击前必定触发mouseenter事件，所以不用再去查找节点id
      //      直接根据this.selectNodeData拿到节点信息
      // 优化后：只需定义一个点击事件即可
      function nodeClick(event, d) {
        // console.log('node clicked!')
        // sticked用于固定节点（无法实现节点固定功能）
        // delete d.fx
        // delete d.fy
        // d3.select(this).classed("fixed", true)
        // simulation.alpha(1).restart()

        // 直接通过this.selectNodeData拿到节点信息
        event.cancelBubble = true
        event.stopPropagation() // 阻止事件冒泡

        const name = _this.selectNodeData.name
        console.log('nodeClicked:', name);
        _this.isNodeClicked = true
        _this.changeGraphStyle(_this.selectNodeData.id)

        return false
      }
    },
    // 根据当前节点名称来更改图样式
    changeGraphStyle(id) {
      // 选择#svg1 .nodes中所有的circle，再增加个class
      this.svgDom.select('.nodes').selectAll('circle').attr('class', d => {
        // 节点属性name是否等于name，返回fixed（激活选中样式）
        if (d.id == id) {
          return 'fixed'
        }
        // 当前节点返回空，否则其他节点循环判断是否被隐藏起来(CSS设置隐藏)
        else {
          // links链接的起始节点进行判断,如果其id等于name则显示这类节点
          // 注意: graph = data
          for (var i = 0; i < this.links.length; i++) {
            // 如果links的起点等于name，并且终点等于正在处理的则显示
            if (this.links[i]['source'].id == id && this.links[i]['target'].id == d.id) {
              return 'active'
            }
            if (this.links[i]['target'].id == id && this.links[i]['source'].id == d.id) {
              return 'active'
            }
          }
          return this.isNodeClicked ? 'inactive' : ''
        }
      })
      // 处理相邻的文字是否隐藏
      this.svgDom.select('.texts').selectAll('text')
        .attr('class', d => {
          // 节点属性name是否等于name，返回fixed（激活选中样式）
          if (d.id == id) {
            return ''
          }
          // 当前节点返回空，否则其他节点循环判断是否被隐藏起来(CSS设置隐藏)
          else {
            // links链接的起始节点进行判断,如果其id等于name则显示这类节点
            // 注意: graph = data
            for (var i = 0; i < this.links.length; i++) {
              // 如果links的起点等于name，并且终点等于正在处理的则显示
              if (this.links[i]['source'].id == id && this.links[i]['target'].id == d.id) {
                return ''
              }
              if (this.links[i]['target'].id == id && this.links[i]['source'].id == d.id) {
                return ''
              }
            }
            return this.isNodeClicked ? 'inactive' : ''
          }
        })
      // 处理相邻的边line是否隐藏 注意 || 
      this.svgDom.select(".links").selectAll('line')
        .attr('class', d => {
          if (d.source.id == id || d.target.id == id) {
            return 'active'
          } else {
            return this.isNodeClicked ? 'inactive' : ''
          }
        })
        .attr('marker-end', d => {
          if (d.source.id == id || d.target.id == id) {
            return 'url(#posActMarker)'
          } else {
            return 'url(#posMarker)'
          }
        })
      // 处理相邻的边上文字是否隐藏 注意 || 
      this.svgDom.select(".linkTexts").selectAll('text')
        .attr('class', d => {
          if (d.source.id == id || d.target.id == id) {
            return 'active'
          } else {
            return this.isNodeClicked ? 'inactive' : ''
          }
        })
    },
    clearGraphStyle() {
      // 移除所有样式
      this.svgDom.select('.nodes').selectAll('circle').attr('class', '')
      this.svgDom.select(".texts").selectAll('text').attr('class', '')
      this.svgDom.select('.links').selectAll('line').attr('class', '').attr('marker-end', 'url(#posMarker)')
      this.svgDom.select(".linkTexts").selectAll('text').attr('class', '')
      // d3.select(this).attr('class', '')
    },
    drag(simulation) {
      function dragsubject(event) {
        return simulation.find(event.x, event.y);
      }

      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        // 注释以下代码，使拖动结束后固定节点
        // event.subject.fx = null;
        // event.subject.fy = null;
      }

      return d3.drag()
        .subject(dragsubject)
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    },
    // 绘制关系箭头
    addMarkers() {
      // 定义箭头的标识
      var defs = this.svgDom.append("defs")
      const posMarker = defs.append("marker")
        .attr("id", "posMarker")
        .attr("orient", "auto")
        .attr("stroke-width", 2)
        .attr("markerUnits", "strokeWidth")
        .attr("markerUnits", "userSpaceOnUse")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 31)
        .attr("refY", 0)
        .attr("markerWidth", 12)
        .attr("markerHeight", 12)
        .append("path")
        .attr("d", "M 0 -5 L 10 0 L 0 5")
        .attr('fill', '#e0cac1')
        .attr("stroke-opacity", 0.6);
      const posActMarker = defs.append("marker")
        .attr("id", "posActMarker")
        .attr("orient", "auto")
        .attr("stroke-width", 2)
        .attr("markerUnits", "strokeWidth")
        .attr("markerUnits", "userSpaceOnUse")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 31)
        .attr("refY", 0)
        .attr("markerWidth", 12)
        .attr("markerHeight", 12)
        .append("path")
        .attr("d", "M 0 -5 L 10 0 L 0 5")
        .attr('fill', '#1E90FF')
        .attr("stroke-opacity", 0.6);
      // const negMarker = defs.append("marker")
      //   .attr("id","negMarker")
      //   .attr("orient","auto")
      //   .attr("stroke-width",2)
      //   .attr("markerUnits", "strokeWidth")
      //   .attr("markerUnits", "userSpaceOnUse")
      //   .attr("viewBox", "0 -5 10 10")
      //   .attr("refX", -25)
      //   .attr("refY", 0)
      //   .attr("markerWidth", 12)
      //   .attr("markerHeight", 12)
      //   .append("path")
      //   .attr("d", "M 10 -5 L 0 0 L 10 5")
      //   .attr('fill', '#999')
      //   .attr("stroke-opacity", 0.6);
    },
    // 通用深拷贝函数
    deepClone(target) {
      const map = new WeakMap();
      function isObject(target) {
        return (typeof target === "object" && target) || (typeof target === "function");
      }
      function clone(data) {
        if (!isObject(target)) {
          return;
        }
        if ([Date, RegExp].includes(data.constructor)) {
          return new data.constructor(data);
        }
        if (typeof data === "function") {
          return new Function("return " + data.toString())();
        }
        const exist = map.get(data);
        if (exist) {
          return exist;
        }
        if (data instanceof Map) {
          const result = new Map();
          map.set(data, result);
          data.forEach((val, key) => {
            if (isObject(val)) {
              result.set(key, clone(val));
            } else {
              result.set(key, val);
            }
          });
          return result;
        }
        if (data instanceof Set) {
          const result = new Set();
          map.set(data, result);
          data.forEach(val => {
            if (isObject(val)) {
              result.add(clone(val));
            } else {
              result.add(val);
            }
          });
          return result;
        }
        const keys = Reflect.ownKeys(data);
        const allDesc = Object.getOwnPropertyDescriptors(data);
        const result = Object.create(Object.getPrototypeOf(data), allDesc);
        map.set(data, result);
        keys.forEach(key => {
          const val = data[key];
          if (isObject(val)) {
            result[key] = clone(val);
          } else {
            result[key] = val;
          }
        });
        return result;
      }
      return clone(target);
    },
  }
}
</script>

<style lang="scss">
@import '@/plugins/d3-context-menu';
$opacity: 0.15;
/* 显示的不透明度 */
$activeColor: #1E90FF;

/* 激活的颜色 */
svg {
  margin: 20px 0px;
  // border: 1px #000 solid;
}

/*设置节点及边的样式*/
.links line {
  stroke: #e0cac1b2; // #bbb
  stroke-opacity: 1;

  &.inactive {
    /* display: none !important; */
    opacity: $opacity;
  }

  &.active {
    stroke: $activeColor;
    stroke-width: 3px;
  }

  &.hide {
    display: none !important;
  }
}

.nodes circle {

  // stroke: #000;
  // stroke-width: 1.5px;
  &.fixed {
    // fill: rgb(102, 81, 81);
    stroke: #FFC0CB; // #888;
    stroke-width: 14px;
    stroke-opacity: $opacity + 0.3;
    border: 10px #000 solid;
  }

  &.inactive {
    /* display: none !important; */
    opacity: $opacity;
  }

  &.active {
    stroke: $activeColor;
    stroke-width: 4px;
  }

  &:hover {
    cursor: pointer;
  }

  &.hide {
    display: none !important;
  }
}

.texts text {
  cursor: pointer;
  text-decoration: none;
  user-select: none;

  &:hover {
    cursor: pointer;
  }

  &.inactive {
    /* display: none !important; */
    opacity: $opacity;
  }
}

.linkTexts text {
  stroke: #ecddd8b2; // #bbb
  stroke-opacity: 1;

  &.active {
    stroke: $activeColor;
  }

  &.inactive {
    /* display: none !important; */
    opacity: $opacity;
  }
}
</style>

<style lang="scss" scoped>
@media only screen and (max-width: 1125px) {

  // 媒体查询，当屏幕的最大宽度为1125像素或更小时，ID为info的元素将被隐藏
  #info {
    display: none !important;
  }
}


#keyword {
  position: absolute;
  top: 20px;
  left: 20px;
}

#presetKeyword {
  position: absolute;
  top: 65px;
  left: 20px;
}

#innerkeyword {
  position: absolute;
  top: 110px;
  left: 20px;
}

#setting {
  position: absolute;
  top: 155px;
  left: 20px;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  z-index: 9;

  .settingState {
    margin-left: 15px;
    background-color: var(--el-input-bg-color, var(--el-fill-color-blank));
    border: 1px solid var(--el-border-color);
    border-radius: var(--el-input-border-radius, var(--el-border-radius-base));
    padding: 5px 15px;
    // 过渡效果
    transition: color, background-color .3s;
    -o-transition: color, background-color .3s;
    -ms-transition: color, background-color .3s;
    -moz-transition: color, background-color .3s;
    -webkit-transition: color, background-color .3s;
  }

  .settingState:active,
  .settingState:hover {
    border: 1px solid var(--el-color-primary);
  }
}

/*图例样式*/
#indicator {
  position: absolute;
  left: 20px;
  bottom: 20px;
  display: flex;
  flex-direction: column-reverse;
  justify-content: flex-start;
  align-items: flex-start;
  // z-index: 9;
  text-align: left;
  color: #f2f2f2;
  font-size: 14px;
  font-weight: bold;

  .indicatorInfo div {
    margin-bottom: 6px;
    margin-left: 8px;
  }

  .indicatorInfo span {
    display: inline-block;
    width: 32px;
    height: 16px;
    position: relative;
    top: 2px;
    margin-right: 8px;
  }

  .graphInfo {
    margin-bottom: 20px;
    margin-left: 8px;
  }
}

#refresh {
  position: absolute;
  margin: auto;
  bottom: 0px;
}

/*悬浮节点的info样式*/
#info {
  position: absolute;
  top: 30px;
  right: 30px;
  width: 350px;

  .node-card {
    border: 1px solid #9faecf;
    background-color: #00aeff6b;
    color: #fff;
    text-align: left;
    // 自动开启滚动条
    overflow: auto;
    // 设置最大高度
    max-height: 570px;

    // .el-card__header {
    //   border-bottom: 10px solid #50596d;
    // }
  }
}
</style>

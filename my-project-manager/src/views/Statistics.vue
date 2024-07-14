<template>
    <div class="">
        <div class="crumbs">
            <!-- 面包屑导航 -->
            <el-breadcrumb separator="/">
                <el-breadcrumb-item><el-icon>
                        <CollectionTag />
                    </el-icon> 统计分析</el-breadcrumb-item>
            </el-breadcrumb>
        </div>
        <div class="container">
            <div class="selector">
                <el-form ref="form" :model="userForm" label-width="auto" label-position="top">
                    <el-form-item label="标题">
                        <el-select v-model="userForm.title" placeholder="请选择想要绘制的图表">
                            <el-option v-for="(option, index) in menu" :key="index" :label="option.title"
                                :value="option.title"></el-option>
                        </el-select>
                    </el-form-item>
                    <el-form-item v-for="(param, index) in userOption"
                        :label="formItemShow(param, param.type) ? param.label : ''">
                        <el-select v-if="formItemShow(param, 'select')" v-model="userForm[param.label]"
                            placeholder="请选择">
                            <el-option v-for="(option, index) in param.value" :key="index" :label="option"
                                :value="option"></el-option>
                        </el-select>
                        <el-select v-if="formItemShow(param, 'multiSelect')" v-model="userForm[param.label]" multiple
                            collapse-tags collapse-tags-tooltip placeholder="请选择">
                            <el-option v-for="(option, index) in param.value" :key="index" :label="option"
                                :value="option"></el-option>
                        </el-select>
                        <el-input-number v-if="formItemShow(param, 'number')" v-model="userForm[param.label]"
                            :step="param.step" :min="param.min" :max="param.max" placeholder="0" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="submitForm">Submit</el-button>
                        <el-button @click="resetForm">Reset</el-button>
                    </el-form-item>
                </el-form>
            </div>
            <div class="plot">
                <myPlotly :data="plotlyData"></myPlotly>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import { ref } from 'vue'
import { CollectionTag } from '@element-plus/icons-vue'
import myPlotly from '../components/myPlotly.vue'
import { reactive } from 'vue'
export default {
    name: 'statistics',
    components: {
        CollectionTag,
        myPlotly
    },
    data() {
        return {
            queryMenuServer: "http://127.0.0.1:5000/queryStatisticsMenu",
            queryServer: "http://127.0.0.1:5000/queryStatistics",
            menu: [],  // 全部查询选项
            userForm: reactive({}),  // 用户查询表单
            userOption: reactive([]),  // 某一项查询额外的参数
            plotlyData: reactive([]),  // 用于向画图组件传值
        }
    },
    methods: {
        // 加载菜单
        loadMenu() {
            axios.get(this.queryMenuServer)
                .then(response => {
                    console.log(response.data);
                    this.menu = response.data
                })
                .catch(error => {
                    console.error(error);
                });
        },
        // 表单数据发送给后端
        submitForm() {
            axios.post(this.queryServer, this.userForm)
                .then(response => {
                    console.log(response.data);
                    this.plotlyData = response.data
                })
                .catch(error => {
                    console.error(error);
                });
        },
        // 重新填写表单
        resetForm() {
            this.userForm = {}
            this.userOption = []
        },
        formItemShow(param, type) {
            if (param.condition) {
                return this.userForm[param.condition.label] == param.condition.value && param.type == type
            }
            return param.type == type
        }
    },
    mounted() {  // 页面挂载后获取查询选项
        this.loadMenu()
    },
    watch: {  // 监测是否重新选择
        'userForm.title': function (newVal, oldVal) {
            console.log('select', newVal);
            this.userForm = { 'title': newVal }
            for (let i = 0; i < this.menu.length; i++) {
                if (this.menu[i].title == newVal) {
                    this.userOption = this.menu[i].option
                    if (this.menu[i].option) {
                        for (let j = 0; j < this.userOption.length; j++) {
                            let opt = this.userOption[j]
                            if (opt.default) {
                                this.userForm[opt.label] = opt.default
                            }
                        }
                    }
                    break
                }
            }

        },
    }
}

</script>

<style>
.container {
    display: flex;
    align-items: stretch;
    height: 530px;
}

.selector {
    width: 30%;
    height: 100%;
}

.plot {
    width: 70%;
    height: 100%;
}
</style>

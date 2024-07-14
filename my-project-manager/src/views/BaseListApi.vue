<template>
    <div>
        <div class="crumbs">
            <el-breadcrumb separator="/">
                <el-breadcrumb-item><el-icon>
                        <Operation />
                    </el-icon> API </el-breadcrumb-item>
            </el-breadcrumb>
        </div>
        <div class="container">
            <el-tabs type="border-card">
                <el-tab-pane class='tab' label="Computer Vision">
                    <!-- 选择任务 -->
                    <el-menu class="mission_menu" @select="handleSelectMission">
                        <el-menu-item v-for="(mission, index) in api_missions" :index="mission">
                            <span>{{ mission }}</span>
                        </el-menu-item>
                    </el-menu>

                    <div class="mission_api" v-if="active_mission">
                        <!-- 选择算法API -->
                        <el-select v-model="active_api" class="api_selector" placeholder="选择算法">
                            <el-option v-for="item in apiCSVData.filter((api) => api['任务'] == active_mission)"
                                :value="item['名称']" :label="item['名称']" />
                        </el-select>
                        <!-- 生成调用API的表单 -->
                        <div v-if="active_api">
                            <div class="api_form">
                                <el-form :model="form" label-width="160px" label-position="left">
                                    <el-form-item v-for="(apiKey, index) in active_api_param" :label="apiKey['param']">
                                        <!-- 表单填写类型 -->
                                        <!-- 单选 -->
                                        <el-radio-group v-if="apiKey['type'] == '单选'" v-model="form[apiKey['param']]">
                                            <el-radio v-for="choice in apiKey['option']" :label="choice" />
                                        </el-radio-group>
                                        <!-- 图片上传 -->
                                        <div v-else-if="apiKey['type'] == '上传图片'">
                                            <el-upload v-model:file-list="form[apiKey['param']]" action="#"
                                                :auto-upload="false" list-type="picture-card"
                                                :on-preview="handlePictureCardPreview" :on-remove="handlePictureRemove"
                                                :limit="9 - 9 % Number(apiKey['least'])">
                                                <!-- v-model 可以在组件上使用以实现双向绑定 -->
                                                <el-icon
                                                    v-if="form[apiKey['param']].length < (9 - 9 % Number(apiKey['least']))">
                                                    <Plus />
                                                </el-icon>
                                            </el-upload>
                                            <!-- 图片预览（支持裁剪） 只有最新一张图片支持裁剪（所有图片都可以裁剪目前有BUG）-->
                                            <el-dialog class="previewImgContainer"
                                                v-if="dialogImageIndex == (form[apiKey['param']].length - 1)"
                                                v-model="dialogImageVisible">
                                                <vue-cropper ref="cropper" :src="dialogImageUrl" :ready="readyCropImage"
                                                    :zoom="cropImage" :cropmove="cropImage"
                                                    style="width:100%;height:300px;">
                                                </vue-cropper>
                                                <template #footer>
                                                    <span class="dialog-footer">
                                                        <el-button @click="cancelCropImage">取 消</el-button>
                                                        <el-button type="primary" @click="confirmCropImage">
                                                            确定</el-button>
                                                    </span>
                                                </template>
                                            </el-dialog>
                                            <el-dialog class="previewImgContainer" v-else v-model="dialogImageVisible">
                                                <img class="previewImg" :src="dialogImageUrl">
                                            </el-dialog>
                                        </div>
                                    </el-form-item>
                                </el-form>
                                <!-- 提交表单按钮 -->
                                <div class="submit">
                                    <el-button class="btn-submit" type="primary"
                                        @click="handleSubmitClick">提交</el-button>
                                </div>
                            </div>
                            <!-- 显示响应结果 -->
                            <div class="api_result" v-if="loading_response | Object.keys(response).length"
                                v-loading="loading_response" element-loading-text="等待响应结果...">
                                <el-divider v-if="!loading_response" content-position="center">API响应结果</el-divider>
                                <el-form label-width="160px" label-position="left">
                                    <el-form-item v-for="resType in active_api_response" :label="resType">
                                        <div v-if="resType == '图片'">
                                            <el-image style="height: 100px;width: auto;display: block;margin: 5px;"
                                                fit="contain" v-for="res in response[resType]"
                                                :src="'data:image/jpeg;base64,' + res"
                                                :preview-src-list="['data:image/jpeg;base64,' + res]" />
                                        </div>
                                    </el-form-item>
                                </el-form>
                            </div>

                        </div>

                    </div>

                </el-tab-pane>
                <el-tab-pane label="Natural Language Processing">Config</el-tab-pane>
                <el-tab-pane label="Knowledge Graph">Role</el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import { reactive } from 'vue'
import { Operation, Plus } from '@element-plus/icons-vue'
import VueCropper from "vue-cropperjs";
import "cropperjs/dist/cropper.css";

export default {
    name: "api",
    data() {
        return {
            apiCSVData: [],  // 全部API数据
            api_missions: [],  // set类型，所有任务
            // 用于交互填写表单
            active_mission: "",  // 当前激活的任务
            active_api: "",  // 当前激活算法
            active_api_param: [],  // 该算法需要的参数，用于生成交互填写表单
            active_api_url: "",  // 该算法API URL，用于请求
            active_api_response: [],  // 响应结果
            form: reactive({}),  // 响应式对象，用于绑定用户表单的选择
            // 用于上传图片
            dialogImageUrl: "",  // 预览图片URL
            dialogImageIndex: 0,  // 预览图片是第几张
            dialogImageVisible: false,  // 预览对话框
            exceedLimit: false,  // 是否超出限制数量
            defaultSrc: "",  // 裁剪前图片文件

            fileParam: "",
            response: {},  // 请求返回结果
            loading_response: false  // 是否正在返回结果
        };
    },
    components: {
        Operation,
        Plus,
        VueCropper
    },
    methods: {
        loadCSV(csvLocate) {
            axios.get(csvLocate)
                .then(response => {
                    this.apiCSVData = response.data;
                    this.api_missions = new Set()
                    for (let i = 0; i < this.apiCSVData.length; i++) {
                        this.api_missions.add(this.apiCSVData[i]['任务'])
                    }
                    this.api_missions = Array.from(this.api_missions)
                    console.log('API data loading:', this.apiCSVData);
                    // query传参，用于直接跳转API
                    if (typeof this.$route.query.active_mission != "undefined" && typeof this.$route.query.active_api != "undefined") {
                        this.active_mission = this.$route.query.active_mission;
                        this.active_api = this.$route.query.active_api;
                        this.$route.query.active_mission = undefined;
                        this.$route.query.active_api = undefined;
                    }
                })
                .catch(error => {
                    console.error(error);
                });
        },
        // 选择的任务
        handleSelectMission(index) {
            if (this.active_mission != index) {
                this.active_mission = index;
                this.active_api = "";
                this.active_api_param = [];
                this.active_api_url = "";
                this.active_api_response = [];
                this.response = {};
                this.loading_response = false;
                console.log('Select mission:', index);
            }
        },
        handlePictureRemove(file) {
            console.log('Remove picture:', file.name);
        },
        // 预览（裁剪）图片
        handlePictureCardPreview(file) {
            this.dialogImageUrl = file.url;
            this.dialogImageIndex = this.form['图片'].indexOf(file);
            this.dialogImageVisible = true;
            console.log('Preview:', this.dialogImageIndex);
            console.log('Blob URL:', this.form['图片'][this.dialogImageIndex].url);
            this.defaultSrc = this.form['图片'][this.dialogImageIndex];
        },
        // 准备裁剪图像
        readyCropImage() {
            console.log('Ready to crop.');
        },
        // 裁剪图像
        cropImage() {
            console.log('Cropping.');
        },
        // 确认裁剪
        confirmCropImage() {
            this.$refs.cropper[0].getCroppedCanvas().toBlob((blob) => {
                // 获得画布图像，blob 流提交，并生成新url
                let arr = new Array(blob);
                let file = new File(arr, 'file', { type: blob.type });
                let url = URL.createObjectURL(blob);
                this.form['图片'][this.dialogImageIndex].raw = file;
                this.form['图片'][this.dialogImageIndex].url = url;
                console.log('Confirm crop URL:', url);
            });
            this.dialogImageVisible = false;
        },
        // 取消裁剪
        cancelCropImage() {
            this.form['图片'][this.dialogImageIndex] = this.defaultSrc;
            this.dialogImageVisible = false;
            this.defaultSrc = "";
            console.log('Cancel crop.');
        },
        // 超出图片上传数量限制
        handlePictureExceed() {
            this.exceedLimit = true;
            console.log('Amount exceeded.');
        },
        // 提交表单
        handleSubmitClick(event) {
            // 解决el-button悬停和点击后不失焦的bug，使用blur使BUTTON强制失焦，没有BUTTON则找父节点
            if (event.target.nodeName == "BUTTON") {
                event.target.blur();
            }
            else if (event.target.nodeName == "SPAN") {
                event.target.parentNode.parentNode.blur();
            }

            this.loading_response = true;
            this.fileParam = new FormData(); //创建form对象
            for (var item in this.form) {
                // 注：特殊表单类型参数名需固定
                if (item == "图片") {
                    for (let i = 0; i < this.form[item].length; i++) {
                        this.fileParam.append("file", this.form[item][i]["raw"]);
                        this.fileParam.append("fileName", this.form[item][i]["name"]);
                    }
                }
                else {
                    this.fileParam.append(item, this.form[item])
                }
            }
            console.log('Submit filename:', this.fileParam.getAll('fileName'));

            axios
                .post("http://127.0.0.1:5000" + this.active_api_url, this.fileParam)
                .then((response) => {
                    this.response = response.data;
                    console.log('Response:', this.response);
                    // 以下用于flask后端send_file响应，需设置{ responseType: "blob" }
                    // const blob = new Blob([response.data], { type: 'image/jpeg' });  // blob表示二进制对象
                    // this.imageUrl = URL.createObjectURL(blob);  //为此二进制对象创建一个URL
                    this.loading_response = false;
                })
                .catch((e) => {
                    console.log(e);
                });
        },
    },
    // 启动时加载API数据
    created() {
        this.loadCSV(this.$store.state.baseURL + '/getApiList');
    },
    // 监听
    watch: {
        // 监听API选择active_api，构造表单选项
        active_api: function (newVal, oldVal) {
            if (newVal != "") {
                // 重置表单
                this.form = reactive({});
                this.exceedLimit = false;
                this.active_api_param = this.apiCSVData.filter((api) => api['名称'] == newVal)[0]['参数'];
                for (let i = 0; i < this.active_api_param.length; i++) {
                    if (this.active_api_param[i]['type'] == '上传图片') {
                        this.form[this.active_api_param[i]['param']] = [];
                    }
                    else if (this.active_api_param[i]['type'] == '单选') {
                        this.form[this.active_api_param[i]['param']] = this.active_api_param[i]['option'][0];  // 缺省为第一种选项
                    }
                    else {
                        this.form[this.active_api_param[i]['param']] = "";
                    }
                }
                this.active_api_url = this.apiCSVData.filter((api) => api['名称'] == newVal)[0]['api'];
                this.active_api_response = this.apiCSVData.filter((api) => api['名称'] == newVal)[0]['响应'];
                console.log('Select API:', newVal);
            }
        },
    }
};
</script>

<style scoped>
.tab {
    display: flex;
    /* 暂时有小BUG，上传多张图片会导致菜单栏被挤压 */
}

.mission_menu {
    width: 240px;
}

.mission_api {
    padding-left: 5%;
}

.api_selector {
    width: 300px;
}

.api_form {
    margin-top: 20px;
}

.submit {
    overflow: hidden;
}

.submit .btn-submit {
    float: right;
}

.previewImgContainer .previewImg {
    width: 100%;
    height: 500px;
    object-fit: contain;
}
</style>
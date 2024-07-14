<template>
    <div class="header">
        <!-- 折叠按钮 -->
        <div class="collapse-btn" @click="collapseChage">
            <el-icon v-if="!collapse">
                <Fold />
            </el-icon>
            <el-icon v-else>
                <Expand />
            </el-icon>
        </div>
        <div class="logo">双创项目知识图谱管理系统</div>
        <div class="header-user-icon">
            <!-- 消息中心 -->
            <div class="btn-bell">
                <!-- el-tooltip文字提示 -->
                <el-tooltip effect="dark" :content="message ? `有${message}条未读消息` : `消息中心`" placement="bottom">
                    <router-link to="/tabs">
                        <el-icon class="el-icon-bell">
                            <Bell />
                        </el-icon>
                    </router-link>
                </el-tooltip>
                <!-- 显示消息上的红点 -->
                <span class="btn-bell-badge" v-if="message"></span>
            </div>
            <!-- 用户头像 -->
            <div class="user-avator">
                <img src="../assets/img/img.jpg" />
            </div>
            <!-- 用户名下拉菜单 @command用于指令绑定，调用回调函数-->
            <el-dropdown class="user-name" trigger="click" @command="handleCommand">
                <span class="el-dropdown-link">
                    {{ username }}
                    <el-icon class="el-icon-arrowdown">
                        <ArrowDown />
                    </el-icon>
                </span>
                <!-- 定义了一个下拉菜单的模板片段 -->
                <template #dropdown>
                    <el-dropdown-menu>
                        <!-- _blank表示链接将在新的浏览器窗口或标签中打开 -->
                        <a href="https://github.com/TJ20GJQ?tab=repositories" target="_blank">
                            <el-dropdown-item>项目仓库</el-dropdown-item>
                        </a>
                        <el-dropdown-item divided command="loginout">退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </div>
    <!-- 全屏按钮 -->
    <div class="btn-fullscreen" @click="handleFullScreen">
        <el-button v-if="!fullscreen" type="primary">
            <el-icon size="large">
                <FullScreen />
            </el-icon>
        </el-button>
        <el-button v-else type="danger">
            <el-icon size="large">
                <SwitchButton />
            </el-icon>
        </el-button>
    </div>
</template>
<script>
import { Fold, Expand, Bell, ArrowDown, FullScreen, SwitchButton } from "@element-plus/icons-vue"  //（难点）注：以组件方式导入element-plus图标
import { ref } from 'vue'
export default {
    data() {  //为变量赋值等
        return {
            fullscreen: ref(false),  //全屏按钮
            name: "GJQ",
            message: 2  //未读消息数量，需要从后端获取
        };
    },
    components: {  //组件注册(局部注册)
        Fold,
        Expand,
        Bell,
        ArrowDown,
        FullScreen,
        SwitchButton
    },
    computed: {  //计算属性
        username() {
            let username = localStorage.getItem("ms_username");
            return username ? username : this.name;
        },
        collapse() {
            return this.$store.state.collapse;
        },
    },
    methods: {  //编写js函数
        // 用户名下拉菜单选择事件
        handleCommand(command) {
            if (command == "loginout") {
                localStorage.removeItem("ms_username");
                this.$router.push("/login");
            }
        },
        // 侧边栏折叠
        collapseChage() {
            this.$store.commit("handleCollapse", !this.collapse);
        },
        // 全屏事件，允许ESC退出
        handleFullScreen() {
            let element = document.documentElement;
            if (this.fullscreen)
                document.exitFullscreen();
            else
                element.requestFullscreen();
            this.fullscreen = !this.fullscreen;
        },
        fullScreenEsc() {
            if (!this.checkFull()) {
                this.fullscreen = false
            }
        },
        checkFull() {
            var isFull =
                document.fullscreenElement ||
                document.mozFullScreenElement ||
                document.webkitFullscreenElement;
            //to fix : false || undefined == undefined
            if (isFull === undefined)
                isFull = false;
            return isFull;
        },
    },
    mounted() {  // mounted在模板渲染成html后调用，通常是初始化页面完成后，再对html的dom节点进行一些需要的操作
        if (document.body.clientWidth < 1500) {  //网页可见区域宽 小就折叠起来
            this.$store.commit("handleCollapse", true);
        }
        document.addEventListener("fullscreenchange", this.fullScreenEsc)
    }
};
</script>
<style scoped>
.header {
    position: relative;
    box-sizing: border-box;
    width: 100%;
    height: 70px;
    font-size: 22px;
    color: #fff;
}

.collapse-btn {
    float: left;
    padding: 0 21px;
    cursor: pointer;
    line-height: 70px;
}

.header .logo {
    float: left;
    width: 300px;
    line-height: 70px;
}

.btn-fullscreen {
    position: fixed;
    right: 18px;
    bottom: 3px;
    /* 设置z-index属性为一个比遮挡组件堆叠顺序更高的值 */
    z-index: 100;
    cursor: pointer;
}

/* el-button不同type默认的class */
.btn-fullscreen .el-button--primary,
.el-button--danger {
    padding-left: 6px;
    padding-right: 6px;
}

.header-user-icon {
    float: right;
    padding-right: 50px;
    display: flex;
    height: 70px;
    align-items: center;
}

.btn-bell {
    position: relative;
    width: 30px;
    height: 30px;
    text-align: center;
    border-radius: 15px;
    cursor: pointer;
    top: 5px;
}

.btn-bell-badge {
    position: absolute;
    right: 0;
    top: -2px;
    width: 8px;
    height: 8px;
    border-radius: 4px;
    background: #f56c6c;
    color: #fff;
}

.btn-bell .el-icon-bell {
    color: #fff;
}

.user-name {
    margin-left: 10px;
}

.user-name .el-icon-arrowdown {
    top: 2px;
    margin-left: 3px;
}

.user-avator {
    margin-left: 20px;
}

.user-avator img {
    display: block;
    width: 40px;
    height: 40px;
    border-radius: 50%;
}

.el-dropdown-link {
    color: #fff;
    cursor: pointer;
}
</style>

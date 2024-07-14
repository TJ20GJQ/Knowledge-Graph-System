<template>
    <div class="sidebar">
        <el-menu class="sidebar-el-menu" :default-active="onRoutes" :collapse="collapse" background-color="#324157"
            text-color="#bfcbd9" active-text-color="#20a0ff" unique-opened router>
            <!-- router:是否启用 vue-router 模式。启用该模式会在激活导航时以index作为path进行路由跳转 
                使用default-active来设置加载时的激活项 -->
            <!-- 一级目录 -->
            <template v-for="item in items">
                <!-- 如果有子目录 -->
                <template v-if="item.subs">
                    <el-sub-menu :index="item.index" :key="item.index">
                        <template #title>
                            <el-icon>
                                <component :is="item.icon"></component>
                            </el-icon>
                            <span>{{ item.title }}</span>
                        </template>
                        <!-- 二级目录 -->
                        <template v-for="subItem in item.subs">
                            <template v-if="subItem.subs">
                                <el-sub-menu :index="subItem.index" :key="subItem.index">
                                    <template #title>{{ subItem.title }}</template>
                                    <!-- 三级目录 -->
                                    <el-menu-item v-for="threeItem in subItem.subs" :key="threeItem.index"
                                        :index="threeItem.index">{{
                                        threeItem.title }}</el-menu-item>
                                </el-sub-menu>
                            </template>
                            <template v-else>
                                <el-menu-item :index="subItem.index" :key="subItem.index">{{
                                    subItem.title }}</el-menu-item>
                            </template>
                        </template>
                    </el-sub-menu>
                </template>
                <!-- 如果没有子目录 -->
                <!-- 解决图标消失：去除 <el-menu-item> 下的 template 标签 -->
                <template v-else>
                    <el-menu-item :index="item.index" :key="item.index">
                        <el-icon>
                            <component :is="item.icon"></component>
                        </el-icon>
                        <span>{{ item.title }}</span>
                    </el-menu-item>
                </template>
            </template>
        </el-menu>
    </div>
</template>

<script>
import { HomeFilled, PieChart, List, Notification, StarFilled, Collection, Promotion, Warning, CoffeeCup, Grid } from "@element-plus/icons-vue"
export default {
    components: {
        HomeFilled,
        PieChart,
        List,
        Notification,
        StarFilled,
        Collection,
        Promotion,
        Warning,
        CoffeeCup,
        Grid
    },
    data() {
        return {
            items: [
                {
                    icon: "HomeFilled",
                    index: "dashboard",
                    title: "系统首页"
                },
                {
                    icon: "Grid",
                    index: "2dView",
                    title: "图谱展示"
                },
                // {
                //     icon: "List",
                //     index: "table",
                //     title: "基础表格"
                // },
                // {
                //     icon: "Notification",
                //     index: "tabs",
                //     title: "tab选项卡"
                // },
                // {
                //     icon: "Collection",
                //     index: "3",
                //     title: "表单相关",
                //     subs: [
                //         {
                //             index: "form",
                //             title: "基本表单"
                //         },
                //         {
                //             index: "upload",
                //             title: "文件上传"
                //         }
                //     ]
                // },
                {
                    icon: "StarFilled",
                    index: "statistics",
                    title: "统计分析",
                },
                // {
                //     icon: "PieChart",
                //     index: "charts",
                //     title: "schart图表"
                // },
                // {
                //     icon: "Promotion",
                //     index: "i18n",
                //     title: "国际化功能"
                // },
                // {
                //     icon: "Warning",
                //     index: "7",
                //     title: "错误处理",
                //     subs: [
                //         {
                //             index: "permission",
                //             title: "权限测试"
                //         },
                //         {
                //             index: "404",
                //             title: "404页面"
                //         }
                //     ]
                // },
                // {
                //     icon: "CoffeeCup",
                //     index: "donate",
                //     title: "支持作者"
                // }
            ]
        };
    },
    computed: {
        onRoutes() {
            return this.$route.path.replace("/", "");
        },
        collapse() {
            return this.$store.state.collapse
        }
    }
};
</script>

<style scoped>
.sidebar {
    display: block;
    position: absolute;
    left: 0;
    top: 70px;
    bottom: 0;
    overflow-y: scroll;
}

.sidebar::-webkit-scrollbar {
    width: 0;
}

.sidebar-el-menu:not(.el-menu--collapse) {
    width: 250px;
}

.sidebar>ul {
    height: 100%;
}
</style>

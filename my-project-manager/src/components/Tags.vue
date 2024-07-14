<template>
    <div class="tags" v-if="showTags">
        <ul>
            <li class="tags-li" v-for="(item, index) in tagsList" :class="{ 'active': isActive(item.path) }"
                :key="index">
                <!-- :class基于组件的属性和状态动态地添加类 -->
                <router-link :to="item.path" class="tags-li-title">{{ item.title }}</router-link>
                <el-icon class="el-icon-close" @click="closeTags(index)">
                    <Close />
                </el-icon>
            </li>
        </ul>
        <!-- 标签选项 -->
        <div class="tags-close-box">
            <el-dropdown @command="handleTags">
                <span class="el-dropdown-link">
                    标签选项
                    <el-icon class="el-icon-arrowdown">
                        <ArrowDown />
                    </el-icon>
                </span>
                <template #dropdown>
                    <el-dropdown-menu size="small">
                        <el-dropdown-item command="other">关闭其他</el-dropdown-item>
                        <el-dropdown-item command="all">关闭所有</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </div>
</template>

<script>
import { Close, ArrowDown } from "@element-plus/icons-vue"
export default {
    components: {
        Close,
        ArrowDown
    },
    computed: {
        tagsList() {
            return this.$store.state.tagsList;
        },
        showTags() {
            return this.tagsList.length > 0;
        }
    },
    methods: {
        isActive(path) {  //找到当前所在route，对应标签背景为蓝色，其余设置为白色
            return path === this.$route.fullPath;
        },
        // 关闭单个标签
        closeTags(index) {
            const delItem = this.tagsList[index];
            this.$store.commit("delTagsItem", { index });
            const item = this.tagsList[index]  //切换高亮显示
                ? this.tagsList[index]
                : this.tagsList[index - 1];
            if (item) {
                delItem.path === this.$route.fullPath &&
                    this.$router.push(item.path);  //导航到其他路由
            } else {
                this.$router.push("/");
            }
        },
        // 关闭全部标签
        closeAll() {
            this.$store.commit("clearTags");
            this.$router.push("/");
        },
        // 关闭其他标签
        closeOther() {
            const curItem = this.tagsList.filter(item => {
                return item.path === this.$route.fullPath;
            });
            this.$store.commit("closeTagsOther", curItem);
        },
        handleTags(command) {
            command === "other" ? this.closeOther() : this.closeAll();
        },
        // 设置标签
        setTags(route) {
            console.log(route.fullPath);
            const isExist = this.tagsList.some(item => {  //测试数组中是否有至少一个元素满足提供的测试函数
                return item.path === route.fullPath;
            });
            if (!isExist) {
                if (this.tagsList.length >= 8) {  //标签数量上限8，可改
                    this.$store.commit("delTagsItem", { index: 0 });
                }
                this.$store.commit("setTagsItem", {
                    name: route.name,
                    title: route.meta.title,
                    path: route.fullPath
                });
            }
        }
    },
    watch: {  //使用 watch 选项来监视数据属性的变化，并在变化时执行某些操作
        $route(newValue) {
            this.setTags(newValue);
        }
    },
    created() {  // created 在模板渲染成html前调用，即通常初始化某些属性值，然后再渲染成视图
        this.setTags(this.$route);
    }
};
</script>


<style>
.tags {
    position: relative;
    height: 30px;
    overflow: hidden;
    background: #fff;
    padding-right: 120px;
    box-shadow: 0 5px 10px #ddd;
}

.tags ul {
    box-sizing: border-box;
    width: 100%;
    height: 100%;
}

.tags-li {
    float: left;
    margin: 3px 5px 2px 3px;
    border-radius: 3px;
    font-size: 12px;
    overflow: hidden;
    cursor: pointer;
    height: 23px;
    line-height: 23px;
    border: 1px solid #e9eaec;
    background: #fff;
    padding: 0 5px 0 12px;
    vertical-align: middle;
    color: #666;
    -webkit-transition: all 0.3s ease-in;
    -moz-transition: all 0.3s ease-in;
    transition: all 0.3s ease-in;
}

.tags-li:not(.active):hover {
    /* 只有当前标签有active类 */
    background: #f8f8f8;
}

.tags-li.active {
    color: #fff;
}

.tags-li-title {
    float: left;
    max-width: 80px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin-right: 5px;
    margin-top: 1px;
    color: #666;
}

.tags-li.active .tags-li-title {
    color: #fff;
}

.tags-li .el-icon-close {
    top: 3px;
}

.tags-close-box {
    position: absolute;
    right: 0;
    top: 0;
    box-sizing: border-box;
    text-align: center;
    width: 110px;
    height: 30px;
    background: #fff;
    /* box-shadow: -3px 0 15px 3px rgba(0, 0, 0, 0.1); */
    z-index: 10;
    background-color: var(--el-color-primary);
    user-select: none;
}

.tags-close-box:hover {
    background-color: var(--el-color-primary-light-3);
}

.tags-close-box .el-dropdown-link {
    width: 100%;
    cursor: pointer;
    color: white;
    display: flex;
    align-items: center;
    padding: 8px 17.5px 8px 17.5px;

}

.tags-close-box .el-icon-arrowdown {
    margin-left: 5px;
}
</style>

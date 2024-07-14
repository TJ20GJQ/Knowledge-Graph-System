import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";

const routes = [
    {
        path: '/',
        redirect: '/dashboard'  //路由重定向
    },
    {
        path: "/",
        name: "Home",
        component: Home,
        children: [
            {
                path: "/dashboard",
                name: "dashboard",
                meta: {
                    title: '系统首页'  //meta:路由元信息，可以加上permission添加管理员权限限制
                },
                component: () => import(
                    /* webpackChunkName: "dashboard" */
                    "../views/Dashboard.vue")
            }, {
                path: "/2dView",
                name: "2dView",
                meta: {
                    title: '图谱'
                },
                component: () => import(
                    /* webpackChunkName: "2dView" */
                    "../views/2dView.vue")
            },
            {
                path: "/table",
                name: "basetable",
                meta: {
                    title: '表格'
                },
                component: () => import(
                    /* webpackChunkName: "table" */
                    "../views/BaseTable.vue")
            },
            {
                path: "/charts",
                name: "basecharts",
                meta: {
                    title: '图表'
                },
                component: () => import(
                    /* webpackChunkName: "charts" */
                    "../views/BaseCharts.vue")
            }, {
                path: "/form",
                name: "baseform",
                meta: {
                    title: '表单'
                },
                component: () => import(
                    /* webpackChunkName: "form" */
                    "../views/BaseForm.vue")
            }, {
                path: "/statistics",
                name: "statistics",
                meta: {
                    title: '统计'
                },
                component: () => import(
                    /* webpackChunkName: "statistics" */
                    "../views/Statistics.vue")
            }, {
                path: "/tabs",
                name: "tabs",
                meta: {
                    title: 'tab标签'
                },
                component: () => import(
                    /* webpackChunkName: "tabs" */
                    "../views/Tabs.vue")
            }, {
                path: "/donate",
                name: "donate",
                meta: {
                    title: '鼓励作者'
                },
                component: () => import(
                    /* webpackChunkName: "donate" */
                    "../views/Donate.vue")
            }, {
                path: "/permission",
                name: "permission",
                meta: {
                    title: '权限管理',
                    permission: true  //需要管理员权限
                },
                component: () => import(
                    /* webpackChunkName: "permission" */
                    "../views/Permission.vue")
            }, {
                path: "/i18n",
                name: "i18n",
                meta: {
                    title: '国际化语言'
                },
                component: () => import(
                    /* webpackChunkName: "i18n" */
                    "../views/I18n.vue")
            }, {
                path: "/upload",
                name: "upload",
                meta: {
                    title: '上传插件'
                },
                component: () => import(
                    /* webpackChunkName: "upload" */
                    "../views/Upload.vue")
            }, {
                path: "/icon",
                name: "icon",
                meta: {
                    title: '自定义图标'
                },
                component: () => import(
                    /* webpackChunkName: "icon" */
                    "../views/Icon.vue")
            }, {
                path: '/404',
                name: '404',
                meta: {
                    title: '找不到页面'
                },
                component: () => import(/* webpackChunkName: "404" */
                    '../views/404.vue')
            }, {
                path: '/403',
                name: '403',
                meta: {
                    title: '没有权限'
                },
                component: () => import(/* webpackChunkName: "403" */
                    '../views/403.vue')
            }
        ]
    },
    {
        path: "/login",
        name: "Login",
        meta: {
            title: '登录'
        },
        component: () => import(
            /* webpackChunkName: "login" */
            "../views/Login.vue")
    }
];

const router = createRouter({  //设置为history模式
    history: createWebHistory(process.env.BASE_URL),
    routes
});

//登录校验
//在前端路由跳转中，路由跳转前都是会经过beforeEach，而beforeEach可以通过next来控制到底去哪个路由。
//根据这个特性我们就可以在beforeEach中设置一些条件来控制路由的重定向。
//常见的使用场景有：1、验证用户是否登录（若未登录，且当前非登录页面，则自动重定向登录页面）；2、用户权限；3、用户输入的路路径是否存在，不存在的情况下如何处理，重定向到哪个页面
router.beforeEach((to, from, next) => {
    //参数说明：
    //to: 表示要跳转的路由对象
    //from: 表示跳转前的路由对象
    //next: 继续执行跳转的函数，只有跳转前的拦截才有这个参数
    document.title = `${to.meta.title} | vue-manage-system`;  //设置标签页名称
    const role = localStorage.getItem('ms_username');  //获取指定key本地存储的值
    if (!role && to.path !== '/login') {
        next('/login');
    } else if (to.meta.permission) {
        // 如果是管理员权限则可进入，这里只是简单的模拟管理员权限而已
        role === 'admin'
            ? next()
            : next('/403');
    } else {
        next();
    }
});

export default router;
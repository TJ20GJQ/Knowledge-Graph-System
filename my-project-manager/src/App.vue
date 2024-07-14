<template>
  <router-view />
</template>

<script>
export default {};

// 报错解决：ResizeObserver loop completed with undelivered notifications
// 来源：https://blog.csdn.net/lionet0307/article/details/136369313
const debounce = (fn, delay) => {
  let timer
  return (...args) => {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      fn(...args)
    }, delay)
  }
}

const _ResizeObserver = window.ResizeObserver;
window.ResizeObserver = class ResizeObserver extends _ResizeObserver {
  constructor(callback) {
    callback = debounce(callback, 200);
    super(callback);
  }
}
</script>

<style>
@import "./assets/css/main.css";
@import "./assets/css/color-dark.css";
</style>

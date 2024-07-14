<template>
    <div ref="chart"></div>
</template>

<script>
import Plotly from 'plotly.js-dist-min'

export default {
    name: 'myPlotly',
    props: {
        // data包含data和layout
        data: {
            type: Array,
            required: true
        },
    },
    mounted() {
    },
    methods: {
        drawChart() {
            Plotly.newPlot(this.$refs.chart, this.data[0], this.data[1], { responsive: true });
        }
    },
    watch: {
        // 监听props变化，如果data或layout变化了，重新绘制图表  
        data: {
            handler() {
                this.drawChart();
            },
        },
    }
};
</script>

<style scoped></style>
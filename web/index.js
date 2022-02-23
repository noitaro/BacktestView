const TradingVue = window['TradingVueJs'].TradingVue;

let ohlcv_data = null;
const innerHeightOffset = 231;

var app = new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    components: {
        'trading-vue': TradingVue
    },
    data() {
        return {
            trading_vue: { chart: null, onchart: [], offchart: [] },
            line_chart: {
                labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                datasets: [{ label: 'sample', borderColor: '#0000ff', data: [100, 90, 60, 70, 50, 30, 40, 50, 60, 100], fill: false }]
            },
            options: {
                title: { display: true, text: 'Line chart' }, legend: { display: false },
            },
            timezone: 9,
            dialog1: false,
            dialog2: false,
            dialog3: false,
            dialog4: false,
            loading_ohlcv: false,
            width: window.innerWidth,
            height: window.innerHeight - innerHeightOffset,
            from_date: '2021-12-11',
            to_date: '',
            from_date_menu: false,
            to_date_menu: false,
            timeframe: '1h',
            timeframe_items: ['1m','3m','5m','15m','30m','1h','2h','4h','6h','12h','1d','1w','1M','1y'],
            sheet: false,
            switch_vwma20: { loading: false, isChecked: false },
            switch_vwma25: { loading: false, isChecked: false },
            switch_cci25: { loading: false, isChecked: false },
            switch_bb20: { loading: false, isChecked: false },
            switch_rci9: { loading: false, isChecked: false },
            switch_rci26: { loading: false, isChecked: false },
            switch_rci52: { loading: false, isChecked: false },
            backtest: { module_name: 'strategy1', method_name: 'bb_strategy_directed', loading: false, size: 0.01 },
            desserts: []
        };
    },
    created() {
        const d = new Date();
        // 日付文字列フォーマット (2021-01-01)
        this.to_date = `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`.replace(/\n|\r/g, '');
    },
    methods: {
        async getData_ohlcv() {
            this.loading_ohlcv = true;

            const ohlcv_df = await eel.get_ohlcv(this.timeframe, this.from_date, this.to_date)();
            if (ohlcv_df != null) {
                const ohlcv = JSON.parse(ohlcv_df);
                ohlcv_data = ohlcv;

                const chart_data = get_chart_data(ohlcv.timestamp, [ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume]);
                this.trading_vue.chart = { name: 'BTCUSDT', type: 'Candles', data: chart_data };
            }

            this.loading_ohlcv = false;
        },
        async changed_vwma20() {
            this.switch_vwma20.loading = true;

            array_clear(this.trading_vue.onchart, 'VWMA, 20');

            if (this.switch_vwma20.isChecked) {
                // VWMA 20
                const vwma20_df = await eel.get_vwma(ohlcv_data.timestamp, ohlcv_data.close, ohlcv_data.volume, 20)();
                const vwma20 = JSON.parse(vwma20_df);
                const chart_data = get_chart_data(vwma20.timestamp, [vwma20.vwma]);
                this.trading_vue.onchart.push({ name: 'VWMA, 20', type: 'EMA', data: chart_data });
            }

            this.switch_vwma20.loading = false;
        },
        async changed_vwma25() {
            this.switch_vwma25.loading = true;

            array_clear(this.trading_vue.onchart, 'VWMA, 25');

            if (this.switch_vwma25.isChecked) {
                // VWMA 25
                const vwma25_df = await eel.get_vwma(ohlcv_data.timestamp, ohlcv_data.close, ohlcv_data.volume, 25)();
                const vwma25 = JSON.parse(vwma25_df);
                const chart_data = get_chart_data(vwma25.timestamp, [vwma25.vwma]);
                this.trading_vue.onchart.push({ name: 'VWMA, 25', type: 'EMA', data: chart_data });
            }

            this.switch_vwma25.loading = false;
        },
        async changed_cci25() {
            this.switch_cci25.loading = true;

            array_clear(this.trading_vue.offchart, 'CCI, 25');

            if (this.switch_cci25.isChecked) {

                // CCI 25
                const cci25_df = await eel.get_cci(ohlcv_data.timestamp, ohlcv_data.close, ohlcv_data.close, ohlcv_data.close, 25)();
                const cci25 = JSON.parse(cci25_df);
                const chart_data = get_chart_data(cci25.timestamp, [cci25.cci]);
                this.trading_vue.offchart.push({ name: 'CCI, 25', type: 'SMA', data: chart_data });
            }

            this.switch_cci25.loading = false;
        },
        async changed_bb20() {
            this.switch_bb20.loading = true;

            array_clear(this.trading_vue.onchart, 'BB, 20 UPPER');
            array_clear(this.trading_vue.onchart, 'BB, 20 LOWER');

            if (this.switch_bb20.isChecked) {

                // BB 20
                const bb20_df = await eel.get_bb(ohlcv_data.timestamp, ohlcv_data.close, 20)();
                const bb20 = JSON.parse(bb20_df);
                this.trading_vue.onchart.push({ name: 'BB, 20 UPPER', type: 'SMA', data: get_chart_data(bb20.timestamp, [bb20['BBU_20_2.0']]) });
                this.trading_vue.onchart.push({ name: 'BB, 20 LOWER', type: 'SMA', data: get_chart_data(bb20.timestamp, [bb20['BBL_20_2.0']]) });
            }

            this.switch_bb20.loading = false;
        },
        async changed_rci9() {
            this.switch_rci9.loading = true;

            array_clear(this.trading_vue.offchart, 'RCI, 9');

            if (this.switch_rci9.isChecked) {

                // RCI 9
                const rci9_df = await eel.get_rci(ohlcv_data.timestamp, ohlcv_data.close, 9)();
                const rci9 = JSON.parse(rci9_df);
                const chart_data = get_chart_data(rci9.timestamp, [rci9.cci]);
                this.trading_vue.offchart.push({ name: 'RCI, 9', type: 'SMA', data: chart_data });
            }

            this.switch_rci9.loading = false;
        },
        async changed_rci26() {
            this.switch_rci26.loading = true;

            array_clear(this.trading_vue.offchart, 'RCI, 26');

            if (this.switch_rci26.isChecked) {

                // RCI 26
                const rci26_df = await eel.get_rci(ohlcv_data.timestamp, ohlcv_data.close, 26)();
                const rci26 = JSON.parse(rci26_df);
                const chart_data = get_chart_data(rci26.timestamp, [rci26.cci]);
                this.trading_vue.offchart.push({ name: 'RCI, 26', type: 'SMA', data: chart_data });
            }

            this.switch_rci26.loading = false;
        },
        async changed_rci52() {
            this.switch_rci52.loading = true;

            array_clear(this.trading_vue.offchart, 'RCI, 52');

            if (this.switch_rci52.isChecked) {

                // RCI 52
                const rci52_df = await eel.get_rci(ohlcv_data.timestamp, ohlcv_data.close, 52)();
                const rci52 = JSON.parse(rci52_df);
                const chart_data = get_chart_data(rci52.timestamp, [rci52.cci]);
                this.trading_vue.offchart.push({ name: 'RCI, 52', type: 'SMA', data: chart_data });
            }

            this.switch_rci52.loading = false;
        },
        async run_backtest() {
            this.backtest.loading = true;

            array_clear(this.trading_vue.onchart, this.backtest.method_name);

            if (ohlcv_data == null) {
                this.backtest.loading = false;
                return;
            }

            const result_df = await eel.run_backtest(ohlcv_data, this.backtest.module_name, this.backtest.method_name, this.backtest.size)();
            if (result_df == null) {
                this.backtest.loading = false;
                return;
            }

            const ret = JSON.parse(result_df);
            const chart_data = get_chart_data(ret.timestamp, [ret.type, ret.price, ret.label]);

            this.trading_vue.onchart.push({ name: this.backtest.method_name, type: 'Trades', data: chart_data });

            let desserts = [];
            let total_profit = 0;
            idx = 0;
            while (true) {
                if (ret.timestamp[idx] == null) break;

                total_profit += ret.profit[idx];
                const dessert1 = {
                    'type1': ret.type[idx] == 0 ? 'ショートエントリー' : 'ロングエントリー',
                    'type2': ret.type[idx] == 0 ? 'ショートを決済' : 'ロングを決済',
                    'datetime1': ret.datetime[idx],
                    'datetime2': ret.execution_datetime[idx] ?? 'まだ',
                    'price1': ret.price[idx],
                    'price2': ret.execution_price[idx],
                    'profit': ret.profit[idx],
                    'total_profit': Math.round(total_profit * 1000) / 1000 // 小数点第 4 位で四捨五入
                };
                desserts.push(dessert1);
                idx += 1;
            }


            this.desserts = desserts;

            const linechart_labels = desserts.map(x => x.datetime2);
            const linechart_data = desserts.map(x => x.total_profit);

            Vue.component('line-chart', {
                extends: VueChartJs.Line,
                mounted() {
                    this.renderChart({
                        labels: linechart_labels,
                        datasets: [
                            {
                                label: 'USDT',
                                data: linechart_data
                            }
                        ]
                    }, {
                        responsive: true,
                        maintainAspectRatio: false,
                        elements: {
                            line: {
                                tension: 0
                            }
                        },
                        animation: {
                            duration: 0
                        },
                        hove: {
                            animationDuration: 0
                        },
                        responsiveAnimationDuration: 0
                    })
                }
            });

            this.backtest.loading = false;
        },
        handleResize() {
            this.width = window.innerWidth;
            this.height = window.innerHeight - innerHeightOffset;
        }
    },
    mounted: function () {
        window.addEventListener('resize', this.handleResize);
    },
    beforeDestroy: function () {
        window.removeEventListener('resize', this.handleResize);
    }
});

function array_clear(ary, name) {
    for (let index = 0; index < ary.length; index++) {
        const element = ary[index];
        if (element.name == name) {
            ary.splice(index, 1);
            break;
        }
    }
}

function get_chart_data(timestamp, data) {

    let chart_data = []
    idx = 0;
    while (true) {
        if (timestamp[idx] == null) break;

        let params = [timestamp[idx]];

        if (data != null && data.length >= 1) {
            data.forEach(element => {
                params.push(element[idx]);
            });
        }

        chart_data.push(params);
        idx += 1;
    }

    return chart_data;
}

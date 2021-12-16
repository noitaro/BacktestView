const TradingVue = window['TradingVueJs'].TradingVue;

let ohlcv_data = null;

var app = new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    components: {
        'trading-vue': TradingVue
    },
    data: {
        dialog1: false,
        dialog2: false,
        dialog3: false,
        loading_ohlcv: false,
        chart: null,
        onchart: [],
        offchart: [],
        width: window.innerWidth,
        height: window.innerHeight - 100,
        from_date: '2021-11-01',
        to_date: '',
        from_date_menu: false,
        to_date_menu: false,
        sheet: false,
        switch_vwma20: { loading: false, isChecked: false },
        switch_vwma25: { loading: false, isChecked: false },
        switch_cci25: { loading: false, isChecked: false },
        backtest: { module_name: 'strategy1', method_name: 'bb_strategy_directed', loading: false }
    },
    created() {
        const d = new Date();
        // 日付文字列フォーマット (2021-01-01)
        this.to_date = `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`.replace(/\n|\r/g, '');
    },
    methods: {
        async getData_ohlcv() {
            this.loading_ohlcv = true;

            const ohlcv_df = await eel.get_ohlcv(this.from_date, this.to_date)();
            if (ohlcv_df != null) {
                const ohlcv = JSON.parse(ohlcv_df);
                ohlcv_data = ohlcv;

                const chart_data = get_chart_data(ohlcv.timestamp, [ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume]);
                this.chart = { name: 'BTCUSDT', type: 'Candles', data: chart_data };
            }

            this.loading_ohlcv = false;
        },
        async changed_vwma20() {
            this.switch_vwma20.loading = true;

            array_clear(this.onchart, 'VWMA, 20');

            if (this.switch_vwma20.isChecked) {
                // VWMA 20
                const vwma20_df = await eel.get_vwma(ohlcv_data.timestamp, ohlcv_data.close, ohlcv_data.volume, 20)();
                const vwma20 = JSON.parse(vwma20_df);
                const chart_data = get_chart_data(vwma20.timestamp, [vwma20.vwma]);
                this.onchart.push({ name: 'VWMA, 20', type: 'EMA', data: chart_data });
            }

            this.switch_vwma20.loading = false;
        },
        async changed_vwma25() {
            this.switch_vwma25.loading = true;

            array_clear(this.onchart, 'VWMA, 25');

            if (this.switch_vwma25.isChecked) {
                // VWMA 25
                const vwma25_df = await eel.get_vwma(ohlcv_data.timestamp, ohlcv_data.close, ohlcv_data.volume, 25)();
                const vwma25 = JSON.parse(vwma25_df);
                const chart_data = get_chart_data(vwma25.timestamp, [vwma25.vwma]);
                this.onchart.push({ name: 'VWMA, 25', type: 'EMA', data: chart_data });
            }

            this.switch_vwma25.loading = false;
        },
        async changed_cci25() {
            this.switch_cci25.loading = true;

            array_clear(this.offchart, 'CCI, 25');

            if (this.switch_cci25.isChecked) {

                // CCI 25
                const cci25_df = await eel.get_cci(ohlcv_data.timestamp, ohlcv_data.close, ohlcv_data.close, ohlcv_data.close, 25)();
                const cci25 = JSON.parse(cci25_df);
                const chart_data = get_chart_data(cci25.timestamp, [cci25.cci]);
                this.offchart.push({ name: 'CCI, 25', type: 'SMA', data: chart_data });
            }

            this.switch_cci25.loading = false;
        },
        async run_backtest() {
            this.backtest.loading = true;

            if (ohlcv_data != null) {
                await eel.run_backtest(ohlcv_data, this.backtest.module_name, this.backtest.method_name)();
            }

            this.backtest.loading = false;
        },
        handleResize() {
            this.width = window.innerWidth;
            this.height = window.innerHeight - 100;
        }
    },
    mounted: function () {
        window.addEventListener('resize', this.handleResize)
    },
    beforeDestroy: function () {
        window.removeEventListener('resize', this.handleResize)
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
        data.forEach(element => {
            params.push(element[idx]);
        });

        chart_data.push(params);
        idx += 1;
    }

    return chart_data;
}
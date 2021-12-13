const TradingVue = window['TradingVueJs'].TradingVue;

var app = new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    components: {
        'trading-vue': TradingVue
    },
    data: {
        loading_ohlcv: false,
        disabled_ohlcv: false,
        chart: null,
        onchart: [],
        offchart: [],
        width: window.innerWidth,
        height: window.innerHeight - 100,
        from_date: '2021-11-01',
        to_date: '',
        from_date_menu: false,
        to_date_menu: false
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

                let ohlcvData = []
                let idx = 0;
                while (true) {
                    if (ohlcv.timestamp[idx] == null) break;
                    ohlcvData.push([ohlcv.timestamp[idx], ohlcv.open[idx], ohlcv.high[idx], ohlcv.low[idx], ohlcv.close[idx], ohlcv.volume[idx]]);
                    idx += 1;
                }
                this.chart = { name: 'BTCUSDT', type: 'Candles', data: ohlcvData };

                // VWMA 20
                const vwma20_df = await eel.get_vwma(ohlcv.timestamp, ohlcv.close, ohlcv.volume, 20)();
                const vwma20 = JSON.parse(vwma20_df);
                debugger;
                let vwma20_data = []
                idx = 0;
                while (true) {
                    if (vwma20.timestamp[idx] == null) break;
                    vwma20_data.push([vwma20.timestamp[idx], vwma20.vwma[idx]]);
                    idx += 1;
                }
                this.onchart.push({ name: 'VWMA, 20', type: 'EMA', data: vwma20_data });

                // VWMA 25
                const vwma25_df = await eel.get_vwma(ohlcv.timestamp, ohlcv.close, ohlcv.volume, 25)();
                const vwma25 = JSON.parse(vwma25_df);
                let vwma25_data = []
                idx = 0;
                while (true) {
                    if (ohlcv.timestamp[idx] == null) break;
                    vwma25_data.push([vwma25.timestamp[idx], vwma25.vwma[idx]]);
                    idx += 1;
                }
                this.onchart.push({ name: 'VWMA, 25', type: 'EMA', data: vwma25_data });

                // CCI 25
                const cci25_df = await eel.get_cci(ohlcv.timestamp, ohlcv.close, ohlcv.close, ohlcv.close, 25)();
                const cci25 = JSON.parse(cci25_df);
                let cci25_data = []
                idx = 0;
                while (true) {
                    if (ohlcv.timestamp[idx] == null) break;
                    cci25_data.push([cci25.timestamp[idx], cci25.cci[idx]]);
                    idx += 1;
                }
                this.offchart.push({ name: 'CCI, 25', type: 'SMA', data: cci25_data });
            }

            this.loading_ohlcv = false;
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
})

eel.expose(js_log);
function js_log() {
    console.log('aaa');
    return;
}
const TradingVue = window['TradingVueJs'].TradingVue;

var app = new Vue({
    el: '#app',
    name: 'test',
    vuetify: new Vuetify(),
    components: {
    },
    data() {
        return {}
    },
    methods: {
        resize() {
          console.log('resize')
        }
    }
}).$mount('#app');
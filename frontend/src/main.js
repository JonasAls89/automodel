import Vue from 'vue'
import App from './App'
import VueRouter from 'vue-router'
import Input from './components/NewDbConnect'
import Meta from './components/NewDbConnect'
import Globals from './components/NewGlobals'
import VueDraggable from "vue-draggable";

Vue.config.productionTip = false
Vue.use(VueRouter)
Vue.use(VueDraggable);

const routes = [{
    path: '/scan_db',
    component: Input
  }, {
    path: '/sesam_response',
    components: [Meta, Input]
  },
  {
    path: '/get_pipes',
    components: Globals
  }
]



const router = new VueRouter({
  routes,
  mode: 'history'
})

new Vue({
  el: '#app',
  router,
  render: h => h(App)
});
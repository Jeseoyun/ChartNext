import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import pinia from './stores'
import vuetify from './plugins/vuetify'

import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(pinia)
app.use(vuetify)

app.mount('#app')

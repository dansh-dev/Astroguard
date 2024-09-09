import { createApp } from 'vue';
import router from './router';
import App from './App.vue';

const app = createApp(App);  // Create the app instance

// Set the global property for $apiIp
app.config.globalProperties.$apiIp = process.env.VUE_APP_API_IP;

// Use the router and mount the app
app.use(router);
app.mount('#app');

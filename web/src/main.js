
/**
 * Entry point for the Vue application.
 * Imports global styles and mounts the root App component to the DOM.
 */

/**
 * Mounts the App component to the #app element in index.html
 */
import App from './App.vue'
import { createApp } from 'vue';
createApp(App).mount('#app')

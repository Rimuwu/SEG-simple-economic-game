
/**
 * Entry point for the Vue application.
 * Imports global styles and mounts the root App component to the DOM.
 */

import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

/**
 * Mounts the App component to the #app element in index.html
 */
createApp(App).mount('#app')

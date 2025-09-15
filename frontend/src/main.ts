import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import router from "./router";
import { useKeycloak } from "./composables/keycloak";

import axios from "axios";

axios.defaults.baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const { initKeycloak } = useKeycloak();

initKeycloak().then(() => {
  const app = createApp(App);
  app.use(router);
  app.mount("#app");
});

import axios from "axios";
import { useKeycloak } from "../composables/keycloak";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Add request interceptor
api.interceptors.request.use(async (config) => {
  const { keycloak } = useKeycloak();

  if (keycloak.value && keycloak.value.token) {
    try {
      await keycloak.value.updateToken(30); // refresh if expiring in <30s
      config.headers.Authorization = `Bearer ${keycloak.value.token}`;
    } catch (error) {
      console.error("Token refresh failed:", error);
      keycloak.value.logout();
    }
  }

  return config;
});

// Add response interceptor for 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { keycloak } = useKeycloak();

    if (error.response && error.response.status === 401 && keycloak.value) {
      try {
        await keycloak.value.updateToken(0); // force refresh
        const config = error.config;
        config.headers.Authorization = `Bearer ${keycloak.value.token}`;
        return api(config); // retry request
      } catch (refreshError) {
        console.warn("401 refresh failed, logging out...");
        keycloak.value.logout();
      }
    }

    return Promise.reject(error);
  }
);

export default api;

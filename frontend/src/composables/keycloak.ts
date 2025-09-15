// src/composables/useKeycloak.ts
import Keycloak from "keycloak-js";
import { ref } from "vue";

const keycloak = ref<Keycloak | null>(null);
const isAuthenticated = ref(false);

export function useKeycloak() {
  const useKeycloakEnv = import.meta.env.VITE_USE_KEYCLOAK === "true";

  function initKeycloak(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      if (!useKeycloakEnv) {
        console.warn("Keycloak disabled by environment");
        return resolve(false);
      }

      if (
        import.meta.env.VITE_KEYCLOAK_URL &&
        import.meta.env.VITE_KEYCLOAK_REALM &&
        import.meta.env.VITE_KEYCLOAK_CLIENT_ID
      ) {
        const kc = new Keycloak({
          url: import.meta.env.VITE_KEYCLOAK_URL,
          realm: import.meta.env.VITE_KEYCLOAK_REALM,
          clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID,
        });

        kc.init({ onLoad: "check-sso", checkLoginIframe: false })
          .then((auth) => {
            keycloak.value = kc;
            isAuthenticated.value = auth;
            if (!auth) {
              window.location.href = import.meta.env.VITE_BASE_URL; // or kc.login()
            }
            resolve(auth);
          })
          .catch(reject);
      } else {
        console.error("Keycloak config missing in .env");
        reject("Keycloak config error");
      }
    });
  }

  return {
    keycloak,
    isAuthenticated,
    initKeycloak,
  };
}

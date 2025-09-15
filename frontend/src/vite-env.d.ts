/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_KEYCLOAK_URL: string;
  readonly VITE_KEYCLOAK_REALM: string;
  readonly VITE_KEYCLOAK_CLIENT_ID: string;
  readonly VITE_API_BASE_URL: string;
  readonly VITE_BASE_URL: string;
  readonly VITE_USE_KEYCLOAK: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

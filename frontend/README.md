````markdown
# 🔐 Vue 3 + TypeScript + Tailwind + Keycloak Auth

This project includes:

- ✅ Conditional Keycloak support via `.env`
- ✅ Secure Axios wrapper with auto token refresh
- ✅ Vue Router guard example for protected routes
- ✅ Shared Keycloak module usable in **Vue and React**

- ✅ Header components are utilizing Tailwind 3.4.17 + Headless UI. Theme is added to ./tailwind.config.js and further theme details are shared

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pnpm install
```
````

### 2. Setup environment variables

Create a `.env` file in the root of the project:

```env
# Enable or disable Keycloak auth
VITE_USE_KEYCLOAK=false

# Keycloak config
VITE_KEYCLOAK_URL=https://auth.yourdomain.com/auth
VITE_KEYCLOAK_REALM=your-realm
VITE_KEYCLOAK_CLIENT_ID=your-client-id

# Backend API URL
VITE_API_BASE_URL=https://api.yourdomain.com

# Base URL (landing page)
VITE_BASE_URL=
```

### 3. Run the app

```bash
pnpm dev
```

---

## 🔐 Keycloak Authentication

Keycloak provides OpenID Connect SSO. This app uses it to:

- Check login silently (`check-sso`) at startup
- Redirect unauthenticated users to a landing page (base url) or prompt for login
- Attach access tokens to all API requests via Axios
- Refresh tokens automatically before expiration

You can disable Keycloak for local development:

```env
VITE_USE_KEYCLOAK=false
```

---

## 📁 Project Structure

```bash
src/
├── api/                # Axios wrapper
│   └── axios.ts
├── composables/        # Vue composables
│   └── keycloak.ts
├── router/             # Vue Router config
│   └── index.ts
├── views/              # Pages
├── main.ts             # App entry
```

---

## 🧩 Vue Example (Axios)

```ts
// inside <script setup>
import api from "@/api/axios";

onMounted(async () => {
  const res = await api.get("/user/profile");
  console.log(res.data);
});
```

---

## ⚛️ React Example (Axios)

```tsx
import { useEffect } from "react";
import api from "./api/axios";

export default function Profile() {
  useEffect(() => {
    api.get("/user/profile").then((res) => {
      console.log(res.data);
    });
  }, []);

  return <div>My Profile</div>;
}
```

---

## 🛡️ Vue Router Guard Example

```ts
// src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";
import Protected from "@/views/Protected.vue";
import { keycloak } from "@/composables/keycloak";

const routes = [
  { path: "/", component: Home },
  {
    path: "/protected",
    component: Protected,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, keycloak } = keycloak();

  if (to.meta.requiresAuth) {
    if (import.meta.env.VITE_USE_KEYCLOAK !== "true") return next();

    if (!isAuthenticated.value) {
      await keycloak.value?.login({
        redirectUri: window.location.origin + to.fullPath,
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
```

---

## 🔄 Shared Keycloak Module Example (Vue + React)

```ts
// src/auth/keycloak.ts
import Keycloak from "keycloak-js";

let keycloak: Keycloak | null = null;

export function initKeycloak(): Promise<boolean> {
  return new Promise((resolve, reject) => {
    if (import.meta.env.VITE_USE_KEYCLOAK !== "true") {
      console.warn("Keycloak disabled via env");
      return resolve(false);
    }

    keycloak = new Keycloak({
      url: import.meta.env.VITE_KEYCLOAK_URL,
      realm: import.meta.env.VITE_KEYCLOAK_REALM,
      clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID,
    });

    keycloak
      .init({ onLoad: "check-sso", checkLoginIframe: false })
      .then((authenticated) => {
        if (!authenticated) {
          window.location.href = "https://mydomain.com"; // or keycloak.login()
        }
        resolve(authenticated);
      })
      .catch(reject);
  });
}

export function getKeycloak(): KeycloakInstance | null {
  return keycloak;
}
```

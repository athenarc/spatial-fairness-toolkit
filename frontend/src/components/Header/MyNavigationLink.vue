<script setup lang="ts">
import { useRouter, type Router } from "vue-router";
import MyNavItem from "./MyNavItem.vue";

const router: Router = useRouter();
const routes = router.options.routes;
</script>

<template>
  <nav class="flex flex-col flex-1">
    <ul role="list" class="flex flex-col flex-1 px-2 gap-y-7">
      <li>
        <ul role="list" class="space-y-2">
          <li v-for="route in routes" :key="route.name" class="relative group">
            <MyNavItem
              :to="route.path"
              :icon="route.meta?.icon"
              :isChild="false"
            >
              {{ route.name }}
            </MyNavItem>
            <!-- Submenu (only if there are children) -->
            <div
              v-if="route.children"
              class="absolute top-0 invisible p-3 space-y-2 text-indigo-900 transition-opacity rounded-lg shadow-lg opacity-0 left-24 bg-aidapt-500 group-hover:opacity-100 group-hover:visible"
            >
              <ul class="w-48 space-y-1">
                <li v-for="child in route.children" :key="child.path">
                  <MyNavItem
                    :to="route.path + '/' + child.path"
                    :icon="child.meta?.icon"
                    isChild
                  >
                    {{ child.name }}
                  </MyNavItem>
                </li>
              </ul>
            </div>
          </li>
        </ul>
      </li>
    </ul>
  </nav>
</template>

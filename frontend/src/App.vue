<script setup lang="ts">
import MyNavigationLink from "./components/Header/MyNavigationLink.vue";
import Navigation from "./components/Navigation.vue";
</script>

<template>
  <Navigation>
    <template #navigation-links>
      <MyNavigationLink />
    </template>
    <RouterView />
  </Navigation>
</template>

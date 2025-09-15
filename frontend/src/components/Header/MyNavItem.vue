<script setup lang="ts">
import { RouterLink, useLink } from "vue-router";
import MyIcon from "../MyIcon.vue";

const props = defineProps<{ to: string; icon: any; isChild: boolean }>();

// `useLink` provides `isActive`, `isExactActive`, and `href`
const { isActive } = useLink({ to: props.to });
</script>

<template>
  <RouterLink
    :to="to"
    class="flex flex-col items-center justify-center w-full p-3 transition-all rounded-md"
    :class="[
      isActive
        ? 'bg-white text-aidapt-500'
        : 'hover:bg-white hover:text-aidapt-500 text-white',
      isChild ? ' bg-aidapt-500 hover:text-aidapt-500' : '',
    ]"
  >
    <MyIcon :name="icon" class="size-6" />
    <span class="mt-1 text-sm">
      <slot />
    </span>
  </RouterLink>
</template>

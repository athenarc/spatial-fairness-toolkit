<script setup lang="ts">
import { defineProps, computed } from "vue";
import * as HeroIcons from "@heroicons/vue/24/solid";

type HeroIconName = keyof typeof HeroIcons;

const props = defineProps<{
  name: HeroIconName;
  size?: string;
  className?: string;
}>();

const IconComponent = computed(() => HeroIcons[props.name] || null);
</script>

<template>
  <component
    v-if="IconComponent"
    :is="IconComponent"
    :class="className"
    :width="size"
    :height="size"
    aria-hidden="true"
  />
</template>

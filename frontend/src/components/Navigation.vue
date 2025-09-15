<script setup lang="ts">
import { ref } from "vue";
import {
  Dialog,
  DialogPanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  TransitionChild,
  TransitionRoot,
} from "@headlessui/vue";
import { Bars3Icon, BellIcon, XMarkIcon } from "@heroicons/vue/24/outline";
import { ChevronDownIcon } from "@heroicons/vue/20/solid";
import { useRouter } from "vue-router";
import MyIcon from "./MyIcon.vue";
import * as HeroIcons from "@heroicons/vue/24/solid";

type HeroIconName = keyof typeof HeroIcons;

const router = useRouter();
const navigation = router.options.routes;

const userNavigation = [
  { name: "Your profile", path: "#" },
  { name: "Sign out", path: "#" },
];

const sidebarOpen = ref(false);
</script>
<template>
  <div class="h-full">
    <TransitionRoot as="template" :show="sidebarOpen">
      <Dialog class="relative z-50" @close="sidebarOpen = false">
        <TransitionChild
          as="template"
          enter="transition-opacity ease-linear duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="transition-opacity ease-linear duration-300"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-900/80"></div>
        </TransitionChild>

        <div class="fixed inset-0 flex">
          <TransitionChild
            as="template"
            enter="transition ease-in-out duration-300 transform"
            enter-from="-translate-x-full"
            enter-to="translate-x-0"
            leave="transition ease-in-out duration-300 transform"
            leave-from="translate-x-0"
            leave-to="-translate-x-full"
          >
            <DialogPanel class="relative flex flex-1 w-full max-w-xs mr-16">
              <TransitionChild
                as="template"
                enter="ease-in-out duration-300"
                enter-from="opacity-0"
                enter-to="opacity-100"
                leave="ease-in-out duration-300"
                leave-from="opacity-100"
                leave-to="opacity-0"
              >
                <div
                  class="absolute top-0 flex justify-center w-16 pt-5 left-full"
                >
                  <button
                    type="button"
                    class="-m-2.5 p-2.5"
                    @click="sidebarOpen = false"
                  >
                    <span class="sr-only">Close sidebar</span>
                    <XMarkIcon class="text-white size-6" aria-hidden="true" />
                  </button>
                </div>
              </TransitionChild>
              <!-- Sidebar component, swap this element with another sidebar if you like -->
              <div
                class="flex flex-col px-6 pb-4 overflow-y-auto bg-aidapt-500 grow gap-y-5"
              >
                <div class="flex items-center h-16 shrink-0">
                  <!-- Can add logo -->
                </div>
                <nav class="flex flex-col flex-1">
                  <ul role="list" class="flex flex-col flex-1 gap-y-7">
                    <li>
                      <ul role="list" class="-mx-2 space-y-1">
                        <li v-for="item in navigation" :key="item.name">
                          <RouterLink
                            :to="item.path"
                            :class="[
                              item.name === $router.currentRoute.value.name
                                ? 'bg-aidapt-600 text-white'
                                : 'text-indigo-200 hover:bg-aidapt-700 hover:text-white',
                              'group flex gap-x-3 rounded-md p-2 text-sm/6 font-semibold',
                            ]"
                          >
                            <MyIcon
                              v-if="item.meta?.icon"
                              :name="item.meta.icon as HeroIconName"
                              class="size-6"
                            />
                            {{ item.name }}
                          </RouterLink>
                          <div
                            v-if="item.children"
                            class="space-y-2 text-indigo-900 ml-9"
                          >
                            <ul class="space-y-1">
                              <li
                                v-for="child in item.children"
                                :key="child.path"
                              >
                                <RouterLink
                                  :to="child.path"
                                  :class="[
                                    child.name ===
                                    $router.currentRoute.value.name
                                      ? 'bg-aidapt-600 text-white'
                                      : 'text-indigo-200 hover:bg-aidapt-700 hover:text-white',
                                    'group flex gap-x-3 rounded-md p-2 text-sm/6 font-semibold',
                                  ]"
                                >
                                  <MyIcon
                                    v-if="child.meta?.icon"
                                    :name="child.meta.icon as HeroIconName"
                                    class="size-6"
                                  />
                                  {{ child.name }}
                                </RouterLink>
                              </li>
                            </ul>
                          </div>
                        </li>
                      </ul>
                    </li>
                  </ul>
                </nav>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Static sidebar for desktop -->
    <div
      class="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-24 lg:flex-col bg-aidapt-500"
    >
      <!-- Sidebar component, swap this element with another sidebar if you like -->
      <div class="flex flex-col pb-4 grow gap-y-5 bg-primary-400">
        <div
          class="flex items-center justify-center w-full h-16 cursor-pointer shrink-0 bg-aidaptPurple"
          @click="sidebarOpen = true"
        >
          <Bars3Icon class="text-white size-8" aria-hidden="true" />
        </div>
        <slot name="navigation-links"></slot>
      </div>
    </div>

    <div class="h-full lg:pl-24">
      <div
        class="sticky top-0 z-40 flex items-center h-16 px-4 bg-white border-b border-gray-200 shadow-sm shrink-0 gap-x-4 sm:gap-x-6 sm:px-6 lg:px-8"
      >
        <button
          type="button"
          class="-m-2.5 p-2.5 text-gray-700 lg:hidden"
          @click="sidebarOpen = true"
        >
          <span class="sr-only">Open sidebar</span>
          <Bars3Icon class="size-6" aria-hidden="true" />
        </button>

        <!-- Separator -->
        <div class="w-px h-6 bg-gray-900/10 lg:hidden" aria-hidden="true" />

        <div class="flex self-stretch flex-1 gap-x-4 lg:gap-x-6">
          <div class="grid flex-1 grid-cols-1">
            <div class="self-center">
              <img
                class="w-auto h-10 bg-gray-50"
                src="../assets/logo.png"
                alt=""
              />
            </div>
          </div>
          <div class="flex items-center gap-x-4 lg:gap-x-6">
            <button
              type="button"
              class="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500"
            >
              <span class="sr-only">View notifications</span>
              <BellIcon class="size-6" aria-hidden="true" />
            </button>

            <!-- Separator -->
            <div
              class="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-900/10"
              aria-hidden="true"
            />

            <!-- Profile dropdown -->
            <Menu as="div" class="relative">
              <MenuButton class="-m-1.5 flex items-center p-1.5">
                <span class="sr-only">Open user menu</span>
                <img
                  class="rounded-full size-8 bg-gray-50"
                  src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                  alt=""
                />
                <span class="hidden lg:flex lg:items-center">
                  <span
                    class="ml-4 font-semibold text-gray-900 text-sm/6"
                    aria-hidden="true"
                    >Tom Cook</span
                  >
                  <ChevronDownIcon
                    class="ml-2 text-gray-400 size-5"
                    aria-hidden="true"
                  />
                </span>
              </MenuButton>
              <transition
                enter-active-class="transition duration-100 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-75 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0"
              >
                <MenuItems
                  class="absolute right-0 z-10 mt-2.5 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none"
                >
                  <MenuItem
                    v-for="item in userNavigation"
                    :key="item.name"
                    v-slot="{ active }"
                  >
                    <a
                      :href="item.path"
                      :class="[
                        active ? 'bg-gray-50 outline-none' : '',
                        'block px-3 py-1 text-sm/6 text-gray-900',
                      ]"
                      >{{ item.name }}</a
                    >
                  </MenuItem>
                </MenuItems>
              </transition>
            </Menu>
          </div>
        </div>
      </div>

      <main class="full-page">
        <!-- Your content -->
        <slot></slot>
      </main>
    </div>
  </div>
</template>
<style>
.full-page {
  height: calc(100vh - 64px);
}
</style>

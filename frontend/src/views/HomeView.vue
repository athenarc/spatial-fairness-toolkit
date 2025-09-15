<script setup lang="ts">
    import { useRouter } from "vue-router";

    const router = useRouter();

    const navigateToAnalysis = (type: string) => {
        if (type === "spatial-bias") {
            router.push("/spatial-bias");
        }
    };
</script>

<template>
    <div class="flex items-center justify-center flex-1 h-full bg-gradient-to-br from-indigo-50 to-white pt-20">
        <div class="max-w-4xl mx-auto px-6 py-12">
            <div class="text-center mb-12">
                <h1 class="text-4xl font-bold text-gray-900 mb-4">
                    AI-DAPT Data Valuation Engine
                </h1>
            </div>

            <div class="grid md:grid-cols-3 gap-8 mb-12">

                <!-- Spatial Bias Detection Card -->
                <div class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer border border-gray-200"
                     @click="navigateToAnalysis('spatial-bias')">
                    <div class="flex items-center mb-4">
                        <div class="bg-green-100 p-3 rounded-lg mr-4">
                            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h8M12 8v8" />
                            </svg>
                        </div>
                        <h3 class="text-xl font-semibold text-gray-900">Spatial Bias Detection & Mitigation</h3>
                    </div>
                    <p class="text-gray-600 mb-4">
                        Detect and mitigate spatial bias in your data to ensure fair and representative geographic outcomes.
                    </p>
                    <div class="flex items-center text-green-600 font-medium">
                        <span>Start Analysis</span>
                        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M9 5l7 7-7 7" />
                        </svg>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Technology Stack</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="text-center">
                        <div class="bg-green-100 p-3 rounded-lg mb-2 inline-block">
                            <span class="text-green-600 font-bold">FastAPI</span>
                        </div>
                        <p class="text-sm text-gray-600">Backend API</p>
                    </div>
                    <div class="text-center">
                        <div class="bg-blue-100 p-3 rounded-lg mb-2 inline-block">
                            <span class="text-blue-600 font-bold">Vue 3</span>
                        </div>
                        <p class="text-sm text-gray-600">Frontend</p>
                    </div>
                    <!-- <div class="text-center">
                        <div class="bg-yellow-100 p-3 rounded-lg mb-2 inline-block">
                            <span class="text-yellow-600 font-bold">PyCaret</span>
                        </div>
                        <p class="text-sm text-gray-600">ML Models</p>
                    </div>
                    <div class="text-center">
                        <div class="bg-red-100 p-3 rounded-lg mb-2 inline-block">
                            <span class="text-red-600 font-bold">SHAP</span>
                        </div>
                        <p class="text-sm text-gray-600">Explainability</p>
                    </div> -->
                </div>
            </div>
        </div>
    </div>
</template>
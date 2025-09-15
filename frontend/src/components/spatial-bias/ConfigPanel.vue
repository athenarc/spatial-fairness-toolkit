<template>
    <div v-if="mode === 'relabel'" class="border border-gray-300 rounded p-4 space-y-4">
        <h3 class="text-lg font-semibold">Configuration</h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
                <label>Fairness Notion</label>
                <select v-model="advanced.equal_opp" class="w-full p-2 border rounded">
                <option :value="true">Equal Opportunity</option>
                <option :value="false">Statistical Parity</option>
                </select>
            </div>
            <div>
                <label>Work Limit</label>
                <input 
                    type="number" 
                    v-model.number="advanced.wlimit" 
                    class="w-full p-2 border rounded" 
                    step="1"
                    min="1"
                    inputmode="numeric"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Budget Constraint (%)</label>
                <input 
                    type="number" 
                    v-model.number="budgetPct" 
                    class="w-full p-2 border rounded" 
                    step="1"
                    min="0"
                    max="100"
                    inputmode="decimal"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Approximate Solution</label>
                <select v-model="advanced.approx" class="w-full p-2 border rounded">
                <option :value="true">True</option>
                <option :value="false">False</option>
                </select>
            </div>
            <div>
                <label>Positive Rate Change Tolerance (%)</label>
                <input 
                    type="number" 
                    v-model.number="prPct" 
                    class="w-full p-2 border rounded" 
                    step="1"
                    min="0"
                    max="100"
                    inputmode="decimal"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Alternate Worlds</label>
                <input
                    type="number"
                    v-model.number="advanced.n_worlds"
                    class="w-full p-2 border rounded"
                    step="1"
                    min="1"
                    inputmode="numeric"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Significance Level</label>
                <input
                    type="number"
                    v-model.number="advanced.signif_level"
                    class="w-full p-2 border rounded"
                    step="0.0001"
                    min="0.000001"
                    max="1"
                    inputmode="decimal"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
        </div>
    </div>

    <div v-if="mode === 'threshold'" class="border border-gray-300 rounded p-4 space-y-4">
        <h3 class="text-lg font-semibold">Configuration</h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
                <label>Fairness Notion</label>
                <select v-model="advanced.equal_opp" class="w-full p-2 border rounded">
                <option :value="true">Equal Opportunity</option>
                <option :value="false">Statistical Parity</option>
                </select>
            </div>
            <div>
                <label>Work Limit</label>
                <input 
                    type="number" 
                    v-model.number="advanced.wlimit" 
                    class="w-full p-2 border rounded" 
                    step="1"
                    min="1"
                    inputmode="numeric"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Budget Constraint (%)</label>
                <input 
                    type="number" 
                    v-model.number="budgetPct" 
                    class="w-full p-2 border rounded" 
                    step="1"
                    min="0"
                    max="100"
                    inputmode="decimal"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Approximate Solution</label>
                <select v-model="advanced.approx" class="w-full p-2 border rounded">
                <option :value="true">True</option>
                <option :value="false">False</option>
                </select>
            </div>
            <div>
                <label>Positive Rate Change Tolerance (%)</label>
                <input 
                    type="number" 
                    v-model.number="prPct" 
                    class="w-full p-2 border rounded" 
                    step="1"
                    min="0"
                    max="100"
                    inputmode="decimal"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Alternate Worlds</label>
                <input
                    type="number"
                    v-model.number="advanced.n_worlds"
                    class="w-full p-2 border rounded"
                    step="1"
                    min="1"
                    inputmode="numeric"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Significance Level</label>
                <input
                    type="number"
                    v-model.number="advanced.signif_level"
                    class="w-full p-2 border rounded"
                    step="0.0001"
                    min="0.000001"
                    max="1"
                    inputmode="decimal"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
            <label>Base Decision Boundary</label>
                <input
                    type="number"
                    v-model.number="advanced.decision_bound"
                    class="w-full p-2 border rounded"
                    step="0.01"
                    min="0"
                    max="1"
                    inputmode="decimal"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
        </div>
    </div>
    <!-- Right: Config -->
    <div v-if="mode === 'audit'" class="border border-gray-300 rounded p-4 space-y-4">
        <h3 class="text-lg font-semibold">Configuration</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
                <label>Fairness Notion</label>
                <select v-model="advanced.equal_opp" class="w-full p-2 border rounded">
                <option :value="true">Equal Opportunity</option>
                <option :value="false">Statistical Parity</option>
                </select>
            </div>
            <div>
                <label>Alternate Worlds</label>
                <input
                    type="number"
                    v-model.number="advanced.n_worlds"
                    class="w-full p-2 border rounded"
                    step="1"
                    min="1"
                    inputmode="numeric"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
            <div>
                <label>Significance Level</label>
                <input
                    type="number"
                    v-model.number="advanced.signif_level"
                    class="w-full p-2 border rounded"
                    step="0.001"
                    min="0.000001"
                    max="1"
                    inputmode="decimal"
                    @wheel.prevent="preventWheel"
                    @keydown.e.prevent="preventE"
                    @keydown.E.prevent="preventE"
                />
            </div>
        </div>
    </div>
</template>
  
<script setup lang="ts">
    import { computed } from 'vue'

    const props = defineProps<{
        mode: 'audit' | 'relabel' | 'threshold',
        advanced: {
            equal_opp: boolean,
            signif_level: number,      // 0..1
            n_worlds: number,          // int
            budget_constr: number,     // fraction 0..1 (UI shows %)
            pr_constr: number,         // fraction 0..1 (UI shows %)
            approx: boolean,
            wlimit: number,            // int
            decision_bound: number     // 0..1
        }
    }>()

    // helpers
    const clamp = (v: number, min: number, max: number) => Math.min(max, Math.max(min, v))
    const round1 = (v: number) => Math.round(v * 10) / 10

    // UI-as-percent for budget_constr (0..100), stored as fraction (0..1)
    const budgetPct = computed<number>({
        get: () => round1((props.advanced.budget_constr ?? 0) * 100),
        set: (v) => { props.advanced.budget_constr = clamp(v, 0, 100) / 100 }
    })

    // UI-as-percent for pr_constr (0..100), stored as fraction (0..1)
    const prPct = computed<number>({
        get: () => round1((props.advanced.pr_constr ?? 0) * 100),
        set: (v) => { props.advanced.pr_constr = clamp(v, 0, 100) / 100 }
    })

    // (Optional) Prevent accidental number scroll & scientific notation in all inputs
    const preventWheel = (e: Event) => (e.target as HTMLInputElement).blur()
    const preventE = (e: KeyboardEvent) => {
    if (e.key === 'e' || e.key === 'E' || e.key === '+' || e.key === '-') e.preventDefault()
    }
</script>
  
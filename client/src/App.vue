<script setup>
import { ref } from 'vue';
import CampaignForm from './components/CampaignForm.vue';
import Dashboard from './components/Dashboard.vue';
import AnalyzingState from './components/AnalyzingState.vue';

const sampleData = {
  predictive_score: 85.0,
  final_rating: 'Green',
  benchmark_score: 78.5,
  dna_score: 92.3,
  message: 'Policy Safe',
  policy_check: {
    is_safe: true,
    reason: 'Compliant'
  },
  creative_metrics: {
    hook_score: 88,
    pacing_score: 75,
    safe_zone: true,
    duration_seconds: 15
  }
};

const analysisData = ref(null);
const isLoading = ref(false);
const errorMsg = ref('');

const handleAnalysisStart = () => {
  isLoading.value = true;
  errorMsg.value = '';
  // analysisData.value = null; // Keep sample data visible or clear it? Clearning it shows loading state better if we handle loading in App.vue
};

const handleAnalysisSuccess = (data) => {
  isLoading.value = false;
  analysisData.value = data;
};

const handleAnalysisError = (message) => {
  isLoading.value = false;
  errorMsg.value = message;
};

const resetAnalysis = () => {
  analysisData.value = null;
  errorMsg.value = '';
};

// Version & Env Logic
const appVersion = 'v' + __APP_VERSION__;
const hostname = window.location.hostname;
let envLabel = 'Local';
let envClass = 'bg-gray-100 text-gray-600';

if (hostname.includes('develop')) {
    envLabel = 'Staging';
    envClass = 'bg-yellow-100 text-yellow-700 border-yellow-200';
} else if (hostname.includes('vercel.app') && !hostname.includes('develop')) {
    envLabel = 'Production';
    envClass = 'bg-green-100 text-green-700 border-green-200';
}
</script>

<template>
  <div class="min-h-screen bg-cream font-sans text-gray-800 p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="flex items-center gap-3 mb-8">
        <div class="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-indigo-200 shadow-lg">
          <i class="fa-solid fa-plane-departure"></i>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 tracking-tight">Pre-flight Check</h1>
          <p class="text-xs text-gray-500 font-medium uppercase tracking-wider">Benchmark Tool</p>
        </div>
      </div>

      <!-- Version Badge (Top Right) -->
      <div class="absolute top-4 right-4 md:top-8 md:right-8 flex items-center gap-2">
          <span class="px-3 py-1 rounded-full text-xs font-bold border" :class="envClass">
              {{ envLabel }}
          </span>
          <span class="text-xs text-gray-400 font-mono">{{ appVersion }}</span>
      </div>

      <!-- Error Toast -->
      <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 flex items-center gap-3 animate-pulse">
        <i class="fa-solid fa-circle-exclamation"></i>
        <span v-html="errorMsg"></span>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Left Column: Form -->
        <div class="lg:col-span-4 space-y-6">
          <CampaignForm 
            @start="handleAnalysisStart"
            @success="handleAnalysisSuccess"
            @error="handleAnalysisError"
            :is-loading="isLoading"
          />
        </div>

        <!-- Right Column: Dashboard or Placeholder -->
        <div class="lg:col-span-8 relative">
          <!-- Real Data -->
          <Dashboard v-if="analysisData && !isLoading" :data="analysisData" />

          <!-- Analyzing State -->
          <AnalyzingState v-else-if="isLoading" />
          
          <!-- Sample Data / Empty State -->
          <div v-else class="relative">
             <div class="absolute inset-0 z-10 bg-white/60 backdrop-blur-[2px] rounded-3xl flex flex-col items-center justify-center text-center p-6 border-2 border-dashed border-indigo-100/50">
                <div class="bg-white p-4 rounded-full shadow-lg mb-4">
                   <i class="fa-solid fa-chart-pie text-3xl text-indigo-600 animate-pulse"></i>
                </div>
                <h3 class="text-xl font-bold text-gray-800 mb-2">Ready for Analysis</h3>
                <p class="text-gray-500 max-w-sm mx-auto">Fill out the campaign details on the left to generate your custom AI analysis</p>
             </div>
             <!-- Render Dashboard with Sample Data (Blurred BG) -->
             <Dashboard :data="sampleData" class="opacity-50 pointer-events-none filter blur-sm select-none" />
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

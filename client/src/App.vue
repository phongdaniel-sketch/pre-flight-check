<script setup>
import { ref } from 'vue';
import CampaignForm from './components/CampaignForm.vue';
import Dashboard from './components/Dashboard.vue';

const analysisData = ref(null);
const isLoading = ref(false);
const errorMsg = ref('');

const handleAnalysisStart = () => {
  isLoading.value = true;
  errorMsg.value = '';
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
        <div class="lg:col-span-8">
          <Dashboard v-if="analysisData" :data="analysisData" />
          
          <div v-else class="h-full min-h-[400px] border-2 border-dashed border-gray-200 rounded-2xl flex flex-col items-center justify-center text-gray-400 bg-white/50">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4 text-gray-300">
              <i class="fa-solid fa-chart-pie text-2xl"></i>
            </div>
            <p class="font-medium">Ready for Analysis</p>
            <p class="text-sm mt-1">Fill out the campaign details to begin.</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

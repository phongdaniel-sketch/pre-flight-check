<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  elapsedSeconds: {
    type: Number,
    default: 0
  }
});

const timer = ref(0);
let intervalId = null;

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

onMounted(() => {
  intervalId = setInterval(() => {
    timer.value++;
  }, 1000);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});
</script>

<template>
  <div class="h-full min-h-[500px] flex flex-col items-center justify-center p-8 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl border border-indigo-50 dark:border-gray-700 shadow-sm relative overflow-hidden transition-colors duration-300">
    <!-- Background Abstract Shapes -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
      <div class="absolute top-10 left-10 w-64 h-64 bg-indigo-200/20 dark:bg-indigo-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-10 right-10 w-80 h-80 bg-purple-200/20 dark:bg-purple-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
    </div>

    <!-- Main Content -->
    <div class="z-10 flex flex-col items-center">
      <!-- Animated Icon Container -->
      <div class="relative w-32 h-32 mb-8 flex items-center justify-center">
        <!-- Pulse Rings -->
        <div class="absolute inset-0 border-4 border-indigo-100 dark:border-indigo-900/30 rounded-full animate-ping opacity-75"></div>
        <div class="absolute inset-0 border-4 border-indigo-200 dark:border-indigo-800/30 rounded-full animate-ping opacity-50" style="animation-delay: 0.5s;"></div>
        
        <!-- Rotating Spinner -->
        <div class="absolute inset-0 w-full h-full border-4 border-t-indigo-600 border-r-transparent border-b-purple-500 border-l-transparent rounded-full animate-spin"></div>
        
        <!-- Center Icon -->
        <div class="bg-white dark:bg-gray-800 rounded-full w-24 h-24 flex items-center justify-center shadow-lg dark:shadow-gray-900/50 relative z-10 transition-colors">
          <i class="fa-solid fa-wand-magic-sparkles text-3xl bg-gradient-to-br from-indigo-600 to-purple-600 bg-clip-text text-transparent animate-pulse"></i>
        </div>
      </div>

      <!-- Text Content -->
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-2">Analyzing</h2>
      <p class="text-gray-500 dark:text-gray-400 mb-6 text-center max-w-xs">
        Our AI is breaking down your video, checking policies, and predicting performance...
      </p>

      <!-- Timer Pill -->
      <div class="flex items-center gap-2 bg-indigo-50 dark:bg-indigo-900/20 px-4 py-2 rounded-full border border-indigo-100 dark:border-indigo-800 transition-colors">
        <i class="fa-regular fa-clock text-indigo-500 dark:text-indigo-400 animate-spin-slow"></i>
        <span class="font-mono font-medium text-indigo-700 dark:text-indigo-300">{{ formatTime(timer) }}</span>
      </div>
    </div>
    
    <!-- Progress Steps (Visual only) -->
    <div class="mt-12 w-full max-w-xs space-y-3 z-10">
      <div class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300">
        <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        <span>Video breakdown and scene detection</span>
      </div>
      <div class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300 opacity-75">
        <div class="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" style="animation-delay: 0.5s;"></div>
        <span>Policy compliance check</span>
      </div>
      <div class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300 opacity-50">
        <div class="w-2 h-2 rounded-full bg-purple-300 animate-pulse" style="animation-delay: 1s;"></div>
        <span>Performance prediction model</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-spin-slow {
  animation: spin 3s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

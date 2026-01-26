<script setup>
import { computed } from 'vue';

const props = defineProps({
  data: Object,
  isSample: {
    type: Boolean,
    default: false
  }
});

// Benchmark Rating Color
const benchmarkColor = computed(() => {
    const score = props.data.benchmark_score;
    if (score > 80) return 'text-pastel-mint';
    if (score >= 50) return 'text-pastel-canary';
    return 'text-pastel-coral';
});

// DNA Rating Color
const dnaColor = computed(() => {
  const score = props.data.dna_score;
  if (score > 80) return 'text-pastel-mint';
  if (score >= 50) return 'text-pastel-canary';
  return 'text-pastel-coral';
});

// Final Score Color
const finalRatingColor = computed(() => {
  return props.data.final_rating === 'Red' ? 'text-pastel-coral' : 
         props.data.final_rating === 'Yellow' ? 'text-pastel-canary' : 'text-pastel-mint';
});

// Policy Logic
const policyReasons = computed(() => {
    const raw = props.data.policy_check.reason || 'Unsafe';
    return raw.split('; ').map(r => {
        let badge = '';
        let content = r;
        let details = '';

        if (r.startsWith('Video:')) {
            content = r.replace('Video:', '').trim();
            badge = 'Video Violation';
        } else if (r.startsWith('LP:')) {
            content = r.replace('LP:', '').trim();
            badge = 'Landing Page Violation';
        }

        if (content.includes('Flagged for Manual Review:')) {
            const parts = content.split('Flagged for Manual Review:');
            content = 'Flagged for Manual Review';
            details = parts[1] ? parts[1].trim() : '';
        }

        return { badge, content, details };
    });
});

const isSafe = computed(() => props.data.policy_check.is_safe);

// Assessment Parsing
const assessmentPoints = computed(() => {
    let msg = props.data.message.replace('Analysis Complete. ', '');
    if (msg === 'Policy Safe') msg = 'No policy violations found.';
    
    return msg.split('; ').map(p => {
        let title = '';
        let content = p;
        
        if (p.startsWith('Video:')) {
           title = 'Video Analysis';
           content = p.replace('Video:', '').trim();
        } else if (p.startsWith('LP:')) {
           title = 'Landing Page Analysis';
           content = p.replace('LP:', '').trim();
        }
        
        // Handle Flagged Details in Assessment too
        let details = '';
        if (content.includes('Flagged for Manual Review:')) {
             const parts = content.split('Flagged for Manual Review:');
             content = 'Flagged for Manual Review';
             details = parts[1] ? parts[1].trim() : '';
        }

        return { title, content, details };
    });
});

// Gauge Logic
const gaugeDashArray = computed(() => {
    const score = props.data.predictive_score || 0;
    // Circumference = 2 * pi * 45 ≈ 282.7
    const circumference = 282.7;
    const dash = (score / 100) * circumference;
    return `${dash} ${circumference}`;
});

const gaugeColorClass = computed(() => {
    const rating = props.data.final_rating;
    if (rating === 'Green') return 'text-pastel-mint';
    if (rating === 'Yellow') return 'text-pastel-canary';
    return 'text-pastel-coral';
});

const statusLabel = computed(() => {
    const rating = props.data.final_rating;
    if (rating === 'Green') return 'Ready to Fly';
    if (rating === 'Yellow') return 'Needs Optimization';
    return 'Rejected';
});

const statusColorClass = computed(() => {
    const rating = props.data.final_rating;
    if (rating === 'Green') return 'bg-pastel-mint text-white';
    if (rating === 'Yellow') return 'bg-pastel-canary text-yellow-900';
    return 'bg-pastel-coral text-white';
});
</script>

<template>
  <div class="space-y-6 animate-fade-in-up">
    <!-- Top Row: Scores and Metrics -->
    <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 relative overflow-hidden">
        <!-- Floating Watermark/Icon style from reference -->
        <div class="absolute top-0 right-0 p-6 opacity-5 pointer-events-none">
            <i class="fa-solid fa-chart-line text-9xl text-indigo-900"></i>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-12 gap-8 items-center relative z-10">
            <!-- Left: Score Gauge -->
            <div class="md:col-span-5 flex flex-col items-center border-r border-gray-100 pr-8">
                <div class="w-48 h-48 relative mb-4">
                    <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" fill="none" stroke="#F3F4F6" stroke-width="6"></circle>
                        <circle cx="50" cy="50" r="45" fill="none" :class="gaugeColorClass" stroke="currentColor" stroke-width="6" stroke-linecap="round" :stroke-dasharray="gaugeDashArray" stroke-dashoffset="0" class="transition-all duration-1000 ease-out shadow-lg"></circle>
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Predictive Score</span>
                        <span class="text-5xl font-extrabold text-gray-800">{{ Math.round(data.predictive_score) }}</span>
                        <div class="flex items-center gap-1 mt-2">
                             <div class="w-2 h-1 rounded-full" :class="data.final_rating === 'Red' ? 'bg-pastel-coral' : 'bg-gray-200'"></div>
                             <div class="w-2 h-1 rounded-full" :class="data.final_rating === 'Yellow' ? 'bg-pastel-canary' : 'bg-gray-200'"></div>
                             <div class="w-2 h-1 rounded-full" :class="data.final_rating === 'Green' ? 'bg-pastel-mint' : 'bg-gray-200'"></div>
                        </div>
                    </div>
                </div>
                <span class="px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide transition-colors" :class="statusColorClass">{{ statusLabel }}</span>
            </div>

            <!-- Middle/Right: Benchmark & DNA Cards -->
            <div class="md:col-span-7 grid grid-cols-2 gap-6">
                <!-- Benchmark Card -->
                <div class="bg-indigo-50/50 p-6 rounded-2xl border border-indigo-50 flex flex-col items-center justify-center text-center">
                    <div class="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-3">Benchmark</div>
                    <span class="text-3xl font-extrabold text-indigo-900" id="benchmarkVal">{{ Math.round(data.benchmark_score) }}</span>
                    <div class="w-12 h-1 bg-indigo-200 rounded-full mt-2"></div>
                </div>

                <!-- DNA Score Card -->
                <div class="bg-purple-50/50 p-6 rounded-2xl border border-purple-50 flex flex-col items-center justify-center text-center">
                    <div class="text-xs font-bold text-purple-400 uppercase tracking-widest mb-3">DNA Score</div>
                     <span class="text-3xl font-extrabold text-purple-900">{{ data.dna_score.toFixed(0) }}</span>
                     <div class="w-12 h-1 bg-purple-200 rounded-full mt-2"></div>
                </div>

                 <!-- Policy Check Status Row (Spanning 2 cols) -->
                <div class="col-span-2 bg-white border border-gray-100 p-4 rounded-xl flex items-center justify-between px-6 shadow-sm">
                    <span class="text-sm font-semibold text-gray-600">Policy Check</span>
                     <span v-if="isSafe" class="flex items-center gap-2 text-pastel-mint font-bold text-sm">
                        <i class="fa-solid fa-check"></i> Passed
                    </span>
                    <span v-else class="flex items-center gap-2 text-pastel-coral font-bold text-sm">
                        <i class="fa-solid fa-triangle-exclamation"></i> Issues Found
                    </span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Policy Check -->
    <div v-if="!isSample" class="bg-white p-6 rounded-2xl shadow-sm border border-indigo-50">
       <div class="flex items-center gap-2 mb-4">
          <i class="fa-solid fa-shield-halved text-indigo-500"></i>
          <h3 class="font-bold text-gray-800">Policy Check</h3>
       </div>

       <div v-if="isSafe" class="bg-cream p-4 rounded-xl border border-indigo-100 flex items-center gap-3 px-6">
           <i class="fa-solid fa-shield-check text-pastel-mint text-xl"></i>
           <span class="text-sm font-bold text-gray-700">Safe</span>
       </div>

       <div v-else class="bg-cream p-5 rounded-xl border border-indigo-100 flex flex-col gap-3 px-6">
           <div class="flex items-center gap-2 mb-1">
               <i class="fa-solid fa-triangle-exclamation text-pastel-coral"></i> 
               <span class="uppercase font-bold text-xs text-pastel-coral">Policy Warning</span>
           </div>
           
           <div v-for="(reason, idx) in policyReasons" :key="idx" class="text-sm">
               <div v-if="reason.badge" class="font-bold text-indigo-500 text-xs uppercase tracking-wide mb-1 block">
                   {{ reason.badge }}:
               </div>
               
               <div v-if="reason.details" class="bg-white/50 p-3 rounded-lg border border-indigo-100/50 mt-1">
                   <div class="font-bold text-indigo-600 mb-1">{{ reason.content }}</div>
                   <p class="text-gray-600 leading-snug whitespace-pre-wrap text-xs">{{ reason.details }}</p>
               </div>
               <div v-else class="text-gray-600 font-medium">
                   {{ reason.content }}
               </div>
           </div>
       </div>
    </div>

    <!-- Assessment -->
    <div v-if="!isSample" class="bg-indigo-50/30 p-6 rounded-2xl border border-indigo-100">
         <div class="flex items-center gap-2 mb-4">
            <i class="fa-solid fa-clipboard-check text-indigo-600"></i>
            <h3 class="font-bold text-indigo-900 uppercase tracking-widest text-xs">Assessment</h3>
        </div>
        
        <div class="space-y-4">
             <div v-for="(point, idx) in assessmentPoints" :key="idx">
                <div v-if="point.title" class="mb-2">
                    <span class="font-bold text-indigo-600 block mb-1 text-base">{{ point.title }}</span>
                    
                     <div v-if="point.details" class="bg-indigo-50 p-4 rounded-xl border border-indigo-100 mt-2">
                         <span class="inline-block font-bold text-indigo-700 text-[10px] uppercase tracking-wide px-2 py-0.5 bg-white rounded border border-indigo-200 mb-2 shadow-sm">Flagged for Review</span>
                         <div class="text-gray-700 leading-relaxed text-sm">{{ point.details }}</div>
                     </div>
                     <span v-else class="text-sm text-gray-600">{{ point.content }}</span>
                </div>
                <div v-else class="text-sm text-gray-600 mb-2">
                    {{ point.content }}
                </div>
             </div>
        </div>

        <!-- Financial Context -->
        <div v-if="isSafe" class="mt-4 p-3 bg-indigo-50/50 rounded-xl border border-indigo-100">
            <div class="text-xs font-bold text-indigo-400 uppercase tracking-wide mb-1">Financial Potential</div>
            <div class="text-sm text-gray-700">Benchmarking indicates <span class="font-bold" :class="data.benchmark_score > 80 ? 'text-pastel-mint' : 'text-pastel-canary'">{{ data.benchmark_score > 80 ? 'Strong' : 'Moderate' }}</span> performance potential.</div>
        </div>
        <div v-else class="mt-4 p-4 bg-red-50 rounded-xl border border-red-100">
            <div class="text-xs font-bold text-red-500 uppercase tracking-wide mb-1">Action Required</div>
            <div class="text-sm text-red-700 font-bold">Please resolve policy violations to see financial benchmarking.</div>
        </div>
    </div>

    <!-- Creative DNA Details -->
    <div v-if="!isSample" class="bg-white p-6 rounded-2xl shadow-sm border border-indigo-50">
        <div class="flex items-center gap-2 mb-4">
          <i class="fa-solid fa-wand-magic-sparkles text-indigo-500"></i>
          <h3 class="font-bold text-gray-800">Creative DNA</h3>
       </div>
       
       <div class="space-y-4">
            <!-- Hook -->
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium text-gray-600">Hook Score (3s)</span>
                    <span class="font-bold text-indigo-600">{{ data.creative_metrics.hook_score }}/100</span>
                </div>
                <div class="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                    <div class="h-full bg-indigo-500 transition-all duration-1000" :style="{width: data.creative_metrics.hook_score + '%'}"></div>
                </div>
            </div>

            <!-- Pacing -->
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium text-gray-600">Pacing Score</span>
                    <span class="font-bold text-purple-600">{{ data.creative_metrics.pacing_score }}/100</span>
                </div>
                <div class="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                    <div class="h-full bg-purple-500 transition-all duration-1000" :style="{width: data.creative_metrics.pacing_score + '%'}"></div>
                </div>
            </div>

            <div class="flex justify-between items-center py-2 border-t border-gray-100 mt-2">
                <span class="text-sm font-medium text-gray-600">Safe Zone</span>
                <span v-if="data.creative_metrics.safe_zone" class="px-3 py-1 rounded-full bg-green-50 text-green-600 text-xs font-bold border border-green-100">Compliant</span>
                <span v-else class="px-3 py-1 rounded-full bg-red-50 text-red-500 text-xs font-bold border border-red-100">X Violation</span>
            </div>
             <div class="flex justify-between items-center py-2 border-t border-gray-100">
                <span class="text-sm font-medium text-gray-600">Duration</span>
                <span class="text-sm font-bold text-gray-800">{{ data.creative_metrics.duration_seconds }}s</span>
            </div>
       </div>
    </div>
  </div>
</template>

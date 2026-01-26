<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';

const emit = defineEmits(['start', 'success', 'error']);
const props = defineProps({
  isLoading: Boolean
});

const formData = ref({
  industry: 'Ecommerce',
  target_cpa: 50,
  budget: 2500,
  country: 'US',
  landing_page_url: '',
  audience_age: 'All Ages',
  audience_gender: 'All',
  video_url_input: '',
  video_file: null // for file object
});

const activeTab = ref('upload'); // 'upload' or 'link'

// Country Dropdown Logic
const isCountryDropdownOpen = ref(false);
const countrySearchQuery = ref('');
const countrySearchInput = ref(null);

const countries = [
    { code: 'US', name: 'United States (US)' },
    { code: 'UK', name: 'United Kingdom (UK)' },
    { code: 'ID', name: 'Indonesia (ID)' },
    { code: 'MY', name: 'Malaysia (MY)' },
    { code: 'TH', name: 'Thailand (TH)' },
    { code: 'VN', name: 'Vietnam (VN)' },
    { code: 'PH', name: 'Philippines (PH)' },
    { code: 'SG', name: 'Singapore (SG)' },
    { code: 'FR', name: 'France (FR)' },
    { code: 'DE', name: 'Germany (DE)' },
    { code: 'ES', name: 'Spain (ES)' },
    { code: 'IT', name: 'Italy (IT)' },
    { code: 'IE', name: 'Ireland (IE)' },
    { code: 'MX', name: 'Mexico (MX)' },
    { code: 'BR', name: 'Brazil (BR)' },
    { code: 'SA', name: 'Saudi Arabia (SA)' },
    { code: 'AE', name: 'United Arab Emirates (UAE)' },
    { code: 'Global', name: 'Global' }
];

const filteredCountries = computed(() => {
    if (!countrySearchQuery.value) return countries;
    const query = countrySearchQuery.value.toLowerCase();
    return countries.filter(c => c.name.toLowerCase().includes(query) || c.code.toLowerCase().includes(query));
});

const selectedCountryLabel = computed(() => {
    const c = countries.find(c => c.code === formData.value.country);
    return c ? c.name : formData.value.country;
});

const selectCountry = (country) => {
    formData.value.country = country.code;
    isCountryDropdownOpen.value = false;
    countrySearchQuery.value = '';
};

// Watch Target CPA to Auto Update Budget
const updateBudget = () => {
    formData.value.budget = formData.value.target_cpa * 50;
};

const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
        // Vercel Limit Check (Warn only on prod, but allow local)
        const sizeMB = file.size / (1024 * 1024);
        if (sizeMB > 100) {
            alert(`File too large (${sizeMB.toFixed(1)}MB). Limit is 100MB. Please use Video Link.`);
            event.target.value = ''; // clear
            return;
        }
        formData.value.video_file = file;
    }
};

const submitForm = async () => {
    emit('start');
    
    // Create FormData
    const data = new FormData();
    data.append('industry_id', formData.value.industry);
    data.append('target_cpa', formData.value.target_cpa);
    data.append('budget', formData.value.budget);
    data.append('country', formData.value.country);
    data.append('audience_age', formData.value.audience_age);
    data.append('audience_gender', formData.value.audience_gender);
    
    if (formData.value.landing_page_url) {
        data.append('landing_page_url', formData.value.landing_page_url);
    }

    if (activeTab.value === 'link' && formData.value.video_url_input) {
        data.append('video_url_input', formData.value.video_url_input);
    } else if (activeTab.value === 'upload' && formData.value.video_file) {
        data.append('video_file', formData.value.video_file);
    }

    if (!formData.value.video_file && !formData.value.video_url_input && !formData.value.landing_page_url) {
        emit('error', 'Please provide either a Video or Landing Page.');
        return;
    }

    try {
        const res = await axios.post('/api/analyze', data, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        emit('success', res.data);
    } catch (err) {
        console.error(err);
        let msg = "Analysis Failed";
        if (err.response && err.response.data && err.response.data.detail) {
            msg = err.response.data.detail;
        } else if (err.message) {
            msg = err.message;
        }
        emit('error', msg);
    }
};

const industries = [
    { id: 'Ecommerce', label: 'Ecommerce ($325)', cpa: 325 },
    { id: 'Finance', label: 'Finance ($750)', cpa: 750 },
    { id: 'Beauty', label: 'Beauty ($350)', cpa: 350 },
    { id: 'FnB', label: 'Food & Beverage ($260)', cpa: 260 },
    { id: 'Tech', label: 'Tech/SaaS ($500)', cpa: 500 },
    { id: 'Travel', label: 'Travel ($380)', cpa: 380 },
    { id: 'Health', label: 'Health & Wellness ($68)', cpa: 68 },
    { id: 'Fashion', label: 'Fashion ($325)', cpa: 325 },
    { id: 'Education', label: 'Education ($85)', cpa: 85 },
    { id: 'Gaming', label: 'Gaming ($20)', cpa: 20 },
    { id: 'Other', label: 'Other ($50)', cpa: 50 }
];

// Industry Dropdown Logic
const isIndustryDropdownOpen = ref(false);
const industrySearchQuery = ref('');
const industrySearchInput = ref(null);

const filteredIndustries = computed(() => {
    if (!industrySearchQuery.value) return industries;
    const query = industrySearchQuery.value.toLowerCase();
    return industries.filter(i => i.label.toLowerCase().includes(query));
});

const selectedIndustryLabel = computed(() => {
    const i = industries.find(i => i.id === formData.value.industry);
    return i ? i.label : formData.value.industry;
});

const selectIndustry = (industry) => {
    formData.value.industry = industry.id;
    formData.value.target_cpa = industry.cpa; // Auto-update CPA
    updateBudget(); // Update Budget based on new CPA
    isIndustryDropdownOpen.value = false;
    industrySearchQuery.value = '';
};
</script>

<template>
  <div class="bg-white p-6 rounded-2xl shadow-sm border border-indigo-50">
    <div class="flex items-center gap-2 mb-6">
      <i class="fa-solid fa-sliders text-indigo-500"></i>
      <h2 class="font-bold text-gray-800">AI Score Analysis</h2>
    </div>

    <form @submit.prevent="submitForm" class="space-y-5">
      <!-- Industry -->
      <div class="relative">
        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Industry</label>
        
         <!-- Custom Dropdown Trigger -->
         <div @click="isIndustryDropdownOpen = !isIndustryDropdownOpen" class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 text-gray-700 flex justify-between items-center cursor-pointer hover:bg-gray-100 transition-all">
            <span class="font-medium truncate">{{ selectedIndustryLabel }}</span>
            <i class="fa-solid fa-chevron-down text-gray-400 text-xs transition-transform" :class="{'rotate-180': isIndustryDropdownOpen}"></i>
         </div>

         <!-- Dropdown Menu -->
         <div v-if="isIndustryDropdownOpen" class="absolute z-50 w-full mt-2 bg-white rounded-xl shadow-xl border border-indigo-50 max-h-60 flex flex-col overflow-hidden animate-fade-in-down">
            <!-- Search Input -->
            <div class="p-2 border-b border-gray-100 bg-gray-50">
               <div class="relative">
                  <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs"></i>
                  <input 
                    ref="industrySearchInput"
                    v-model="industrySearchQuery" 
                    type="text" 
                    placeholder="Search industry..." 
                    class="w-full pl-8 pr-3 py-2 bg-white rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    @click.stop
                  >
               </div>
            </div>
            
            <!-- Options List -->
            <div class="overflow-y-auto flex-1">
               <div 
                  v-for="ind in filteredIndustries" 
                  :key="ind.id"
                  @click="selectIndustry(ind)"
                  class="px-4 py-2 hover:bg-indigo-50 cursor-pointer flex items-center justify-between group transition-colors"
                  :class="{'bg-indigo-50/50': formData.industry === ind.id}"
               >
                  <span class="text-sm font-medium text-gray-700 group-hover:text-indigo-700">{{ ind.label }}</span>
                  <span v-if="formData.industry === ind.id" class="text-indigo-600"><i class="fa-solid fa-check"></i></span>
               </div>
               <div v-if="filteredIndustries.length === 0" class="p-4 text-center text-gray-400 text-xs">
                  No industries found
               </div>
            </div>
         </div>
         
         
         <!-- Backdrop to close -->
         <div v-if="isIndustryDropdownOpen" @click="isIndustryDropdownOpen = false" class="fixed inset-0 z-40 cursor-default"></div>
      </div>

      <!-- CPA & Budget -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Target CPA ($)</label>
          <input type="number" v-model="formData.target_cpa" @input="updateBudget" class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 text-gray-700 font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all">
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Budget ($)</label>
          <input type="number" v-model="formData.budget" class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 text-gray-700 font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all">
        </div>
      </div>

      <!-- Country -->
      <div class="relative">
         <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Country</label>
         
         <!-- Custom Dropdown Trigger -->
         <div @click="isCountryDropdownOpen = !isCountryDropdownOpen" class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 text-gray-700 flex justify-between items-center cursor-pointer hover:bg-gray-100 transition-all">
            <span class="font-medium truncate">{{ selectedCountryLabel }}</span>
            <i class="fa-solid fa-chevron-down text-gray-400 text-xs transition-transform" :class="{'rotate-180': isCountryDropdownOpen}"></i>
         </div>

         <!-- Dropdown Menu -->
         <div v-if="isCountryDropdownOpen" class="absolute z-50 w-full mt-2 bg-white rounded-xl shadow-xl border border-indigo-50 max-h-60 flex flex-col overflow-hidden animate-fade-in-down">
            <!-- Search Input -->
            <div class="p-2 border-b border-gray-100 bg-gray-50">
               <div class="relative">
                  <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs"></i>
                  <input 
                    ref="countrySearchInput"
                    v-model="countrySearchQuery" 
                    type="text" 
                    placeholder="Search country..." 
                    class="w-full pl-8 pr-3 py-2 bg-white rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    @click.stop
                  >
               </div>
            </div>
            
            <!-- Options List -->
            <div class="overflow-y-auto flex-1">
               <div 
                  v-for="country in filteredCountries" 
                  :key="country.code"
                  @click="selectCountry(country)"
                  class="px-4 py-2 hover:bg-indigo-50 cursor-pointer flex items-center justify-between group transition-colors"
                  :class="{'bg-indigo-50/50': formData.country === country.code}"
               >
                  <span class="text-sm font-medium text-gray-700 group-hover:text-indigo-700">{{ country.name }}</span>
                  <span v-if="formData.country === country.code" class="text-indigo-600"><i class="fa-solid fa-check"></i></span>
               </div>
               <div v-if="filteredCountries.length === 0" class="p-4 text-center text-gray-400 text-xs">
                  No countries found
               </div>
            </div>
         </div>
         
         <!-- Backdrop to close -->
         <div v-if="isCountryDropdownOpen" @click="isCountryDropdownOpen = false" class="fixed inset-0 z-40 cursor-default"></div>
      </div>

      <!-- Gender & Age -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Gender</label>
          <select v-model="formData.audience_gender" class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-medium">
            <option value="All">All</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Age</label>
          <select v-model="formData.audience_age" class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-medium">
            <option value="All Ages">All Ages</option>
            <option value="18-24">18-24</option>
            <option value="25-34">25-34</option>
            <option value="35-44">35-44</option>
            <option value="45+">45+</option>
          </select>
        </div>
      </div>

      <!-- Landing Page -->
      <div>
         <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Landing Page URL</label>
         <input type="url" v-model="formData.landing_page_url" placeholder="https://..." class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all">
      </div>

      <!-- Creative Asset -->
      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Creative Asset</label>
        
        <!-- Tabs -->
        <div class="flex bg-gray-100 p-1 rounded-xl mb-3">
            <button type="button" @click="activeTab='upload'" :class="{'bg-white shadow text-indigo-600': activeTab==='upload', 'text-gray-500': activeTab!=='upload'}" class="flex-1 py-1.5 text-xs font-bold rounded-lg transition-all">Upload</button>
            <button type="button" @click="activeTab='link'" :class="{'bg-white shadow text-indigo-600': activeTab==='link', 'text-gray-500': activeTab!=='link'}" class="flex-1 py-1.5 text-xs font-bold rounded-lg transition-all">Video Link</button>
        </div>

        <div v-if="activeTab === 'upload'">
            <div class="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:bg-gray-50 transition-colors cursor-pointer relative">
                <input type="file" accept="video/*" @change="handleFileChange" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer">
                <i class="fa-solid fa-cloud-arrow-up text-gray-400 text-2xl mb-2"></i>
                <p class="text-xs text-gray-500 font-medium">{{ formData.video_file ? formData.video_file.name : 'Click to Upload Video' }}</p>
                <p class="text-[10px] text-gray-400 mt-1">Max 100MB (Local), 4.5MB (Vercel)</p>
            </div>
        </div>

        <div v-if="activeTab === 'link'">
             <input type="url" v-model="formData.video_url_input" placeholder="https://v16-tt4b.tiktokcdn.com/..." class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 text-gray-700 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-mono">
             <p class="text-[10px] text-gray-400 mt-1 ml-1">Direct link to video file (mp4)</p>
        </div>
      </div>

      <!-- Submit Button -->
      <button :disabled="isLoading" type="submit" class="w-full bg-gradient-to-r from-indigo-600 to-indigo-500 text-white p-4 rounded-xl font-bold shadow-lg shadow-indigo-200 hover:shadow-indigo-300 transform hover:-translate-y-0.5 transition-all text-sm flex items-center justify-center gap-2">
         <span v-if="!isLoading">Analyze</span>
         <span v-else><i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing...</span>
      </button>

    </form>
  </div>
</template>

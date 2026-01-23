import mongoose from 'mongoose';

const AnalysisResultSchema = new mongoose.Schema({
    timestamp: {
        type: Date,
        default: Date.now
    },
    campaign_context: {
        industry: String,
        target_cpa: Number,
        budget: Number,
        country: String,
        landing_page_url: String,
        video_url: String
    },
    results: {
        benchmark_score: Number,
        dna_score: Number,
        predictive_score: Number,
        final_rating: String,
        is_safe: Boolean,
        policy_reason: String,
        creative_metrics: {
            hook: Number,
            pacing: Number,
            safe_zone: Boolean,
            duration: Number
        }
    }
}, { timestamps: true });

export default mongoose.model('AnalysisResult', AnalysisResultSchema);

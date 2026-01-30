import AnalysisResult from '../models/AnalysisResult.mjs';
import { ScoringEngine } from '../services/scoringService.mjs';
import { BenchmarkService } from '../services/benchmarkService.mjs';

export class WebhookController {
    static async handleN8nResult(req, res) {
        try {
            console.log("[Webhook] Received N8N Callback:", JSON.stringify(req.body));

            const { analysis_id, policy_results, n8n_status, error_message } = req.body;

            if (!analysis_id) {
                return res.status(400).json({ error: "Missing analysis_id" });
            }

            const analysisRecord = await AnalysisResult.findById(analysis_id);
            if (!analysisRecord) {
                return res.status(404).json({ error: "Analysis record not found" });
            }

            if (n8n_status === 'FAILED' || error_message) {
                analysisRecord.status = 'FAILED';
                analysisRecord.results.policy_reason = error_message || "N8N process failed";
                await analysisRecord.save();
                return res.json({ status: "ok", message: "Record marked as FAILED" });
            }

            // Extract results
            const videoPolicy = policy_results?.video || { is_safe: true, reason: "N8N Video Skipped/Passed" };
            const lpPolicy = policy_results?.landing_page || { is_safe: true, reason: "N8N LP Skipped/Passed" };

            // Aggregation Logic (Similar to original AnalysisController)
            const isSafe = videoPolicy.is_safe && lpPolicy.is_safe;
            const reasons = [];
            if (!videoPolicy.is_safe) reasons.push(`Video: ${videoPolicy.reason}`);
            if (!lpPolicy.is_safe) reasons.push(`LP: ${lpPolicy.reason}`);
            const reasonStr = reasons.length ? reasons.join('; ') : "Policy Safe";

            // Recalculate Scores if needed (though context is saved in DB)
            // We use the PREVIOUSLY saved creative_metrics (from client)
            const creativeRes = analysisRecord.results.creative_metrics;
            const context = analysisRecord.campaign_context;

            const benchmarkScore = BenchmarkService.calculateBenchmarkScore(context.target_cpa, context.industry);
            const dnaScore = ScoringEngine.calculateDnaScore(creativeRes);
            const predictiveScore = isSafe
                ? ScoringEngine.calculateFinalScore(benchmarkScore, dnaScore)
                : 0.0;
            const finalRating = ScoringEngine.getRating(predictiveScore, isSafe);

            // Update Record
            analysisRecord.status = 'COMPLETED';
            analysisRecord.results.benchmark_score = benchmarkScore;
            analysisRecord.results.dna_score = dnaScore;
            analysisRecord.results.predictive_score = predictiveScore;
            analysisRecord.results.final_rating = finalRating;
            analysisRecord.results.is_safe = isSafe;
            analysisRecord.results.policy_reason = reasonStr;

            await analysisRecord.save();
            console.log(`[Webhook] Analysis ${analysis_id} COMPLETED.`);

            res.json({ ...req.body, status: "ok", message: "Analysis updated successfully" });

        } catch (error) {
            console.error("[Webhook] Error processing callback:", error);
            res.status(500).json({ error: error.message });
        }
    }
}

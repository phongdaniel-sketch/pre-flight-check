import AnalysisResult from '../models/AnalysisResult.js';
import { ScoringEngine } from '../services/scoringService.js';
import { BenchmarkService } from '../services/benchmarkService.js';

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

            // Extract and Normalize results
            const videoPolicy = policy_results?.video || { is_safe: true, reason: "N8N Video Skipped/Passed" };
            const lpPolicy = policy_results?.landing_page || { is_safe: true, reason: "N8N LP Skipped/Passed" };

            // Helper to safe cast to boolean
            const toBool = (val) => String(val).toLowerCase() === 'true';

            const videoSafe = toBool(videoPolicy.is_safe);
            const lpSafe = toBool(lpPolicy.is_safe);
            const videoReason = videoPolicy.reason || "";
            const lpReason = lpPolicy.reason || "";

            // Check for explicit violations OR manual review flags in text
            const isVideoFlagged = !videoSafe || videoReason.includes('Flagged') || videoReason.includes('Review');
            const isLpFlagged = !lpSafe || lpReason.includes('Flagged') || lpReason.includes('Review');

            const reasons = [];
            if (isVideoFlagged) reasons.push(`Video: ${videoReason}`);
            if (isLpFlagged) reasons.push(`LP: ${lpReason}`);
            const reasonStr = reasons.length ? reasons.join('; ') : "Policy Safe";

            // Aggregation Logic
            // Note: Manual Review (Yellow) is considered "Safe" for scoring purposes, but has a flagged reason.
            const isSafe = videoSafe && lpSafe;

            // Recalculate Scores if needed (though context is saved in DB)
            // We use the PREVIOUSLY saved creative_metrics (from client)
            const creativeRes = analysisRecord.results.creative_metrics;
            const context = analysisRecord.campaign_context;

            const benchmarkScore = BenchmarkService.calculateBenchmarkScore(context.target_cpa, context.industry);
            const dnaScore = ScoringEngine.calculateDnaScore(creativeRes);
            const predictiveScore = isSafe
                ? ScoringEngine.calculateFinalScore(benchmarkScore, dnaScore)
                : 0.0;

            // Determine Final Rating
            // Force Yellow if Manual Review is required but score classified it as Green
            let finalRating = ScoringEngine.getRating(predictiveScore, isSafe);
            if (isSafe && (isVideoFlagged || isLpFlagged) && finalRating === 'Green') {
                finalRating = 'Yellow';
            }

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

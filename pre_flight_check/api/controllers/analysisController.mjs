import { BenchmarkService } from '../services/benchmarkService.mjs';
import { N8nClient } from '../services/n8nService.mjs';
import { ScoringEngine } from '../services/scoringService.mjs';
import AnalysisResult from '../models/AnalysisResult.mjs';

export class AnalysisController {
    static async analyze(req, res) {
        try {
            // 1. Extract Form Data
            const {
                industry_id, target_cpa, country, budget,
                landing_page_url, video_url_input,
                creative_metrics
            } = req.body || {};

            // Basic Validation
            if (!industry_id || !target_cpa || !budget) {
                return res.status(422).json({ detail: "Missing required fields (industry_id, target_cpa, budget)" });
            }

            const videoUrl = video_url_input ? video_url_input.trim() : "";

            // 2. Create PENDING Database Record Immediately
            const benchmarkScore = BenchmarkService.calculateBenchmarkScore(Number(target_cpa), industry_id);
            const clientCreative = creative_metrics || {};
            const creativeRes = {
                hook_score: clientCreative.hook_score || 0,
                pacing_score: clientCreative.pacing_score || 0,
                safe_zone: clientCreative.safe_zone || false,
                duration_seconds: clientCreative.duration_seconds || 0
            };
            const dnaScore = ScoringEngine.calculateDnaScore(creativeRes);

            const newAnalysis = await AnalysisResult.create({
                campaign_context: {
                    industry: industry_id,
                    target_cpa: Number(target_cpa),
                    budget: Number(budget),
                    country,
                    landing_page_url: landing_page_url || "",
                    video_url: videoUrl || ""
                },
                results: {
                    benchmark_score: benchmarkScore,
                    dna_score: dnaScore,
                    predictive_score: 0, // Pending
                    final_rating: "Pending",
                    is_safe: true, // Optimistic default
                    policy_reason: "Pending Analysis...",
                    creative_metrics: creativeRes
                },
                status: 'PENDING'
            });

            const analysisId = newAnalysis._id.toString();
            console.log(`[Controller] Analysis ${analysisId} Created (Pending). Triggering Hybrid N8N...`);

            // 3. Trigger N8N (Hybrid Strategy)
            const n8n = new N8nClient();

            // Construct Callback URL
            const protocol = req.headers['x-forwarded-proto'] || 'https';
            const host = req.headers.host;
            const callbackUrl = `${protocol}://${host}/api/webhook/n8n-result`;

            const triggerData = {
                analysis_id: analysisId,
                callback_url: callbackUrl,
                video_url: videoUrl,
                landing_page_url: landing_page_url,
                industry: industry_id,
                country
            };

            // Hybrid Call: Wait 50s for Sync response
            const syncResult = await n8n.triggerHybridAnalysis(triggerData);

            if (syncResult) {
                // Scenario A: Fast Response (Sync)
                console.log(`[Controller] Sync Response Success for ${analysisId}`);

                // Since WebhookController already processed the data (and echoed it back),
                // we fetch the updated record from the DB to ensure consistency.
                const updatedAnalysis = await AnalysisResult.findById(analysisId);

                return res.json({
                    message: "Analysis Completed",
                    analysis_id: analysisId,
                    status: updatedAnalysis.status,
                    results: updatedAnalysis.results
                });

            } else {
                // Scenario B: Timeout (Async)
                console.log(`[Controller] Timeout for ${analysisId}. Switching to Async.`);

                // Return 202 Accepted
                return res.status(202).json({
                    message: "Analysis continuing in background",
                    analysis_id: analysisId,
                    status: "PENDING"
                });
            }

        } catch (error) {
            console.error("Controller Error:", error);
            res.status(500).json({ detail: error.message });
        }
    }

    static async getStatus(req, res) {
        try {
            const { id } = req.params;
            const analysis = await AnalysisResult.findById(id);

            if (!analysis) {
                return res.status(404).json({ detail: "Analysis not found" });
            }

            res.json({
                status: analysis.status,
                results: analysis.results,
                message: analysis.results.policy_reason
            });

        } catch (error) {
            res.status(500).json({ detail: error.message });
        }
    }
}

import fs from 'fs';
import path from 'path';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { BenchmarkService } from '../services/benchmarkService.js';
import { N8nClient } from '../services/n8nService.js';
import { CreativeAnalyzer } from '../services/creativeAnalyzer.js';
import { ScoringEngine } from '../services/scoringService.js';
import AnalysisResult from '../models/AnalysisResult.js';

export class AnalysisController {
    static async analyze(req, res) {
        try {
            // 1. Extract Form Data
            const {
                industry_id, target_cpa, country, budget,
                landing_page_url, video_url_input,
                creative_metrics // [NEW] Client-side metrics
            } = req.body || {};

            // Basic Validation
            if (!industry_id || !target_cpa || !budget) {
                return res.status(422).json({ detail: "Missing required fields (industry_id, target_cpa, budget)" });
            }

            // 2. Handle Video Input
            let videoUrl = video_url_input ? video_url_input.trim() : "";
            let hasVideo = !!videoUrl;

            // 3. Benchmark Calculation
            const benchmarkScore = BenchmarkService.calculateBenchmarkScore(Number(target_cpa), industry_id);

            // 4. Parallel Analysis
            const n8n = new N8nClient();
            const campaignContext = {
                industry: industry_id,
                country,
                target_cpa,
                budget,
                lp: landing_page_url
            };

            const promises = [];

            // Video Policy Analysis (N8N)
            if (hasVideo) {
                promises.push(n8n.analyzeVideo(videoUrl, campaignContext));
            } else {
                promises.push(Promise.resolve(null));
            }

            // LP Analysis (N8N)
            if (landing_page_url) {
                promises.push(n8n.analyzeLandingPage(landing_page_url));
            } else {
                promises.push(Promise.resolve(null));
            }

            // Server-Side Creative Analysis Removed. 
            // We use `creative_metrics` from Client.

            const results = await Promise.all(promises);
            const videoResult = results[0];
            const lpResult = results[1];

            // 5. Aggregation
            let videoPolicySafe = true;
            let videoPolicyReason = "";

            if (videoResult && videoResult.policy) {
                videoPolicySafe = videoResult.policy.is_safe;
                videoPolicyReason = videoResult.policy.reason;
            }

            let lpPolicySafe = true;
            let lpPolicyReason = "";

            if (lpResult && lpResult.policy) {
                lpPolicySafe = lpResult.policy.is_safe;
                lpPolicyReason = lpResult.policy.reason;
            }

            const finalIsSafe = videoPolicySafe && lpPolicySafe;
            const finalReasons = [];
            if (!videoPolicySafe) finalReasons.push(`Video: ${videoPolicyReason}`);
            if (!lpPolicySafe) finalReasons.push(`LP: ${lpPolicyReason}`);

            const reasonStr = finalReasons.length ? finalReasons.join('; ') : "Policy Safe";

            // Creative Metrics (From Client)
            const clientCreative = creative_metrics || {};
            const creativeRes = {
                hook_score: clientCreative.hook_score || 0,
                pacing_score: clientCreative.pacing_score || 0,
                safe_zone: clientCreative.safe_zone || false,
                duration_seconds: clientCreative.duration_seconds || 0
            };

            // 6. Scoring
            const dnaScore = ScoringEngine.calculateDnaScore(creativeRes);
            const predictiveScore = finalIsSafe
                ? ScoringEngine.calculateFinalScore(benchmarkScore, dnaScore)
                : 0.0;
            const finalRating = ScoringEngine.getRating(predictiveScore, finalIsSafe);

            // 7. Cleanup (No local file cleanup needed as we didn't download)

            // 8. Save to DB
            try {
                await AnalysisResult.create({
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
                        predictive_score: predictiveScore,
                        final_rating: finalRating,
                        is_safe: finalIsSafe,
                        policy_reason: reasonStr,
                        creative_metrics: creativeRes
                    }
                });
                console.log("Analysis Result Saved to DB");
            } catch (dbError) {
                console.error("DB Save Failed:", dbError.message);
                // Don't fail the request if DB save fails
            }

            res.json({
                benchmark_score: benchmarkScore,
                policy_check: { is_safe: finalIsSafe, reason: reasonStr },
                creative_metrics: creativeRes,
                dna_score: dnaScore,
                predictive_score: predictiveScore,
                final_rating: finalRating,
                message: `Analysis Complete. ${reasonStr}`
            });

        } catch (error) {
            console.error("Controller Error:", error);
            res.status(500).json({ detail: error.message });
        }
    }
}

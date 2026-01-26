import axios from 'axios';
import dotenv from 'dotenv';
dotenv.config();

export class N8nClient {
    constructor() {
        this.videoWebhookUrl = "https://n88n.ecomdymedia.com/webhook/45c08981-0739-4c4f-82f5-61402bff42de";
        this.lpWebhookUrl = process.env.N8N_LP_WEBHOOK_URL;
    }

    async analyzeVideo(videoUrl, campaignContext) {
        if (!this.videoWebhookUrl) return { policy: { is_safe: true, reason: "N8N URL Invalid" } };

        const payload = {
            creative_videos: [{
                video_preview_url: videoUrl
            }]
        };

        try {
            console.log(`[N8N] Sending Video to: ${this.videoWebhookUrl}`);
            // Increase timeout to 5 minutes for long video processing
            const response = await axios.post(this.videoWebhookUrl, payload, { timeout: 300000 });
            const data = response.data;

            console.log("[DEBUG] N8N Video Raw Response:", JSON.stringify(data));

            const videoReviews = data.creative_videos_review || [];
            let isSafe = true;
            let reason = "N8N Policy Check Passed";

            if (videoReviews.length > 0) {
                const review = videoReviews[0];
                const analysisResult = review.TextAnalysisResult || "Unknown";
                const recommendation = review.Recommendation || "";

                if (analysisResult === "Non-Compliant" || recommendation.includes("Reject")) {
                    isSafe = false;
                    const details = review.ViolationDetails || review.TextViolationDetails || "";
                    const violationType = review.ViolationType || review.TextViolationType || "Policy Violation";
                    reason = details ? `${violationType}: ${details}` : violationType;
                } else if (analysisResult === "Flagged for Review") {
                    isSafe = false;
                    const details = review.ViolationDetails || review.TextViolationDetails || "";
                    reason = details ? `Flagged for Manual Review: ${details}` : "Flagged for Manual Review";
                }
            }

            return {
                policy: { is_safe: isSafe, reason: reason },
                creative: {}
            };

        } catch (error) {
            console.error(`Error calling n8n Video: ${error.message}`);
            return {
                policy: { is_safe: false, reason: `Video Analysis Failed: ${error.message}` },
                creative: {}
            };
        }
    }

    async analyzeLandingPage(landingPageUrl) {
        if (!this.lpWebhookUrl) {
            console.warn("WARNING: N8N_LP_WEBHOOK_URL not set. Using mock data.");
            return { policy: { is_safe: true, reason: "[MOCK-LP] Landing Page Safe" } };
        }

        const payload = { landingPages: [landingPageUrl] };

        try {
            const response = await axios.post(this.lpWebhookUrl, payload, { timeout: 30000 });
            const data = response.data;
            console.log("[DEBUG] N8N LP Raw Response:", JSON.stringify(data));

            const reviews = data.landing_pages_review || [];
            if (reviews.length > 0) {
                const review = reviews[0];
                const status = review.AnalysisResult || "Unknown";
                const isCompliant = status.toLowerCase() === "compliant";
                const reason = isCompliant ? "Landing Page Compliant" : (review.ViolationDetails || review.Recommendation || "Policy Violation");

                return {
                    policy: { is_safe: isCompliant, reason: reason }
                };
            }

            return {
                policy: data.policy || { is_safe: false, reason: "Invalid response format from Policy Check" }
            };

        } catch (error) {
            console.error(`Error calling n8n LP: ${error.message}`);
            return {
                policy: { is_safe: false, reason: `LP Analysis Failed: ${error.message}` }
            };
        }
    }
}

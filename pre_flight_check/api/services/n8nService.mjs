import axios from 'axios';
import dotenv from 'dotenv';
dotenv.config();

export class N8nClient {
    constructor() {
        this.videoWebhookUrl = process.env.N8N_VIDEO_WEBHOOK_URL || "https://n88n.ecomdymedia.com/webhook/45c08981-0739-4c4f-82f5-61402bff42de";
        this.lpWebhookUrl = process.env.N8N_LP_WEBHOOK_URL || "https://n88n.ecomdymedia.com/webhook/62490610-0585-4e53-8678-fe6da7ade707";
    }

    /**
     * Triggers N8N with a Hybrid Strategy (Sync first, then Async).
     * @param {Object} triggerData - { analysis_id, callback_url, ... }
     * @returns {Promise<Object|null>} - Returns data if sync success, null if timeout.
     */
    async triggerHybridAnalysis(triggerData) {
        // Use Video Webhook if video is present, otherwise fallback to LP Webhook
        const url = triggerData.video_url ? this.videoWebhookUrl : this.lpWebhookUrl;

        if (!url) throw new Error("N8N Webhook URL not configured");

        console.log(`[N8N] Hybrid Trigger to ${url} (Video: ${!!triggerData.video_url})`);

        try {
            const httpsAgent = new (await import('https')).Agent({ keepAlive: true });

            // Soft Timeout: 50s (Wait for Sync Response)
            const response = await axios.post(url, triggerData, {
                timeout: 50000,
                httpsAgent
            });

            console.log("[N8N] Hybrid: Sync Response Received!");
            return response.data;

        } catch (error) {
            if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
                console.warn("[N8N] Hybrid: Timeout (50s) reached. Switching to Async callback mode.");
                return null; // Signal to Controller: "Accepted" (Async)
            }
            console.error(`[N8N] Hybrid: Error - ${error.message}`);
            throw error; // Real error (DNS, 500, etc)
        }
    }
}

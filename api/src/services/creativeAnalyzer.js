import axios from 'axios';

export class CreativeAnalyzer {
    constructor() { }

    async analyzeRemote(videoUrl) {
        console.log("Calling Python Video Analysis Service...");
        try {
            // Determine API Base URL
            // In Production: `https://${process.env.VERCEL_URL}`
            // Fallback for local: 'http://localhost:8000' (if serving python manually, otherwise this will fail gracefully)

            const baseUrl = process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:8000';
            const apiUrl = `${baseUrl}/api/analyze`;

            console.log(`Target Python Endpoint: ${apiUrl}`);

            const response = await axios.post(apiUrl, { video_url: videoUrl }, { timeout: 60000 });
            return response.data; // Expected { creative: { ... } }

        } catch (error) {
            console.error("Python Analysis Failed:", error.message);
            // Fallback for when Python service is unavailable
            return {
                creative: {
                    hook: 0,
                    pacing: 0,
                    safe_zone: false,
                    duration: 0,
                    details: { error: "Analysis Service Unavailable" }
                }
            };
        }
    }
}

export class VideoAnalysisService {
    /**
     * Analyzes a video file directly in the browser.
     * @param {File} file - The video file object.
     * @returns {Promise<Object>} - The creative metrics.
     */
    static async analyzeVideo(file) {
        return new Promise((resolve, reject) => {
            const video = document.createElement('video');
            video.preload = 'metadata';
            video.muted = true;
            video.playsInline = true;

            const objectUrl = URL.createObjectURL(file);
            video.src = objectUrl;

            // Analysis State
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d', { willReadFrequently: true });

            // Configuration
            const SAMPLE_RATE_SEC = 0.5; // Check every 0.5s for scene changes

            let duration = 0;
            const sceneCuts = [];
            let prevHist = null;

            video.onloadedmetadata = () => {
                duration = video.duration;
                canvas.width = 64; // Low res for speed
                canvas.height = 64;

                // Start processing frames
                processFrames();
            };

            video.onerror = (e) => {
                URL.revokeObjectURL(objectUrl);
                reject(new Error("Video load failed"));
            };

            const processFrames = async () => {
                try {
                    const times = [];
                    for (let t = 0; t < duration; t += SAMPLE_RATE_SEC) {
                        times.push(t);
                    }
                    // Limit to first 30s to be fast
                    if (times.length > 60) times.length = 60;

                    for (const t of times) {
                        await seekTo(video, t);
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                        const frameData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                        const hist = calculateHistogram(frameData);

                        if (prevHist) {
                            const diff = compareHistograms(prevHist, hist);
                            // Threshold: approx 15% change in pixel distribution
                            // 64*64*3 = 12288 pixels. Max diff = 12288 * 255.
                            // 0.15 * (12288 * 255) approx 470,000
                            if (diff > 400000) {
                                sceneCuts.push(t);
                            }
                        }
                        prevHist = hist;
                    }

                    // Done
                    URL.revokeObjectURL(objectUrl);
                    resolve(calculateMetrics(duration, sceneCuts));

                } catch (err) {
                    URL.revokeObjectURL(objectUrl);
                    console.error("Client Analysis Error:", err);
                    // Fallback
                    resolve({
                        hook_score: 50,
                        pacing_score: 50,
                        safe_zone: true,
                        duration_seconds: duration,
                        details: { error: err.message }
                    });
                }
            };
        });
    }
}

function seekTo(video, time) {
    return new Promise(resolve => {
        const onSeeked = () => {
            video.removeEventListener('seeked', onSeeked);
            resolve();
        };
        video.addEventListener('seeked', onSeeked);
        video.currentTime = time;
    });
}

function calculateHistogram(data) {
    // Simple RGB histogram
    // 3 channels * 16 bins = 48 values
    const bins = 16;
    const binSize = 256 / bins;
    const hist = new Array(3 * bins).fill(0);

    for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];

        hist[Math.floor(r / binSize)]++;
        hist[bins + Math.floor(g / binSize)]++;
        hist[2 * bins + Math.floor(b / binSize)]++;
    }
    return hist;
}

function compareHistograms(h1, h2) {
    let diff = 0;
    for (let i = 0; i < h1.length; i++) {
        diff += Math.abs(h1[i] - h2[i]);
    }
    return diff;
}

function calculateMetrics(duration, sceneCuts) {
    const numScenes = sceneCuts.length + 1;
    const pacingRate = numScenes > 0 ? duration / numScenes : duration;

    // Pacing Score (Same logic as backend)
    let pacingScore = 50;
    if (pacingRate >= 1.5 && pacingRate <= 2.5) {
        pacingScore = 100;
    } else if (pacingRate > 4.0) {
        pacingScore = 40;
    } else if (pacingRate > 2.5) {
        pacingScore = 100 - 40 * (pacingRate - 2.5);
        pacingScore = Math.max(40, pacingScore);
    } else {
        pacingScore = 80;
    }

    // Hook Score (First 3s)
    let hook_score = 30; // Base
    const fastCuts = sceneCuts.filter(t => t <= 3.0).length > 0;
    if (fastCuts) hook_score += 40;

    // Duration Hook (Short videos < 5s are bad hooks generally? Or good? Platform dependent)
    // Leaving logic simple.

    return {
        hook_score: Math.min(hook_score, 100),
        pacing_score: Math.round(pacingScore),
        safe_zone: true, // Placeholder
        duration_seconds: Math.round(duration),
        details: {
            scene_count: numScenes,
            pacing_rate: pacingRate.toFixed(2)
        }
    };
}

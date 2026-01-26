import ffmpeg from 'fluent-ffmpeg';
import pathToFfmpeg from 'ffmpeg-static';
import pathToFfprobe from 'ffprobe-static';
import fs from 'fs';

// Set ffmpeg & ffprobe paths
ffmpeg.setFfmpegPath(pathToFfmpeg);
ffmpeg.setFfprobePath(pathToFfprobe.path);

export class CreativeAnalyzer {
    constructor(videoPath) {
        if (!fs.existsSync(videoPath)) {
            throw new Error(`Video file not found at: ${videoPath}`);
        }
        this.videoPath = videoPath;
    }

    async runFullAnalysis() {
        console.log("Starting Local Analysis (Node.js + ffmpeg)...");
        try {
            const metadata = await this.getMetadata();
            const duration = metadata.format.duration;

            // Detect Scenes
            const scenes = await this.detectScenes();
            const numScenes = scenes.length + 1;

            // Calculate Metrics
            const pacingRate = numScenes > 0 ? duration / numScenes : duration;
            let pacingScore = 50;

            // Pacing Logic
            if (pacingRate >= 1.5 && pacingRate <= 2.5) {
                pacingScore = 100;
            } else if (pacingRate > 4.0) {
                pacingScore = 40;
            } else if (pacingRate > 2.5) {
                // Linear interpolation: 2.5 -> 100, 4.0 -> 40
                // y = mx + c
                // m = (40 - 100) / (4.0 - 2.5) = -60 / 1.5 = -40
                pacingScore = 100 - 40 * (pacingRate - 2.5);
                pacingScore = Math.max(40, pacingScore);
            } else {
                pacingScore = 80; // Fast pacing < 1.5
            }

            // Hook Logic (First 3s)
            let hookScore = 30; // Baseline
            const fastCuts = scenes.filter(s => s <= 3.0).length > 0;
            if (fastCuts) {
                hookScore += 40;
            }
            // Cannot easily detect "Human" or "Text" without AI/OpenCV heavy models.
            // Keeping consistent with Python "Lite" version.

            return {
                creative: {
                    hook: Math.min(hookScore, 100),
                    pacing: Math.round(pacingScore),
                    safe_zone: true, // Placeholder
                    duration: Number(duration),
                    details: {
                        scene_count: numScenes,
                        pacing_rate: pacingRate.toFixed(2)
                    }
                }
            };
        } catch (error) {
            console.error("Analysis Failed:", error);
            return { creative: {} };
        }
    }

    getMetadata() {
        return new Promise((resolve, reject) => {
            ffmpeg.ffprobe(this.videoPath, (err, metadata) => {
                if (err) reject(err);
                else resolve(metadata);
            });
        });
    }

    detectScenes() {
        return new Promise((resolve, reject) => {
            const scenes = [];
            ffmpeg(this.videoPath)
                .inputOptions(['-t 10']) // LIMIT ANALYSIS TO FIRST 10 SECONDS to prevent Timeout
                .videoFilters("select='gt(scene,0.3)',showinfo")
                .format('null')
                .on('stderr', (stderrLine) => {
                    // Parse stderr for showinfo
                    // Line format: ... n:   8 pts:  26692 pts_time:0.33365 ...
                    if (stderrLine.includes('pts_time:')) {
                        const match = stderrLine.match(/pts_time:([0-9.]+)/);
                        if (match && match[1]) {
                            scenes.push(parseFloat(match[1]));
                        }
                    }
                })
                .on('end', () => {
                    resolve(scenes);
                })
                .on('error', (err) => {
                    console.error("FFmpeg Error:", err);
                    resolve([]); // Fallback to 0 scenes
                })
                .save('/dev/null');
        });
    }
}

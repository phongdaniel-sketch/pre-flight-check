export class ScoringEngine {
    static calculateDnaScore(creative) {
        // DNA Score = Hook*0.6 + Pacing*0.4
        // Ensure values are numbers
        const hook = Number(creative.hook_score) || 0;
        const pacing = Number(creative.pacing_score) || 0;

        return (hook * 0.6) + (pacing * 0.4);
    }

    static calculateFinalScore(benchmarkScore, dnaScore) {
        // PredictiveScore = (DNA * 0.7) + (Benchmark * 0.3)
        const weightedScore = (dnaScore * 0.7) + (benchmarkScore * 0.3);
        return Number(weightedScore.toFixed(2));
    }

    static getRating(score, isSafe) {
        if (!isSafe) {
            return "Red"; // Policy Violation
        }
        if (score > 80) {
            return "Green";
        } else if (score >= 50) {
            return "Yellow";
        } else {
            return "Red";
        }
    }
}

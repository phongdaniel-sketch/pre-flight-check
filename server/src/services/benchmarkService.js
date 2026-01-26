// Industry Average CPA Benchmarks (Estimated 2025)
const INDUSTRY_BENCHMARKS = {
    'finance': 750.0,
    'ecommerce': 325.0,
    'beauty': 350.0,
    'fnb': 260.0,
    'tech': 500.0,
    'travel': 380.0,
    'other': 50.0
};

export class BenchmarkService {
    static calculateBenchmarkScore(targetCpa, industryId) {
        const avgCpa = INDUSTRY_BENCHMARKS[industryId.toLowerCase()] || 50.0;

        if (avgCpa === 0) return 0.0;

        // Formula: min(100, (Target_CPA / Industry_Avg_CPA) * 100)
        let score = (targetCpa / avgCpa) * 100;
        return Math.min(100.0, score);
    }
}

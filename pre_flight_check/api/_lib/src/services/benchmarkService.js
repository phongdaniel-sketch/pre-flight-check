// Industry Average CPA Benchmarks (Estimated 2025)
const INDUSTRY_BENCHMARKS = {
    'education': 85.0,
    'vehicles & transportation': 150.0,
    'baby & kids products': 60.0,
    'financial services': 750.0,
    'beauty & personal care': 350.0,
    'tech & electronics': 500.0,
    'appliances': 120.0,
    'travel': 380.0,
    'household products': 50.0,
    'pets': 45.0,
    'apps': 25.0,
    'home improvement': 100.0,
    'apparel & accessories': 80.0,
    'news & entertainment': 30.0,
    'business services': 200.0,
    'games': 20.0,
    'life services': 80.0,
    'food & beverage': 60.0,
    'sports & outdoors': 90.0,
    'e-commerce (non-app)': 325.0
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

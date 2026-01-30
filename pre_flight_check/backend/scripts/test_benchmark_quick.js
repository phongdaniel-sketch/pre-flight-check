import { BenchmarkService } from './src/services/benchmarkService.js';

console.log("🧪 Testing Benchmark Service Logic...");

const testCases = [
    { industry: 'e-commerce (non-app)', cpa: 50, expected: 15.38 },
    { industry: 'e-commerce (non-app)', cpa: 325, expected: 100.0 },
    { industry: 'financial services', cpa: 200, expected: 26.67 },
    { industry: 'games', cpa: 15, expected: 75.0 }
];

testCases.forEach(test => {
    const score = BenchmarkService.calculateBenchmarkScore(test.cpa, test.industry);
    const pass = Math.abs(score - test.expected) < 0.1; // Float tolerance

    console.log(`\nTest Case: ${test.industry} (Target CPA: $${test.cpa})`);
    console.log(`Expected: ${test.expected}`);
    console.log(`Actual:   ${score.toFixed(2)}`);
    console.log(`Status:   ${pass ? '✅ PASS' : '❌ FAIL'}`);
});

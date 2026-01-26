# Tool Pre-flight Check – Creative Scorer

## 1. Mục tiêu của Tool
Dự báo khả năng **đạt Target CPA** của một chiến dịch TikTok Ads *trước khi chạy* bằng cách kết hợp:
- Policy (An toàn)
- Benchmark ngành (Tài chính)
- Chất lượng Creative (AI phân tích)

## 2. Input (Đầu vào từ người dùng)
### 2.1 Thông tin Campaign
- Industry ID
- Target CPA
- Country
- Audience (Age/Gender)
- Ngân sách dự kiến

Required Budget = 50 × Target CPA

### 2.2 Tài nguyên
- Video gốc
- Landing Page

## 3. Processing
### Step 1: Benchmark Validation
Benchmark Score = min(100, (Target_CPA / Industry_Avg_CPA) × 100)

### Step 2: Policy Check (n8n)
Webhook trả về is_safe + reason

### Step 3: AI Creative Analysis (Gemini)
- Hook Score
- Pacing Score
- Safe Zone
- Duration

DNA Score = Hook×0.6 + Pacing×0.4

### Step 4: Predictive Score
PredictiveScore = P × ((D×0.7)+(B×0.3))

## 4. Output
- Green (>80)
- Yellow (50–80)
- Red (<50)

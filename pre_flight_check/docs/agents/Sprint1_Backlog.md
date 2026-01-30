Sprint1_Backlog.md

```
# Sprint 1 Backlog - Pre-flight Check Platform MVP

## Objective:
Build foundational MVP features enabling users to upload video or Landing Page URL, perform policy compliance analysis via N8N, apply AI for creative scoring, and predict campaign CPA and ROAS. Tech stack: Vue.js, Node.js, N8N, Firebase.

## Backlog Items:

1. Upload Video / Landing Page Link  
- User uploads advertising video (mp4, mov) or inputs Landing Page URL to start analysis.  
- Tasks: Vue.js upload UI, Node.js API backend for validation, Firebase Firestore for metadata, Firebase Storage for videos, basic validation rules.

2. Policy Analysis via N8N  
- Analyze advertising content for TikTok policy compliance.  
- Tasks: Design N8N workflow triggered by backend API, analyze content with keyword/forbidden checks, save results in Firebase, display compliance results on frontend.

3. AI-Based Creative Scoring  
- Provide AI-driven score for creative quality assessment.  
- Tasks: Basic AI scoring integration (placeholder/simple ML), backend calls after policy check, store scores and feedback in Firebase, show score and insights in UI.

4. Predict CPA and ROAS  
- Estimate Cost-per-Acquisition (CPA) and Return on Ad Spend (ROAS) for ad content.  
- Tasks: Simple predictive model or rule-based logic, backend prediction endpoint after creative scoring, store predictions in Firebase, display metrics on dashboard.

## Deferred Features:
- Advanced AI/deep learning models  
- Complex policy scanning  
- Analytics dashboards  
- User and campaign management  
- Notifications and alerts

```

User_Stories.json

```json
[
  {
    "id": "US01",
    "title": "Upload Video or Landing Page Link",
    "description": "As a user, I want to upload an advertising video file or enter a Landing Page URL so that I can start the advertising content analysis.",
    "acceptance_criteria": [
      "User can upload video file (mp4, mov) on frontend.",
      "User can enter valid Landing Page URL.",
      "Backend validates and stores upload metadata.",
      "Video files stored securely in Firebase Storage."
    ]
  },
  {
    "id": "US02",
    "title": "Policy Analysis via N8N",
    "description": "As a user, I want the system to analyze uploaded content for TikTok policy compliance automatically.",
    "acceptance_criteria": [
      "N8N workflow triggers on new content upload.",
      "Policy checks performed for forbidden content and keywords.",
      "Results returned to backend and stored in Firebase.",
      "Compliance results shown on frontend UI."
    ]
  },
  {
    "id": "US03",
    "title": "AI-Based Creative Scoring",
    "description": "As a user, I want to receive an AI-generated creative quality score for my ad content.",
    "acceptance_criteria": [
      "AI scoring service integrated with backend.",
      "Scores and feedback saved to Firebase.",
      "Frontend displays creative score and summaries."
    ]
  },
  {
    "id": "US04",
    "title": "Predict CPA and ROAS",
    "description": "As a user, I want the platform to predict important campaign metrics CPA and ROAS based on my ad content.",
    "acceptance_criteria": [
      "Simple predictive model implemented in backend.",
      "Predictions stored in Firebase.",
      "Metrics displayed clearly in frontend dashboard."
    ]
  }
]
```
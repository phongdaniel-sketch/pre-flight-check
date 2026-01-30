```javascript
// Backend Sprint 1 Source Code - Node.js Express + Firebase Admin SDK

// File: server.js
const express = require('express');
const multer = require('multer');
const admin = require('firebase-admin');
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');
const cors = require('cors');

// Initialize Firebase Admin SDK
const serviceAccount = require('./firebase-service-account.json');
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  storageBucket: 'your-firebase-project.appspot.com'
});
const db = admin.firestore();
const bucket = admin.storage().bucket();

const app = express();
app.use(cors());
app.use(bodyParser.json());

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 500 * 1024 * 1024 }, // 500MB max
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['video/mp4', 'video/quicktime', 'video/mov'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Unsupported file type. Allowed: mp4, mov.'));
    }
  }
});

// Helper function: Validate URL
function isValidURL(url) {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// 1. Upload Video or Landing Page Link Endpoint
app.post('/api/upload-content', upload.single('videoFile'), async (req, res) => {
  try {
    const { type, landingPageUrl } = req.body;

    if (type === 'video') {
      if (!req.file) {
        return res.status(400).json({ error: 'No video file uploaded' });
      }

      // Generate unique filename with uuid
      const fileName = `videos/${uuidv4()}_${req.file.originalname}`;
      const file = bucket.file(fileName);

      // Upload video to Firebase Storage
      await file.save(req.file.buffer, {
        metadata: {
          contentType: req.file.mimetype,
          firebaseStorageDownloadTokens: uuidv4()
        }
      });

      const videoUrl = `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o/${encodeURIComponent(fileName)}?alt=media`;

      // Store metadata in Firestore
      const docRef = await db.collection('uploads').add({
        type: 'video',
        fileName,
        videoUrl,
        uploadedAt: admin.firestore.FieldValue.serverTimestamp(),
        policyAnalysis: null,
        creativeScore: null,
        forecast: null
      });

      return res.status(200).json({ 
        message: 'Video uploaded successfully', 
        uploadId: docRef.id,
        videoUrl
      });

    } else if (type === 'landingPage') {
      // Validate Landing Page URL
      if (!landingPageUrl || !isValidURL(landingPageUrl)) {
        return res.status(400).json({ error: 'Invalid Landing Page URL' });
      }

      // Store Landing Page URL in Firestore
      const docRef = await db.collection('uploads').add({
        type: 'landingPage',
        landingPageUrl,
        uploadedAt: admin.firestore.FieldValue.serverTimestamp(),
        policyAnalysis: null,
        creativeScore: null,
        forecast: null
      });

      return res.status(200).json({
        message: 'Landing Page URL uploaded successfully',
        uploadId: docRef.id
      });
      
    } else {
      return res.status(400).json({ error: 'Invalid content type; must be video or landingPage' });
    }

  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Internal server error during upload' });
  }
});

// 2. Trigger Policy Analysis (simulate calling N8N workflow)
// In a real scenario, this could be a webhook or HTTP request to trigger N8N flow.
// For MVP, we simulate policy results here.

app.post('/api/policy-analysis/:uploadId', async (req, res) => {
  try {
    const uploadId = req.params.uploadId;
    const uploadDoc = await db.collection('uploads').doc(uploadId).get();

    if (!uploadDoc.exists) {
      return res.status(404).json({ error: 'Upload not found' });
    }

    // Simulated policy check results:
    const policyResults = [
      { policyName: 'No prohibited content', status: 'Passed', note: '' },
      { policyName: 'No misleading claims', status: 'Passed', note: '' },
      { policyName: 'No adult content', status: 'Passed', note: '' }
    ];

    // For demonstration, randomly fail one policy 10% of time
    if (Math.random() < 0.1) {
      policyResults[1].status = 'Failed';
      policyResults[1].note = 'Detected potential misleading claim.';
    }

    // Overall status
    const anyFailed = policyResults.some(p => p.status === 'Failed');
    const overallStatus = anyFailed ? 'Vi phạm' : 'Passed';

    // Update Firestore doc with policy results
    await db.collection('uploads').doc(uploadId).update({
      policyAnalysis: {
        status: overallStatus,
        details: policyResults,
        analyzedAt: admin.firestore.FieldValue.serverTimestamp()
      }
    });

    return res.status(200).json({
      message: 'Policy analysis complete',
      policyAnalysis: {
        status: overallStatus,
        details: policyResults
      }
    });
  } catch (error) {
    console.error('Policy analysis error:', error);
    res.status(500).json({ error: 'Internal server error during policy analysis' });
  }
});

// 3. AI-Based Creative Scoring (placeholder)

// Simulate a simple score between 60 and 95
function generateCreativeScore() {
  return {
    overallScore: Math.floor(60 + Math.random() * 35),
    factors: {
      imageCreativity: Math.floor(60 + Math.random() * 40),
      headlineAppeal: Math.floor(60 + Math.random() * 40),
      contentRelevance: Math.floor(60 + Math.random() * 40)
    }
  };
}

app.post('/api/creative-scoring/:uploadId', async (req, res) => {
  try {
    const uploadId = req.params.uploadId;
    const uploadDoc = await db.collection('uploads').doc(uploadId).get();

    if (!uploadDoc.exists) {
      return res.status(404).json({ error: 'Upload not found' });
    }

    // Simulate AI scoring
    const scoreData = generateCreativeScore();

    await db.collection('uploads').doc(uploadId).update({
      creativeScore: {
        score: scoreData.overallScore,
        factors: scoreData.factors,
        scoredAt: admin.firestore.FieldValue.serverTimestamp()
      }
    });

    return res.status(200).json({
      message: 'Creative scoring complete',
      creativeScore: scoreData
    });
  } catch (error) {
    console.error('Creative scoring error:', error);
    res.status(500).json({ error: 'Internal server error during creative scoring' });
  }
});

// 4. Predict CPA and ROAS (simple rule-based logic)

app.post('/api/forecast/:uploadId', async (req, res) => {
  try {
    const uploadId = req.params.uploadId;
    const uploadDocSnap = await db.collection('uploads').doc(uploadId).get();

    if (!uploadDocSnap.exists) {
      return res.status(404).json({ error: 'Upload not found' });
    }

    const uploadData = uploadDocSnap.data();

    // Simple prediction logic based on creativeScore if available
    let predictedCPA = 25000; // default
    let predictedROAS = 150; // in percent
    let confidence = 3; // 1 to 5 stars

    if (uploadData.creativeScore) {
      const score = uploadData.creativeScore.score;

      // higher creative score => lower CPA, higher ROAS
      predictedCPA = Math.max(10000, Math.round(40000 - score * 250));
      predictedROAS = Math.min(400, Math.round(score * 4));
      confidence = Math.min(5, Math.max(1, Math.floor(score / 20)));
    }

    // Store forecast in Firestore
    await db.collection('uploads').doc(uploadId).update({
      forecast: {
        predictedCPA,
        predictedROAS,
        confidence,
        forecastedAt: admin.firestore.FieldValue.serverTimestamp()
      }
    });

    return res.status(200).json({
      message: 'Forecast completed',
      forecast: {
        predictedCPA,
        predictedROAS,
        confidence
      }
    });
  } catch (error) {
    console.error('Forecast error:', error);
    res.status(500).json({ error: 'Internal server error during forecasting' });
  }
});

// 5. Fetch all results for frontend display
app.get('/api/results/:uploadId', async (req, res) => {
  try {
    const uploadId = req.params.uploadId;
    const doc = await db.collection('uploads').doc(uploadId).get();

    if (!doc.exists) {
      return res.status(404).json({ error: 'Upload not found' });
    }

    return res.status(200).json({ data: doc.data() });
  } catch (error) {
    console.error('Fetch results error:', error);
    res.status(500).json({ error: 'Internal server error fetching results' });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Pre-flight Check Backend API is running on port ${PORT}`);
});

```

---

# API Documentation for Sprint 1 Backend

## Base URL

```
http://<server-domain>:<port>/api/
```

---

## 1. POST /upload-content

Upload advertising content: video file or Landing Page URL.

### Request

- Multipart/form-data

Fields:

| Field          | Type      | Required | Description                                  |
|----------------|-----------|----------|----------------------------------------------|
| type           | string    | yes      | 'video' for video upload, 'landingPage' for URL |
| videoFile      | file      | conditionally required | Required if type='video'. Video file (mp4, mov). Max 500MB. |
| landingPageUrl | string    | conditionally required | Required if type='landingPage'. Valid URL string. |

### Response

```json
{
  "message": "Video uploaded successfully",
  "uploadId": "string",
  "videoUrl": "string"  // only for video upload
}
```

Or error status with message.

---

## 2. POST /policy-analysis/:uploadId

Trigger policy analysis for upload with ID.

### Request

- Parameters: uploadId (string) - upload document ID in Firestore

- Body: none

### Response

```json
{
  "message": "Policy analysis complete",
  "policyAnalysis": {
    "status": "Passed" | "Vi phạm",
    "details": [
      {
        "policyName": "string",
        "status": "Passed" | "Failed",
        "note": "string"  // optional if failed
      }
    ]
  }
}
```

---

## 3. POST /creative-scoring/:uploadId

Trigger AI-based creative scoring for upload.

### Request

- Parameters: uploadId (string)

- Body: none

### Response

```json
{
  "message": "Creative scoring complete",
  "creativeScore": {
    "overallScore": 0-100,
    "factors": {
      "imageCreativity": 0-100,
      "headlineAppeal": 0-100,
      "contentRelevance": 0-100
    }
  }
}
```

---

## 4. POST /forecast/:uploadId

Trigger CPA and ROAS forecasting for upload.

### Request

- Parameters: uploadId (string)

- Body: none

### Response

```json
{
  "message": "Forecast completed",
  "forecast": {
    "predictedCPA": number,   // in VND
    "predictedROAS": number,  // in %
    "confidence": number      // 1 to 5 stars rating
  }
}
```

---

## 5. GET /results/:uploadId

Fetch all stored data for specified upload: metadata, policy, scoring, forecast.

### Request

- Parameters: uploadId (string)

### Response

```json
{
  "data": {
    "type": "video" | "landingPage",
    "fileName": "string",    // if video
    "videoUrl": "string",    // if video
    "landingPageUrl": "string", // if landing page
    "uploadedAt": "timestamp",
    "policyAnalysis": {
      "status": "Passed" | "Vi phạm",
      "details": [
        {
          "policyName": "string",
          "status": "Passed" | "Failed",
          "note": "string"
        }
      ],
      "analyzedAt": "timestamp"
    },
    "creativeScore": {
      "score": number,
      "factors": {
        "imageCreativity": number,
        "headlineAppeal": number,
        "contentRelevance": number
      },
      "scoredAt": "timestamp"
    },
    "forecast": {
      "predictedCPA": number,
      "predictedROAS": number,
      "confidence": number,
      "forecastedAt": "timestamp"
    }
  }
}
```

---

# Notes

- All API responses use JSON format.
- Errors return appropriate HTTP status codes (400 for invalid input, 404 for not found, 500 for server error).
- Firebase Firestore is used for document persistence.
- Firebase Storage handles video file storage securely.
- Multer handles file upload with validation on file types and size.
- Simple simulated logic is used for policy analysis, creative scoring, and forecasting for MVP.
- Integration with N8N workflow can replace the simulated policy analysis endpoint in future sprints.

---

This completes Sprint 1 backend development source code and API documentation suitable for frontend integration and QA testing.

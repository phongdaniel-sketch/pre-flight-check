import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { AnalysisController } from '../controllers/analysisController.mjs';
import { WebhookController } from '../controllers/webhookController.mjs';

const router = express.Router();

// Configure Multer
const uploadDir = process.env.VERCEL ? "/tmp" : path.join(process.cwd(), "static/uploads");
// Ensure dir exists
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadDir)
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9)
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname))
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 100 * 1024 * 1024 } // 100MB limit
});

// Routes
router.post('/analyze', upload.single('video_file'), AnalysisController.analyze);

router.get('/analysis/:id', AnalysisController.getStatus);

router.post('/webhook/n8n-result', WebhookController.handleN8nResult);

router.post('/webhook/callback', (req, res) => {
    console.log("\n[CALLBACK RECEIVED] Data from n8n:", JSON.stringify(req.body, null, 2));
    res.json({ status: "received" });
});

export default router;

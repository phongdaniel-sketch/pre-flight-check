import express from 'express';
import multer from 'multer';
import path from 'path';
import { AnalysisController } from '../controllers/analysisController.js';

const router = express.Router();

// Configure Multer
const uploadDir = process.env.VERCEL ? "/tmp" : path.join(process.cwd(), "src/uploads");
// Ensure dir exists
import fs from 'fs';
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
    limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Routes
router.post('/analyze', upload.single('video_file'), AnalysisController.analyze);

router.post('/webhook/callback', (req, res) => {
    console.log("\n[CALLBACK RECEIVED] Data from n8n:", JSON.stringify(req.body, null, 2));
    res.json({ status: "received" });
});

export default router;

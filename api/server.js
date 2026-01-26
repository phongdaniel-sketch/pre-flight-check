import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import multer from 'multer';
import path from 'path';

dotenv.config();

const app = express();
const port = process.env.PORT || 8000;

import apiRoutes from './src/routes/apiRoutes.js';
import { connectDB } from './src/config/db.js';

process.on('uncaughtException', (err) => {
    console.log('UNCAUGHT EXCEPTION! 💥 Shutting down...');
    console.log(err.name, err.message);
    process.exit(1);
});

connectDB();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve Uploads (for N8N to potentially access if on same network)
// In Vercel, this is read-only except /tmp, but we can serve if it exists
app.use('/uploads', express.static(path.join(process.cwd(), 'api/src/uploads')));    // Adjusted for Vercel/API context

// API Routes
app.use('/api', apiRoutes);

// Health Check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'Pre-flight Check Backend (Node.js)' });
});

// For Local Dev
if (!process.env.VERCEL) {
    app.listen(port, () => {
        console.log(`Server running at http://localhost:${port}`);
    });
}

export default app;

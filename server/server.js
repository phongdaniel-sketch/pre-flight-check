import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import multer from 'multer';
import os from 'path';

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

// Serve Uploads (for N8N to potentially access if on same network)
app.use('/uploads', express.static('src/uploads'));

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

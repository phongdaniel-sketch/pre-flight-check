import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import multer from 'multer';
import path from 'path';

import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const app = express();
const port = process.env.PORT || 8000;

import apiRoutes from './routes/apiRoutes.js';
import { connectDB } from './config/db.js';

process.on('uncaughtException', (err) => {
    console.log('UNCAUGHT EXCEPTION! 💥 Shutting down...');
    console.log(err.name, err.message);
    process.exit(1);
});

console.log('Attempting to connect to DB...');
connectDB().then(() => console.log('DB Connected')).catch(err => console.error('DB Connection Failed:', err));

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve Uploads (for N8N to potentially access if on same network)
// In Vercel, this is read-only except /tmp, but we can serve if it exists
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// API Routes
app.use('/api', apiRoutes);

// Health Check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'Pre-flight Check Backend (Node.js)' });
});

import { exec } from 'child_process';
app.get('/api/debug-ls', (req, res) => {
    exec('ls -R', (err, stdout, stderr) => {
        res.send(`<pre>CWD: ${process.cwd()}\n\n${stdout}</pre>`);
    });
});

// For Local Dev
if (!process.env.VERCEL) {
    app.listen(port, () => {
        console.log(`Server running at http://localhost:${port}`);
    });
}

export default app;

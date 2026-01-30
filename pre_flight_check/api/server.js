import express from 'express';
import cors from 'cors';

const app = express();

import apiRoutes from './routes/apiRoutes.js';
import { connectDB } from './config/db.js';

// DB Connection (Temporarily disabled for isolation test)
// connectDB().catch(err => console.error('DB Initial Connection Error:', err));

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health Check (Direct)
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'Pre-flight Check Backend (Node.js)' });
});

// API Routes
app.use('/api', apiRoutes);

// For Local Dev
if (!process.env.VERCEL) {
    const port = process.env.PORT || 8000;
    app.listen(port, () => {
        console.log(`Server running at http://localhost:${port}`);
    });
}

export default app;

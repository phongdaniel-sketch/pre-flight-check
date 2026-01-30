import app from '../backend/src/server.js';

export default async (req, res) => {
    // Immediate verification endpoint
    if (req.url?.includes('/ping')) {
        return res.json({ status: "pong", architecture: "esm-mjs" });
    }
    return app(req, res);
};

export const config = {
    maxDuration: 300,
};

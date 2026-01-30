export default async (req, res) => {
    // Immediate verification endpoint (isolated from server.js crashes)
    if (req.url?.includes('/ping')) {
        return res.json({ status: "pong", architecture: "esm-mjs-dynamic" });
    }

    try {
        const { default: app } = await import('./server.mjs');
        return app(req, res);
    } catch (err) {
        console.error('SERVER_IMPORT_ERROR:', err);
        return res.status(500).json({
            error: "Failed to load backend",
            message: err.message,
            stack: err.stack
        });
    }
};

export const config = {
    maxDuration: 300,
};

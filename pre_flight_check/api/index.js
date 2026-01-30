// Bridge: Vercel CommonJS entry point -> ESM Backend
const appPromise = import('../backend/src/server.js').then(m => m.default);

module.exports = async (req, res) => {
    const app = await appPromise;
    return app(req, res);
};

// Vercel function configuration
module.exports.config = {
    maxDuration: 300,
};

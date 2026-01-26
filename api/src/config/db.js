import mongoose from 'mongoose';

export const connectDB = async () => {
    try {
        const conn = await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/pre-flight-check', {
            serverSelectionTimeoutMS: 5000 // Fail fast (5s) to avoid Vercel timeout
        });
        console.log(`MongoDB Connected: ${conn.connection.host}`);
    } catch (error) {
        console.error(`Error: ${error.message}`);
        console.warn("Continuing without Database connection...");
        // process.exit(1); // Do not crash on serverless
    }
};

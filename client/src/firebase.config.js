import { initializeApp } from "firebase/app";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
    apiKey: "AIzaSyB5D7Z65IxXR_SgROx4CRlzVvtLuldsCs4",
    authDomain: "tiktok-analytics-ai-01.firebaseapp.com",
    projectId: "tiktok-analytics-ai-01",
    storageBucket: "tiktok-analytics-ai-01.firebasestorage.app",
    messagingSenderId: "1052395949781",
    appId: "1:1052395949781:web:668e3d272ccf6737271c5c"
};

const app = initializeApp(firebaseConfig);
export const storage = getStorage(app);

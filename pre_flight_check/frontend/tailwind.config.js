/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'cream': '#FDFBF7',
                'pastel-mint': '#34D399',
                'pastel-canary': '#FCD34D',
                'pastel-coral': '#F87171',
                'pastel-sky': '#38BDF8',
            },
        },
    },
    plugins: [],
}

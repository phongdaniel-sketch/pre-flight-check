
(async () => {
    console.log('Start dynamic imports');
    try {
        await import('express'); console.log('Imported express');
        await import('cors'); console.log('Imported cors');
        await import('dotenv'); console.log('Imported dotenv');
        await import('mongoose'); console.log('Imported mongoose');
        await import('multer'); console.log('Imported multer');
        await import('openai'); console.log('Imported openai');
        await import('uuid'); console.log('Imported uuid');
        console.log('All imports done');
    } catch (e) {
        console.error('Import failed', e);
    }
})();

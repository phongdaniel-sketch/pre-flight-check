import express from 'express';
const app = express();
app.get('/', (req, res) => res.send('ok'));
app.listen(8001, () => console.log('listening 8001'));

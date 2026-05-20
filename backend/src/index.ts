import express from 'express';
import cors from 'cors';
import compression from 'compression';
import morgan from 'morgan';

import routes from './routes/index.js';

const app = express();
const port = 8080;

app.use(cors());
app.use(compression());
app.use(morgan('combined'));
app.use(express.json());

// Routes
app.use('/api', routes);
app.get('/', (req, res) => {
  res.json({ message: 'API is running' });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});



--- Database Schema (PostgreSQL) ---

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high');
CREATE TYPE task_status AS ENUM ('To Do', 'In Progress', 'Done');

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  due_date DATE,
  priority task_priority NOT NULL DEFAULT 'medium',
  status task_status NOT NULL DEFAULT 'To Do',
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

--- Backend Source Code (Node.js + Express) ---

**Dependencies:**

```bash
npm install express pg bcrypt jsonwebtoken joi dotenv cors
```

**src/models/db.js**

```js
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});
module.exports = pool;
```

**src/middleware/authMiddleware.js**

```js
const jwt = require('jsonwebtoken');
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  if (!authHeader) return res.status(401).json({ error: 'Authorization header missing' });
  const token = authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token missing' });
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid token' });
    req.user = user;
    next();
  });
};
module.exports = authenticateToken;
```

**src/controllers/authController.js**

```js
const pool = require('../models/db');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Joi = require('joi');

const registerSchema = Joi.object({ username: Joi.string().min(3).max(50).required(), email: Joi.string().email().required(), password: Joi.string().min(6).required() });
const loginSchema = Joi.object({ email: Joi.string().email().required(), password: Joi.string().required() });

exports.register = async (req, res) => {
  try {
    const { error, value } = registerSchema.validate(req.body);
    if (error) return res.status(400).json({ error: error.details[0].message });
    const { username, email, password } = value;
    const userCheck = await pool.query('SELECT id FROM users WHERE email = $1 OR username = $2', [email, username]);
    if (userCheck.rows.length) return res.status(409).json({ error: 'User with given email or username already exists' });
    const hash = await bcrypt.hash(password, 10);
    const newUser = await pool.query('INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3) RETURNING id, username, email, created_at', [username, email, hash]);
    return res.status(201).json({ message: 'User registered', user: newUser.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.login = async (req, res) => {
  try {
    const { error, value } = loginSchema.validate(req.body);
    if (error) return res.status(400).json({ error: error.details[0].message });
    const { email, password } = value;
    const userRes = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (!userRes.rows.length) return res.status(401).json({ error: 'Invalid email or password' });
    const user = userRes.rows[0];
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) return res.status(401).json({ error: 'Invalid email or password' });
    const tokenPayload = { id: user.id, username: user.username, email: user.email };
    const token = jwt.sign(tokenPayload, process.env.JWT_SECRET, { expiresIn: '1h' });
    res.status(200).json({ message: 'Login successful', token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.logout = (req, res) => {
  res.status(200).json({ message: 'Logout successful' });
};
```

**src/controllers/taskController.js**

```js
const pool = require('../models/db');
const Joi = require('joi');

const taskSchema = Joi.object({
  title: Joi.string().max(255).required(),
  description: Joi.string().allow(''),
  due_date: Joi.date().optional(),
  priority: Joi.string().valid('low','medium','high').default('medium'),
  status: Joi.string().valid('To Do','In Progress','Done').default('To Do'),
});

const updateStatusSchema = Joi.object({ status: Joi.string().valid('To Do','In Progress','Done').required() });

exports.createTask = async (req, res) => {
  try {
    const { error, value } = taskSchema.validate(req.body);
    if (error) return res.status(400).json({ error: error.details[0].message });
    const { title, description, due_date, priority, status } = value;
    const user_id = req.user.id;
    const result = await pool.query(`INSERT INTO tasks (title,description,due_date,priority,status,user_id) VALUES ($1,$2,$3,$4,$5,$6) RETURNING *`,
      [title, description, due_date, priority, status, user_id]);
    res.status(201).json({ message: 'Task created', task: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.listTasks = async (req, res) => {
  try {
    const user_id = req.user.id;
    const { status } = req.query;
    let query = 'SELECT * FROM tasks WHERE user_id = $1';
    let params = [user_id];
    if (status) {
      if (!['To Do','In Progress','Done'].includes(status)) return res.status(400).json({ error: 'Invalid status filter' });
      query += ' AND status = $2'; params.push(status);
    }
    query += ' ORDER BY created_at DESC';
    const result = await pool.query(query, params);
    res.status(200).json({ tasks: result.rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.getTask = async (req, res) => {
  try {
    const { taskId } = req.params;
    const user_id = req.user.id;
    const result = await pool.query('SELECT * FROM tasks WHERE id = $1 AND user_id = $2', [taskId, user_id]);
    if (!result.rows.length) return res.status(404).json({ error: 'Task not found' });
    res.status(200).json({ task: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.updateTask = async (req, res) => {
  try {
    const { taskId } = req.params;
    const user_id = req.user.id;
    const schema = Joi.object({
      title: Joi.string().max(255),
      description: Joi.string().allow(''),
      due_date: Joi.date().allow(null),
      priority: Joi.string().valid('low','medium','high'),
      status: Joi.string().valid('To Do','In Progress','Done'),
    }).min(1);
    const { error, value } = schema.validate(req.body);
    if (error) return res.status(400).json({ error: error.details[0].message });
    const taskRes = await pool.query('SELECT * FROM tasks WHERE id = $1 AND user_id = $2', [taskId, user_id]);
    if (!taskRes.rows.length) return res.status(404).json({ error: 'Task not found' });
    const fields = Object.keys(value), values = Object.values(value);
    const setString = fields.map((f,i) => `"${f}"=$${i+1}`).join(', ');
    const queryParams = [...values, taskId, user_id];
    const query = `UPDATE tasks SET ${setString}, updated_at = NOW() WHERE id = $${fields.length+1} AND user_id = $${fields.length+2} RETURNING *`;
    const updatedTaskRes = await pool.query(query, queryParams);
    res.status(200).json({ message: 'Task updated', task: updatedTaskRes.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.deleteTask = async (req, res) => {
  try {
    const { taskId } = req.params;
    const user_id = req.user.id;
    const deleteRes = await pool.query('DELETE FROM tasks WHERE id = $1 AND user_id = $2 RETURNING *', [taskId, user_id]);
    if (!deleteRes.rows.length) return res.status(404).json({ error: 'Task not found' });
    res.status(200).json({ message: 'Task deleted' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.updateTaskStatus = async (req, res) => {
  try {
    const { taskId } = req.params;
    const user_id = req.user.id;
    const { error, value } = updateStatusSchema.validate(req.body);
    if (error) return res.status(400).json({ error: error.details[0].message });
    const { status } = value;
    const taskRes = await pool.query('SELECT * FROM tasks WHERE id=$1 AND user_id=$2', [taskId, user_id]);
    if (!taskRes.rows.length) return res.status(404).json({ error: 'Task not found' });
    const updatedStatusRes = await pool.query(
      'UPDATE tasks SET status=$1, updated_at=NOW() WHERE id=$2 AND user_id=$3 RETURNING *',
      [status, taskId, user_id]);
    res.status(200).json({ message: 'Task status updated', task: updatedStatusRes.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
};
```

**src/routes/authRoutes.js**

```js
const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

router.post('/register', authController.register);
router.post('/login', authController.login);
router.post('/logout', authController.logout);

module.exports = router;
```

**src/routes/taskRoutes.js**

```js
const express = require('express');
const router = express.Router();
const taskController = require('../controllers/taskController');
const authenticateToken = require('../middleware/authMiddleware');

router.use(authenticateToken);

router.post('/', taskController.createTask);
router.get('/', taskController.listTasks);
router.get('/:taskId', taskController.getTask);
router.patch('/:taskId', taskController.updateTask);
router.delete('/:taskId', taskController.deleteTask);
router.patch('/:taskId/status', taskController.updateTaskStatus);

module.exports = router;
```

**src/app.js**

```js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const app = express();

const authRoutes = require('./routes/authRoutes');
const taskRoutes = require('./routes/taskRoutes');

app.use(cors());
app.use(express.json());

app.use('/api/auth', authRoutes);
app.use('/api/tasks', taskRoutes);

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server listening on port ${PORT}`));
```

---

# Swagger API Specification - openapi.yaml

```yaml
openapi: 3.0.3
info:
  title: To-Do App API
  version: '1.0'
servers:
  - url: http://localhost:3000/api
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    UserRegister:
      type: object
      required: [username, email, password]
      properties:
        username:
          type: string
          example: johndoe
        email:
          type: string
          format: email
          example: johndoe@example.com
        password:
          type: string
          format: password
          example: securePass123
    UserLogin:
      type: object
      required: [email, password]
      properties:
        email:
          type: string
          format: email
          example: johndoe@example.com
        password:
          type: string
          format: password
          example: securePass123
    AuthResponse:
      type: object
      properties:
        message:
          type: string
        token:
          type: string
    Task:
      type: object
      properties:
        id:
          type: integer
        title:
          type: string
        description:
          type: string
        due_date:
          type: string
          format: date
        priority:
          type: string
          enum: [low, medium, high]
        status:
          type: string
          enum: [To Do, In Progress, Done]
        user_id:
          type: integer
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
    TaskCreate:
      type: object
      required: [title]
      properties:
        title:
          type: string
        description:
          type: string
        due_date:
          type: string
          format: date
        priority:
          type: string
          enum: [low, medium, high]
          default: medium
        status:
          type: string
          enum: [To Do, In Progress, Done]
          default: To Do
    TaskUpdate:
      type: object
      properties:
        title:
          type: string
        description:
          type: string
        due_date:
          type: string
          format: date
          nullable: true
        priority:
          type: string
          enum: [low, medium, high]
        status:
          type: string
          enum: [To Do, In Progress, Done]
    TaskStatusUpdate:
      type: object
      required: [status]
      properties:
        status:
          type: string
          enum: [To Do, In Progress, Done]
  responses:
    UnauthorizedError:
      description: Unauthorized
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
paths:
  /auth/register:
    post:
      summary: Register user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserRegister'
      responses:
        '201':
          description: Registered
        '400':
          description: Validation error
        '409':
          description: User exists
  /auth/login:
    post:
      summary: User login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserLogin'
      responses:
        '200':
          description: Success with token
        '401':
          description: Invalid credentials
  /auth/logout:
    post:
      summary: Logout user
      responses:
        '200':
          description: Logged out
  /tasks:
    post:
      summary: Create task
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskCreate'
      responses:
        '201':
          description: Created
    get:
      summary: List tasks, filter by status
      security:
        - bearerAuth: []
      parameters:
        - in: query
          name: status
          schema:
            type: string
            enum: [To Do, In Progress, Done]
      responses:
        '200':
          description: List of tasks
  /tasks/{taskId}:
    get:
      summary: Get task by ID
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: taskId
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Task found
        '404':
          description: Not found
    patch:
      summary: Update task partially
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: taskId
          required: true
          schema:
            type: integer
      requestBody:
        content:
            application/json:
              schema:
                $ref: '#/components/schemas/TaskUpdate'
      responses:
        '200':
          description: Updated
        '404':
          description: Not found
    delete:
      summary: Delete task
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: taskId
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Deleted
        '404':
          description: Not found
  /tasks/{taskId}/status:
    patch:
      summary: Update task status
      security:
        - bearerAuth: []
      parameters:
        - in: path
          name: taskId
          required: true
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskStatusUpdate'
      responses:
        '200':
          description: Status updated
        '404':
          description: Not found
```

---

**.env example**

```
DATABASE_URL=postgresql://user:password@localhost:5432/todoappdb
JWT_SECRET=your_jwt_secret_here
PORT=3000
```

---

This solution includes the database schema, all backend source code for API endpoints with validation, secure authentication, and Swagger documentation (openapi.yaml) defining the full API contract per the PRD and user stories.
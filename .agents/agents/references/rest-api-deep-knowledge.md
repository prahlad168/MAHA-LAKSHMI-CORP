# REST API Deep Knowledge - For backend-agent

## REST API Design Principles

### 1. Resource Naming

```javascript
// ✅ Good REST API endpoints
GET    /users          // Get all users
GET    /users/:id      // Get single user
POST   /users          // Create user
PUT    /users/:id      // Update user
DELETE /users/:id      // Delete user

// ✅ Nested resources
GET    /users/:id/posts        // Get user's posts
GET    /users/:id/orders       // Get user's orders
POST   /posts/:id/comments     // Add comment to post

// ✅ Query parameters for filtering
GET /posts?status=published&author=123&page=1&limit=10
GET /products?category=electronics&price_min=100&price_max=500
```

### 2. HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | No/invalid auth |
| 403 | Forbidden | Auth but no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable | Validation failed |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Internal error |

### 3. Response Format

```javascript
// ✅ Success Response
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 100
  }
}

// ✅ Error Response
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [
      { "field": "email", "message": "Email is required" }
    ]
  }
}

// ✅ Pagination Response
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "totalPages": 10,
    "hasNext": true,
    "hasPrev": false
  }
}
```

### 4. Express.js Implementation

```javascript
// app.js
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({ origin: 'https://yourdomain.com' }));
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// Body parsing
app.use(express.json({ limit: '10mb' }));

// Logging
app.use(morgan('combined'));

// Routes
app.use('/api/v1/users', require('./routes/users'));
app.use('/api/v1/posts', require('./routes/posts'));

module.exports = app;
```

### 5. Authentication with JWT

```javascript
// authController.js
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Register
async function register(req, res) {
  const { email, password, name } = req.body;
  
  // Check existing
  const existing = await User.findOne({ email });
  if (existing) {
    return res.status(409).json({ 
      success: false, 
      error: { message: 'Email already registered' }
    });
  }
  
  // Hash password
  const hashedPassword = await bcrypt.hash(password, 12);
  
  // Create user
  const user = await User.create({
    email,
    password: hashedPassword,
    name
  });
  
  // Generate token
  const token = jwt.sign(
    { userId: user.id, email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: '7d' }
  );
  
  res.status(201).json({ success: true, data: { token, user } });
}

// Login
async function login(req, res) {
  const { email, password } = req.body;
  
  const user = await User.findOne({ email });
  if (!user) {
    return res.status(401).json({ 
      success: false, 
      error: { message: 'Invalid credentials' }
    });
  }
  
  const isValid = await bcrypt.compare(password, user.password);
  if (!isValid) {
    return res.status(401).json({ 
      success: false, 
      error: { message: 'Invalid credentials' }
    });
  }
  
  const token = jwt.sign(
    { userId: user.id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '7d' }
  );
  
  res.json({ success: true, data: { token, user } });
}

// Auth middleware
function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ 
      success: false, 
      error: { message: 'No token provided' }
    });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ 
      success: false, 
      error: { message: 'Invalid token' }
    });
  }
}

// Role middleware
function roleMiddleware(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ 
        success: false, 
        error: { message: 'Insufficient permissions' }
      });
    }
    next();
  };
}
```

### 6. Validation with Joi/Zod

```javascript
// validation.js with Zod
const { z } = require('zod');

const createUserSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email format'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain uppercase')
    .regex(/[0-9]/, 'Password must contain number'),
  role: z.enum(['user', 'admin']).optional()
});

const updateUserSchema = createUserSchema.partial();

// Validation middleware
function validate(schema) {
  return (req, res, next) => {
    try {
      schema.parse(req.body);
      next();
    } catch (error) {
      const errors = error.errors.map(e => ({
        field: e.path.join('.'),
        message: e.message
      }));
      res.status(400).json({ 
        success: false, 
        error: { code: 'VALIDATION_ERROR', details: errors }
      });
    }
  };
}

// Usage in routes
router.post('/', validate(createUserSchema), userController.create);
router.put('/:id', validate(updateUserSchema), userController.update);
```

### 7. Error Handling

```javascript
// errorHandler.js
class AppError extends Error {
  constructor(message, statusCode, code) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;
  }
}

// Async handler wrapper
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Error middleware
function errorHandler(err, req, res, next) {
  console.error(err);
  
  if (err.isOperational) {
    return res.status(err.statusCode).json({
      success: false,
      error: { code: err.code, message: err.message }
    });
  }
  
  // Programming or unknown errors
  return res.status(500).json({
    success: false,
    error: { 
      code: 'INTERNAL_ERROR', 
      message: 'Something went wrong' 
    }
  });
}

// Usage
router.get('/:id', asyncHandler(async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) {
    throw new AppError('User not found', 404, 'NOT_FOUND');
  }
  res.json({ success: true, data: user });
}));
```

### 8. Database with Prisma

```javascript
// schema.prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        String   @id @default(uuid())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
}

// queries.js
const prisma = require('./prisma');

async function createUser(data) {
  return prisma.user.create({ data });
}

async function getUsers(filter = {}) {
  const { page = 1, limit = 10, search, role } = filter;
  
  const where = {};
  if (search) {
    where.OR = [
      { name: { contains: search, mode: 'insensitive' } },
      { email: { contains: search, mode: 'insensitive' } }
    ];
  }
  if (role) where.role = role;
  
  const [users, total] = await Promise.all([
    prisma.user.findMany({ where, skip: (page - 1) * limit, take: limit }),
    prisma.user.count({ where })
  ]);
  
  return { users, total, page, limit, totalPages: Math.ceil(total / limit) };
}
```

### 9. API Documentation

```javascript
// OpenAPI/Swagger
/**
 * @swagger
 * /api/v1/users:
 *   get:
 *     summary: Get all users
 *     tags: [Users]
 *     parameters:
 *       - in: query
 *         name: page
 *         schema: { type: integer }
 *       - in: query
 *         name: limit
 *         schema: { type: integer }
 *     responses:
 *       200:
 *         description: List of users
 */
```

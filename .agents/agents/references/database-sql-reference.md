# Database Deep Knowledge - For database-agent

## PostgreSQL Best Practices

### 1. Schema Design

```sql
-- Users table with constraints
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE -- Soft delete
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Posts table with foreign key
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT,
    excerpt VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Full-text search index
CREATE INDEX idx_posts_search ON posts 
USING GIN (to_tsvector('indonesian', title || ' ' || content));
```

### 2. Query Optimization

```sql
-- ✅ EXPLAIN ANALYZE - Check query performance
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT p.*, u.name as author_name
FROM posts p
INNER JOIN users u ON p.author_id = u.id
WHERE p.status = 'published'
ORDER BY p.published_at DESC
LIMIT 10;

-- ✅ Use covering index for frequently queried columns
CREATE INDEX idx_posts_published_author 
ON posts(published_at DESC, author_id) 
WHERE status = 'published';

-- ✅ Avoid SELECT *, specify columns
SELECT id, title, slug, published_at FROM posts WHERE status = 'published';

-- ✅ Use EXISTS instead of IN for subqueries
SELECT * FROM users u 
WHERE EXISTS (
    SELECT 1 FROM posts p 
    WHERE p.author_id = u.id AND p.status = 'published'
);

-- ✅ Batch inserts
INSERT INTO users (id, email, name, password_hash)
SELECT * FROM (
    VALUES 
        (gen_random_uuid(), 'user1@test.com', 'User 1', 'hash1'),
        (gen_random_uuid(), 'user2@test.com', 'User 2', 'hash2')
) AS t(id, email, name, password_hash)
ON CONFLICT (email) DO NOTHING;
```

### 3. Common Table Expressions (CTE)

```sql
-- Recursive CTE for hierarchy
WITH RECURSIVE category_tree AS (
    -- Base case
    SELECT id, name, parent_id, 1 as level
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY level, name;

-- Complex aggregation with CTE
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', created_at) as month,
        COUNT(*) as orders,
        SUM(total) as revenue
    FROM orders
    WHERE created_at >= NOW() - INTERVAL '12 months'
    GROUP BY DATE_TRUNC('month', created_at)
),
running_total AS (
    SELECT 
        month,
        orders,
        revenue,
        SUM(revenue) OVER (ORDER BY month) as cumulative_revenue
    FROM monthly_sales
)
SELECT * FROM running_total;
```

### 4. PostgreSQL Functions

```sql
-- Function for soft delete
CREATE OR REPLACE FUNCTION soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deleted_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_soft_delete
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION soft_delete();

-- Function for updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Materialized view for reports
CREATE MATERIALIZED VIEW monthly_stats AS
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE email_verified) as verified_users
FROM users
GROUP BY DATE_TRUNC('month', created_at);

CREATE UNIQUE INDEX ON monthly_stats(month);
REFRESH MATERIALIZED VIEW monthly_stats;
```

### 5. MongoDB Operations

```javascript
// Connection with Mongoose
const mongoose = require('mongoose');

mongoose.connect(process.env.MONGODB_URI, {
  maxPoolSize: 10,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
});

// Schema with validation
const userSchema = new mongoose.Schema({
  email: { 
    type: String, 
    required: true, 
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\S+@\S+\.\S+$/, 'Invalid email']
  },
  name: { type: String, required: true, minLength: 2 },
  role: { type: String, enum: ['user', 'admin'], default: 'user' },
  createdAt: { type: Date, default: Date.now }
}, { timestamps: true });

// Indexes
userSchema.index({ email: 1 }, { unique: true });
userSchema.index({ createdAt: -1 });
userSchema.index({ 'posts.title': 'text' });

// Aggregation pipeline
async function getUserStats(userId) {
  return mongoose.model('User').aggregate([
    { $match: { _id: new mongoose.Types.ObjectId(userId) } },
    {
      $lookup: {
        from: 'posts',
        localField: '_id',
        foreignField: 'author',
        as: 'posts'
      }
    },
    {
      $project: {
        name: 1,
        email: 1,
        totalPosts: { $size: '$posts' },
        publishedPosts: {
          $size: {
            $filter: {
              input: '$posts',
              as: 'post',
              cond: { $eq: ['$$post.status', 'published'] }
            }
          }
        }
      }
    }
  ]);
}
```

### 6. Redis Caching

```javascript
// Redis client setup
const { createClient } = require('redis');
const client = createClient({
  url: process.env.REDIS_URL
});
await client.connect();

// Cache with TTL
async function getUserWithCache(userId) {
  const cacheKey = `user:${userId}`;
  
  // Try cache first
  const cached = await client.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }
  
  // Cache miss - get from DB
  const user = await User.findById(userId);
  if (!user) return null;
  
  // Store in cache for 1 hour
  await client.setEx(cacheKey, 3600, JSON.stringify(user));
  
  return user;
}

// Cache invalidation
async function invalidateUserCache(userId) {
  await client.del(`user:${userId}`);
}

// Distributed lock
async function acquireLock(key, ttl = 30000) {
  const lockKey = `lock:${key}`;
  const lockValue = Date.now().toString();
  
  const acquired = await client.set(lockKey, lockValue, {
    NX: true,
    PX: ttl
  });
  
  return acquired ? lockValue : null;
}

async function releaseLock(key, lockValue) {
  const script = `
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
  `;
  await client.eval(script, { keys: [`lock:${key}`], arguments: [lockValue] });
}
```

### 7. Migration Examples

```javascript
// Migration: add_phone_to_users.js
module.exports = {
  async up(db) {
    await db.collection('users').updateMany(
      {},
      { $set: { phone: null } }
    );
    
    await db.collection('users').createIndex(
      { phone: 1 },
      { sparse: true, unique: true }
    );
  },

  async down(db) {
    await db.collection('users').updateMany(
      {},
      { $unset: { phone: '' } }
    );
  }
};

// PostgreSQL migration
// 001_add_users_phone.js
exports.up = async (pg) => {
  await pg.query(`
    ALTER TABLE users 
    ADD COLUMN phone VARCHAR(20);
    
    CREATE INDEX idx_users_phone 
    ON users(phone) 
    WHERE phone IS NOT NULL;
  `);
};

exports.down = async (pg) => {
  await pg.query(`
    DROP INDEX IF EXISTS idx_users_phone;
    ALTER TABLE users DROP COLUMN phone;
  `);
};
```

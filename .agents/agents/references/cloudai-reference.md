# Cloud & AI Integration Reference - For cloudai-agent

## AWS Services

### 1. Lambda Functions

```javascript
// handler.js - AWS Lambda
exports.handler = async (event) => {
  console.log('Received event:', JSON.stringify(event));
  
  // Parse body for API Gateway
  const body = event.body ? JSON.parse(event.body) : event;
  
  // Your logic here
  const result = await processData(body);
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify({
      success: true,
      data: result
    })
  };
};

async function processData(data) {
  // Your processing logic
  return { processed: true, ...data };
}
```

```yaml
# serverless.yml
service: my-lambda-api

provider:
  name: aws
  runtime: nodejs18.x
  stage: ${opt:stage, 'dev'}
  region: ap-southeast-1
  environment:
    DATABASE_URL: ${self:custom.databaseUrl}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:PutObject
          Resource: "arn:aws:s3:::my-bucket/*"
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
          Resource: "arn:aws:secretsmanager:ap-southeast-1:*:secret:*"

functions:
  api:
    handler: handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
      - http:
          path: /
          method: GET
  
  scheduled:
    handler: scheduler.handler
    events:
      - schedule: rate(1 day)

resources:
  Resources:
    myBucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: my-unique-bucket-name
        CorsConfiguration:
          CorsRules:
            - AllowedOrigins: ["*"]
              AllowedMethods: [GET, PUT, POST]
              AllowedHeaders: ["*"]
```

### 2. S3 Operations

```javascript
// s3.js
const { S3Client, PutObjectCommand, GetObjectCommand } = require('@aws-sdk/client-s3');

const s3Client = new S3Client({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
  }
});

async function uploadFile(bucket, key, body, contentType) {
  const command = new PutObjectCommand({
    Bucket: bucket,
    Key: key,
    Body: body,
    ContentType: contentType
  });
  
  return s3Client.send(command);
}

async function getFile(bucket, key) {
  const command = new GetObjectCommand({ Bucket: bucket, Key: key });
  const response = await s3Client.send(command);
  
  return {
    body: await response.Body.transformToString(),
    contentType: response.ContentType
  };
}

// Signed URL for secure access
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');

async function getSignedDownloadUrl(bucket, key, expiresIn = 3600) {
  const command = new GetObjectCommand({ Bucket: bucket, Key: key });
  return getSignedUrl(s3Client, command, { expiresIn });
}
```

## OpenAI Integration

### 1. Chat Completions

```javascript
// openai.js
const { OpenAI } = require('openai');

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Chat completion
async function chat(prompt, systemPrompt = 'You are a helpful assistant.') {
  const completion = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: prompt }
    ],
    temperature: 0.7,
    max_tokens: 1000
  });
  
  return completion.choices[0].message.content;
}

// Streaming response
async function streamChat(prompt, onChunk) {
  const stream = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: [{ role: 'user', content: prompt }],
    stream: true
  });
  
  for await (const chunk of stream) {
    const content = chunk.choices[0]?.delta?.content;
    if (content) onChunk(content);
  }
}

// Image generation
async function generateImage(prompt, size = '1024x1024') {
  const response = await openai.images.generate({
    model: 'dall-e-3',
    prompt: prompt,
    size: size,
    n: 1
  });
  
  return response.data[0].url;
}

// Embeddings
async function getEmbedding(text) {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text
  });
  
  return response.data[0].embedding;
}
```

### 2. Claude API

```javascript
// claude.js
const { Anthropic } = require('@anthropic-ai/sdk');

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

async function claudeChat(prompt, systemPrompt = '') {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1024,
    system: systemPrompt,
    messages: [
      { role: 'user', content: prompt }
    ]
  });
  
  return message.content[0].text;
}

// With tools
async function claudeWithTools(prompt) {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1024,
    tools: [
      {
        type: 'web_search',
        name: 'search',
        description: 'Search the web for information',
        input_schema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Search query' }
          }
        }
      }
    ],
    messages: [{ role: 'user', content: prompt }]
  });
  
  return message.content;
}
```

## Vercel Serverless Functions

```javascript
// api/users.js - Vercel serverless
import { withAuth } from '@/lib/auth';

async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  // Your logic
  const users = await getUsers();
  
  return res.status(200).json({ users });
}

// Protected route with auth
export default withAuth(async function handler(req, res) {
  const { userId } = req.user;
  
  const user = await getUserById(userId);
  
  return res.status(200).json({ user });
});
```

```javascript
// lib/auth.js
import { getToken } from 'next-auth/jwt';

export async function withAuth(handler) {
  return async (req, res) => {
    const token = await getToken({ req, secret: process.env.NEXTAUTH_SECRET });
    
    if (!token) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    
    req.user = token;
    return handler(req, res);
  };
}
```

## Supabase (Firebase Alternative)

```javascript
// supabase.js
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

// Auth
async function signUp(email, password, metadata = {}) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: metadata }
  });
  
  if (error) throw error;
  return data;
}

async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });
  
  if (error) throw error;
  return data;
}

async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
}

// Database
async function getPosts(limit = 10) {
  const { data, error } = await supabase
    .from('posts')
    .select('*, author:users(name, avatar)')
    .eq('published', true)
    .order('created_at', { ascending: false })
    .limit(limit);
  
  if (error) throw error;
  return data;
}

async function createPost(post) {
  const { data, error } = await supabase
    .from('posts')
    .insert([post])
    .select()
    .single();
  
  if (error) throw error;
  return data;
}

// Real-time subscriptions
function subscribeToMessages(callback) {
  const channel = supabase
    .channel('messages')
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'messages'
    }, (payload) => callback(payload.new))
    .subscribe();
  
  return () => supabase.removeChannel(channel);
}

// Storage
async function uploadImage(bucket, path, file) {
  const { data, error } = await supabase.storage
    .from(bucket)
    .upload(path, file, {
      cacheControl: '3600',
      upsert: false
    });
  
  if (error) throw error;
  
  // Get public URL
  const { data: { publicUrl } } = supabase.storage
    .from(bucket)
    .getPublicUrl(data.path);
  
  return publicUrl;
}
```

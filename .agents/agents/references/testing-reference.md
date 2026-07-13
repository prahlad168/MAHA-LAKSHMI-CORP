# Testing Deep Knowledge - For testing-agent

## Testing Pyramid

```
        /\
       /  \       E2E Tests (few)
      /----\      - Playwright, Cypress
     /      \
    /--------\   Integration Tests
   /          \  - API testing, Component testing
  /____________\
 /              \  Unit Tests (many)
/________________\ - Jest, Vitest
```

## Unit Testing with Jest/Vitest

### 1. Basic Tests

```javascript
// sum.test.js
import { describe, test, expect } from 'vitest';

// Test simple function
function sum(a, b) {
  return a + b;
}

test('sum adds two numbers', () => {
  expect(sum(2, 3)).toBe(5);
  expect(sum(-1, 1)).toBe(0);
  expect(sum(0, 0)).toBe(0);
});

// Group related tests
describe('Calculator', () => {
  test('addition', () => {
    expect(sum(1, 2)).toBe(3);
  });
  
  test('subtraction', () => {
    function subtract(a, b) { return a - b; }
    expect(subtract(5, 3)).toBe(2);
  });
});
```

### 2. Async Testing

```javascript
// api.test.js
import { test, expect, vi } from 'vitest';

// Mock fetch
global.fetch = vi.fn();

test('fetches user data', async () => {
  const mockUser = { id: 1, name: 'John', email: 'john@test.com' };
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => mockUser
  });
  
  const response = await fetch('/api/users/1');
  const user = await response.json();
  
  expect(user.name).toBe('John');
  expect(global.fetch).toHaveBeenCalledWith('/api/users/1');
});

// Testing promises
test('handles API error', async () => {
  global.fetch.mockRejectedValueOnce(new Error('Network error'));
  
  await expect(fetch('/api/users')).rejects.toThrow('Network error');
});
```

### 3. React Component Testing

```javascript
// Button.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import Button from './Button';

describe('Button', () => {
  test('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  test('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    
    expect(screen.getByRole('button')).toBeDisabled();
  });
  
  test('shows loading state', () => {
    render(<Button loading>Loading...</Button>);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### 4. Mocking Modules

```javascript
// userService.test.js
import { vi } from 'vitest';
import { describe, test, expect } from 'vitest';

// Mock the API module
vi.mock('../api', () => ({
  getUser: vi.fn(),
  updateUser: vi.fn(),
  deleteUser: vi.fn()
}));

import * as api from '../api';
import { getUserProfile, updateUserData } from './userService';

describe('User Service', () => {
  test('gets user profile', async () => {
    const mockUser = { id: 1, name: 'John' };
    api.getUser.mockResolvedValueOnce(mockUser);
    
    const result = await getUserProfile(1);
    
    expect(result).toEqual(mockUser);
    expect(api.getUser).toHaveBeenCalledWith(1);
  });
  
  test('updates user with validation', async () => {
    api.updateUser.mockResolvedValueOnce({ success: true });
    
    const result = await updateUserData(1, { name: 'Jane' });
    
    expect(result.success).toBe(true);
  });
});
```

## E2E Testing with Playwright

### 1. Setup

```bash
# Install Playwright
npm install -D @playwright/test

# Install browsers
npx playwright install

# Config file
```

### 2. Playwright Config

```javascript
// playwright.config.js
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
});
```

### 3. E2E Tests

```javascript
// e2e/login.spec.js
import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });
  
  test('shows validation errors', async ({ page }) => {
    await page.click('button[type="submit"]');
    
    await expect(page.locator('text=Email wajib diisi')).toBeVisible();
    await expect(page.locator('text=Password wajib diisi')).toBeVisible();
  });
  
  test('logs in successfully', async ({ page }) => {
    await page.fill('[name="email"]', 'user@test.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Welcome')).toBeVisible();
  });
  
  test('shows error for invalid credentials', async ({ page }) => {
    await page.fill('[name="email"]', 'wrong@test.com');
    await page.fill('[name="password"]', 'wrongpass');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('text=Invalid credentials')).toBeVisible();
  });
});

test.describe('Dashboard', () => {
  test.use({ storageState: 'e2e/auth.json' }); // Login first
  
  test('displays user data', async ({ page }) => {
    await page.goto('/dashboard');
    
    await expect(page.locator('.user-name')).toContainText('John');
  });
});
```

### 4. API Testing

```javascript
// e2e/api.spec.js
import { test, expect, request } from '@playwright/test';

const apiContext = await request.newContext({
  baseURL: 'http://localhost:3000',
  extraHTTPHeaders: {
    'Authorization': `Bearer test-token`
  }
});

test('GET /api/users returns list', async () => {
  const response = await apiContext.get('/api/users');
  
  expect(response.ok()).toBeTruthy();
  expect(response.status()).toBe(200);
  
  const body = await response.json();
  expect(body.success).toBe(true);
  expect(Array.isArray(body.data)).toBe(true);
});

test('POST /api/users creates user', async () => {
  const newUser = {
    name: 'Test User',
    email: `test-${Date.now()}@test.com`,
    password: 'password123'
  };
  
  const response = await apiContext.post('/api/users', {
    data: newUser
  });
  
  expect(response.status()).toBe(201);
  
  const body = await response.json();
  expect(body.data.email).toBe(newUser.email);
});
```

## TDD Workflow

```javascript
// Step 1: Write failing test first
test('formats currency in IDR', () => {
  expect(formatCurrency(100000)).toBe('Rp 100.000');
  expect(formatCurrency(1500000)).toBe('Rp 1.500.000');
});

// Step 2: Implement minimum code to pass
function formatCurrency(amount) {
  const formatted = amount.toLocaleString('id-ID');
  return `Rp ${formatted}`;
}

// Step 3: Refactor if needed
function formatCurrency(amount, locale = 'id-ID', currency = 'IDR') {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0
  }).format(amount);
}
```

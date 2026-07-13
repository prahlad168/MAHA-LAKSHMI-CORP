# Mobile & PWA Deep Knowledge - For mobile-agent

## React Native Essentials

### 1. Project Setup

```bash
# Create Expo project (recommended)
npx create-expo-app MyApp --template blank

# Start development
npx expo start

# Build for production
npx expo build:android
npx expo build:ios

# Or use React Native CLI
npx react-native@latest init MyApp
```

### 2. Navigation Setup

```bash
# Install dependencies
npx expo install @react-navigation/native @react-navigation/native-stack
npx expo install react-native-screens react-native-safe-area-context
```

```javascript
// App.js
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: '#3B82F6' },
          headerTintColor: '#fff',
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Details" component={DetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### 3. Components

```javascript
// Touchable components
import { TouchableOpacity, Pressable, Text, View, Image, FlatList } from 'react-native';

function UserCard({ user, onPress }) {
  return (
    <TouchableOpacity 
      style={styles.card}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Image source={{ uri: user.avatar }} style={styles.avatar} />
      <View style={styles.info}>
        <Text style={styles.name}>{user.name}</Text>
        <Text style={styles.email}>{user.email}</Text>
      </View>
    </TouchableOpacity>
  );
}

// FlatList with pull-to-refresh
function UserList() {
  const [refreshing, setRefreshing] = useState(false);
  
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await refetchUsers();
    setRefreshing(false);
  }, []);
  
  return (
    <FlatList
      data={users}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <UserCard user={item} />}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
      refreshing={refreshing}
      onRefresh={onRefresh}
    />
  );
}
```

### 4. Forms & Validation

```javascript
import { useState } from 'react';
import { TextInput, Button, StyleSheet, View, Text } from 'react-native';
import { useForm, Controller } from 'react-hook-form';

function LoginScreen() {
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: { email: '', password: '' }
  });
  
  const onSubmit = (data) => {
    console.log(data);
    // Handle login
  };
  
  return (
    <View style={styles.container}>
      <Controller
        control={control}
        name="email"
        rules={{
          required: 'Email wajib diisi',
          pattern: { value: /^\S+@\S+$/i, message: 'Email tidak valid' }
        }}
        render={({ field: { onChange, value } }) => (
          <TextInput
            style={[styles.input, errors.email && styles.inputError]}
            placeholder="Email"
            value={value}
            onChangeText={onChange}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        )}
      />
      {errors.email && <Text style={styles.error}>{errors.email.message}</Text>}
      
      <Controller
        control={control}
        name="password"
        rules={{ required: 'Password wajib diisi', minLength: 6 }}
        render={({ field: { onChange, value } }) => (
          <TextInput
            style={[styles.input, errors.password && styles.inputError]}
            placeholder="Password"
            value={value}
            onChangeText={onChange}
            secureTextEntry
          />
        )}
      />
      
      <Button title="Login" onPress={handleSubmit(onSubmit)} />
    </View>
  );
}
```

## PWA (Progressive Web App)

### 1. Manifest

```json
{
  "name": "My PWA App",
  "short_name": "MyApp",
  "description": "Aplikasi web modern untuk Indonesia",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3B82F6",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "categories": ["business", "productivity"],
  "lang": "id",
  "dir": "ltr"
}
```

### 2. Service Worker

```javascript
// sw.js
const CACHE_NAME = 'myapp-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/static/js/main.js',
  '/static/css/main.css',
  '/icons/icon-192x192.png'
];

// Install
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  event.respondWith(
    caches.match(event.request).then((cached) => {
      // Return cached if available
      if (cached) {
        // Fetch update in background
        event.waitUntil(
          fetch(event.request).then((response) => {
            if (response.ok) {
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(event.request, response);
              });
            }
          }).catch(() => {})
        );
        return cached;
      }
      
      // Fetch from network
      return fetch(event.request).then((response) => {
        // Cache successful responses
        if (response.ok) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      }).catch(() => {
        // Return offline page for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
      });
    })
  );
});

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data.json();
  
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      data: data.url
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data)
  );
});
```

### 3. Register Service Worker

```javascript
// Register in index.html or main.js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('SW registered:', registration.scope);
      
      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New content available
            showUpdateNotification();
          }
        });
      });
    } catch (error) {
      console.error('SW registration failed:', error);
    }
  });
}
```

### 4. Offline Page

```html
<!-- offline.html -->
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Offline - MyApp</title>
  <style>
    body {
      font-family: system-ui, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
      text-align: center;
      background: #f5f5f5;
    }
    h1 { color: #333; }
    p { color: #666; max-width: 400px; }
    button {
      padding: 12px 24px;
      background: #3B82F6;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
    }
    button:hover { background: #2563EB; }
  </style>
</head>
<body>
  <h1>📡 Anda Sedang Offline</h1>
  <p>Koneksi internet Anda terputus. Silakan coba lagi atau periksa pengaturan jaringan Anda.</p>
  <button onclick="window.location.reload()">🔄 Coba Lagi</button>
</body>
</html>
```

### 5. Install Prompt

```javascript
let deferredPrompt;
const installBtn = document.getElementById('installBtn');

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  // Show install button
  if (shouldShowInstallButton()) {
    installBtn.style.display = 'block';
  }
});

installBtn.addEventListener('click', async () => {
  if (!deferredPrompt) return;
  
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  
  if (outcome === 'accepted') {
    console.log('User accepted install');
  }
  
  deferredPrompt = null;
  installBtn.style.display = 'none';
});
```

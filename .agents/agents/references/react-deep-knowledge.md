# React Deep Knowledge - For frontend-agent

## React 18+ Best Practices

### 1. Component Architecture

```jsx
// ✅ Good: Single Responsibility Component
function UserCard({ user }) {
  return (
    <div className="card">
      <Avatar src={user.avatar} />
      <UserInfo name={user.name} email={user.email} />
    </div>
  );
}

// ✅ Good: Composition over Inheritance
function Button({ children, variant = 'primary', ...props }) {
  return (
    <button className={`btn btn-${variant}`} {...props}>
      {children}
    </button>
  );
}

// Usage
<Button variant="secondary" onClick={handleClick}>
  <Icon name="save" /> Save
</Button>
```

### 2. State Management

```jsx
// ✅ useState - Simple state
const [count, setCount] = useState(0);

// ✅ useReducer - Complex state
const reducer = (state, action) => {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 };
    case 'decrement': return { count: state.count - 1 };
    default: return state;
  }
};
const [state, dispatch] = useReducer(reducer, { count: 0 });

// ✅ useCallback - Memoize callbacks
const handleSubmit = useCallback((data) => {
  submitForm(data);
}, [submitForm]);

// ✅ useMemo - Memoize expensive computations
const sortedList = useMemo(() => 
  items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);

// ✅ Custom Hooks
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}
```

### 3. Data Fetching

```jsx
// ✅ React Query (TanStack Query)
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function UserProfile({ userId }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetch(`/api/users/${userId}`).then(res => res.json()),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return <div>{data?.name}</div>;
}

// ✅ useMutation for updates
function CreatePost() {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (newPost) => fetch('/api/posts', {
      method: 'POST',
      body: JSON.stringify(newPost)
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    }
  });
}
```

### 4. Performance Optimization

```jsx
// ✅ React.memo - Prevent unnecessary re-renders
const ExpensiveList = React.memo(function ExpensiveList({ items }) {
  return items.map(item => <ListItem key={item.id} item={item} />);
});

// ✅ useTransition for non-urgent updates
import { useTransition } from 'react';

function SearchInput() {
  const [isPending, startTransition] = useTransition();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    
    startTransition(() => {
      setResults(searchDatabase(value));
    });
  };
}

// ✅ Code Splitting
import { lazy, Suspense } from 'react';
const HeavyChart = lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <HeavyChart data={data} />
    </Suspense>
  );
}
```

### 5. Error Boundaries

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    logErrorToService(error, info);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <MyComponent />
</ErrorBoundary>
```

### 6. Forms with React Hook Form

```jsx
import { useForm } from 'react-hook-form';

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  const onSubmit = (data) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input 
        {...register('email', { 
          required: 'Email wajib diisi',
          pattern: { value: /^\S+@\S+$/i, message: 'Email tidak valid' }
        })} 
      />
      {errors.email && <span>{errors.email.message}</span>}
      
      <input 
        {...register('password', { 
          required: 'Password wajib diisi',
          minLength: { value: 8, message: 'Minimal 8 karakter' }
        })} 
        type="password" 
      />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">Login</button>
    </form>
  );
}
```

### 7. Context Best Practices

```jsx
// ✅ Split contexts by update frequency
const ThemeContext = createContext();
const AuthContext = createContext();

// ✅ Use reducer for complex context
const UIContext = createContext();

function UIProvider({ children }) {
  const [state, dispatch] = useReducer(uiReducer, initialState);
  
  return (
    <UIContext.Provider value={{ state, dispatch }}>
      {children}
    </UIContext.Provider>
  );
}

// ✅ Custom hook for context
function useUI() {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within UIProvider');
  }
  return context;
}
```

### 8. Testing with React Testing Library

```jsx
// ✅ Component Test
import { render, screen, fireEvent } from '@testing-library/react';

test('submit form', async () => {
  render(<LoginForm onSubmit={mockSubmit} />);
  
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' }
  });
  fireEvent.click(screen.getByRole('button', { name: /login/i }));
  
  expect(mockSubmit).toHaveBeenCalledWith({
    email: 'test@example.com'
  });
});

// ✅ Async testing
test('displays user data', async () => {
  render(<UserProfile userId="1" />);
  
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  
  const userName = await screen.findByText(/john doe/i);
  expect(userName).toBeInTheDocument();
});
```

## Common Patterns

### Loading States
```jsx
function DataComponent() {
  const { data, isLoading } = useQuery(['key'], fetcher);
  
  if (isLoading) return <Skeleton />;
  if (!data) return <EmptyState />;
  
  return <DataDisplay data={data} />;
}
```

### Optimistic Updates
```jsx
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    await queryClient.cancelQueries(['todos']);
    const previous = queryClient.getQueryData(['todos']);
    queryClient.setQueryData(['todos'], (old) => [...old, newTodo]);
    return { previous };
  },
  onError: (err, newTodo, context) => {
    queryClient.setQueryData(['todos'], context.previous);
  }
});
```

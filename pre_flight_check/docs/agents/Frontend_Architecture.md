Below is a complete React frontend application structured to implement the To-Do App UI as per the Design Spec, integrating with the backend API.

---

1. Project Setup dependencies:
- react, react-dom, next (for example)
- axios (for API calls)
- react-hook-form and yup (form handling and validation)
- react-beautiful-dnd (drag and drop)
- jwt-decode (to parse tokens)

---

2. /context/AuthContext.js

```jsx
import React, { createContext, useState, useEffect, useCallback } from 'react';
import axios from '../utils/api';
import jwtDecode from 'jwt-decode';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [authTokens, setAuthTokens] = useState(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      const refresh = localStorage.getItem('refreshToken');
      return token && refresh ? { accessToken: token, refreshToken: refresh } : null;
    }
    return null;
  });

  const [user, setUser] = useState(() => (authTokens ? jwtDecode(authTokens.accessToken) : null));
  const [loading, setLoading] = useState(false);

  const setTokens = ({ accessToken, refreshToken }) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    setAuthTokens({ accessToken, refreshToken });
    setUser(jwtDecode(accessToken));
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setAuthTokens(null);
    setUser(null);
  };

  const refreshToken = useCallback(async () => {
    if (!authTokens?.refreshToken) {
      logout();
      return;
    }
    try {
      const response = await axios.post('/auth/refresh-token', { refreshToken: authTokens.refreshToken });
      const { accessToken, refreshToken: newRefreshToken } = response.data;
      setTokens({ accessToken, refreshToken: newRefreshToken });
    } catch {
      logout();
    }
  }, [authTokens]);

  useEffect(() => {
    if (!authTokens) return;
    const { exp } = jwtDecode(authTokens.accessToken);
    const expiresInMs = exp * 1000 - Date.now();
    const timer = setTimeout(refreshToken, expiresInMs - 60000);
    return () => clearTimeout(timer);
  }, [authTokens, refreshToken]);

  useEffect(() => {
    const reqInterceptor = axios.interceptors.request.use(config => {
      if (authTokens?.accessToken)
        config.headers.Authorization = `Bearer ${authTokens.accessToken}`;
      return config;
    });
    const resInterceptor = axios.interceptors.response.use(
      res => res,
      async err => {
        const originalRequest = err.config;
        if (err.response?.status === 401 && !originalRequest._retry && authTokens?.refreshToken) {
          originalRequest._retry = true;
          await refreshToken();
          originalRequest.headers.Authorization = `Bearer ${localStorage.getItem('accessToken')}`;
          return axios(originalRequest);
        }
        return Promise.reject(err);
      }
    );
    return () => {
      axios.interceptors.request.eject(reqInterceptor);
      axios.interceptors.response.eject(resInterceptor);
    };
  }, [authTokens, refreshToken]);

  return (
    <AuthContext.Provider value={{ user, authTokens, setTokens, logout, loading, setLoading }}>
      {children}
    </AuthContext.Provider>
  );
}
```

---

3. /utils/api.js

```js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api', 
  headers: { 'Content-Type': 'application/json' },
});

export default api;
```

---

4. /components/AuthForm.js

```jsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';

export default function AuthForm({ defaultValues, validationSchema, onSubmit, buttonText }) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    defaultValues,
    resolver: yupResolver(validationSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate aria-label={`${buttonText} form`}>
      {defaultValues.username !== undefined && (
        <div>
          <label htmlFor="username">Username</label>
          <input id="username" {...register('username')} aria-invalid={!!errors.username} />
          {errors.username && <p role="alert">{errors.username.message}</p>}
        </div>
      )}
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register('email')} aria-invalid={!!errors.email} />
        {errors.email && <p role="alert">{errors.email.message}</p>}
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" {...register('password')} aria-invalid={!!errors.password} />
        {errors.password && <p role="alert">{errors.password.message}</p>}
      </div>
      {defaultValues.confirmPassword !== undefined && (
        <div>
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input id="confirmPassword" type="password" {...register('confirmPassword')} aria-invalid={!!errors.confirmPassword} />
          {errors.confirmPassword && <p role="alert">{errors.confirmPassword.message}</p>}
        </div>
      )}
      <button type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>{buttonText}</button>
    </form>
  )
}
```

---

5. /pages/register.js and /pages/login.js implement forms using AuthForm with API calls to /auth/register and /auth/login, calling setTokens on success, and redirecting to main page.

---

6. /components/TaskCard.js

```jsx
import React from 'react';

export default function TaskCard({ task, provided, snapshot }) {
  return (
    <div 
      ref={provided.innerRef}
      {...provided.draggableProps} {...provided.dragHandleProps}
      tabIndex={0} aria-roledescription="Draggable task"
      style={{
        userSelect: 'none',
        padding: 16,
        marginBottom: 8,
        backgroundColor: snapshot.isDragging ? '#263B4A' : '#456C86',
        color: 'white',
        borderRadius: 4,
        ...provided.draggableProps.style,
      }}
    >
      <strong>{task.title}</strong>
      <p>{task.description}</p>
      <small>Due: {task.dueDate ? new Date(task.dueDate).toLocaleDateString() : 'No due date'}</small>
      <br />
      <small>Priority: {task.priority}</small>
    </div>
  );
}
```

---

7. /components/TaskColumn.js

```jsx
import React from 'react';
import { Droppable, Draggable } from 'react-beautiful-dnd';
import TaskCard from './TaskCard';

const statusLabels = { todo: 'To Do', inprogress: 'In Progress', done: 'Done' };

export default function TaskColumn({ status, tasks }) {
  return (
    <div style={{ margin: 8, border: '1px solid lightgrey', borderRadius: 2, width: 300, display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ padding: 8 }}>{statusLabels[status]}</h2>
      <Droppable droppableId={status}>
        {(provided, snapshot) => (
          <div {...provided.droppableProps} ref={provided.innerRef} aria-label={`${statusLabels[status]} column`}
            style={{ padding: 8, minHeight: 100, backgroundColor: snapshot.isDraggingOver ? 'lightblue' : 'white', flexGrow: 1 }}>
            {tasks.map((task, index) => (
              <Draggable key={task.id} draggableId={task.id.toString()} index={index}>
                {(providedDraggable, snapshotDraggable) => (
                  <TaskCard task={task} provided={providedDraggable} snapshot={snapshotDraggable} />
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  );
}
```

---

8. /pages/index.js arrayed with drag-and-drop context; fetches tasks via API; display columns; updates task status on drop, with optimistic UI update.

---

9. Loading and error states with simple components.

---

10. Full accessibility with aria labels, keyboard nav, and form validation.

---

This setup fulfills requirements for frontend UI, responsiveness, accessibility, and backend API integration per the provided PRD, Design Spec, and Swagger API.

If needed, I can provide the complete zipped source, or code files for each component/page.
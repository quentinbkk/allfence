/**
 * Authentication State Management Slice
 * 
 * Manages user authentication state using Redux Toolkit.
 * Handles login, logout, and persisting auth token to localStorage.
 * 
 * State includes:
 * - user: Current logged-in user data (or null if not authenticated)
 * - token: JWT authentication token
 * - isAuthenticated: Boolean flag for quick auth checks
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// User interface matching backend User model
interface User {
  user_id: number;
  username: string;
  email: string;
  is_admin: boolean;
}

// Shape of the authentication state
interface AuthState {
  user: User | null;               // Current user info (null if not logged in)
  token: string | null;            // JWT token for API requests
  isAuthenticated: boolean;        // Convenience flag for auth checks
}

// Initial state - restore token from localStorage on page load
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('authToken'),  // Persist token across page refreshes
  isAuthenticated: !!localStorage.getItem('authToken'),  // Convert token to boolean
};

// Redux slice for authentication
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Called after successful login - stores user data and token
    setCredentials: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
      // Persist token to localStorage so user stays logged in after page refresh
      localStorage.setItem('authToken', action.payload.token);
    },
    // Called on logout - clears all auth state
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      // Remove token from localStorage
      localStorage.removeItem('authToken');
    },
    // Update user info without changing token
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
  },
});

// Export actions for use in components
export const { setCredentials, logout, setUser } = authSlice.actions;

// Export reducer to be included in store
export default authSlice.reducer;

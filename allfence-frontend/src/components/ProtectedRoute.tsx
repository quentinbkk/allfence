/**
 * Protected Route Component
 * 
 * This component acts as a route guard - it checks if a user is authenticated
 * before allowing access to protected pages. If the user is not logged in,
 * they are redirected to the login page.
 * 
 * Usage: Wrap protected routes in App.tsx with this component
 * 
 * Example:
 *   <Route element={<ProtectedRoute />}>
 *     <Route path="/dashboard" element={<Dashboard />} />
 *   </Route>
 */

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';

export const ProtectedRoute: React.FC = () => {
  // Get authentication state from Redux store
  const { token, isAuthenticated } = useAppSelector((state) => state.auth);

  // Check if user is authenticated (has valid token)
  if (!isAuthenticated || !token) {
    // Not authenticated - redirect to login page
    // 'replace' prevents user from going back to protected page with browser back button
    return <Navigate to="/login" replace />;
  }

  // User is authenticated - render child routes via Outlet
  return <Outlet />;
};

export default ProtectedRoute;

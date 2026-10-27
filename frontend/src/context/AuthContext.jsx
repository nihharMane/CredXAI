import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';
import { logger } from '../utils/logger';

const AuthContext = createContext(null);

const STORAGE_KEY = 'credxai_auth';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed?.token && parsed?.id) {
          return parsed;
        }
      }
    } catch (e) {
      logger.warn('auth.storage.read_failed', { errorType: e?.name || 'Error' });
    }
    return null;
  });

  const [loading, setLoading] = useState(false);
  const [authError, setAuthError] = useState(null);

  // Listen for 401 unauthorized events dispatched by apiClient
  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null);
      localStorage.removeItem(STORAGE_KEY);
    };

    window.addEventListener('credxai:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('credxai:unauthorized', handleUnauthorized);
    };
  }, []);

  /**
   * Log in user with email & password
   */
  const login = async (email, password) => {
    setLoading(true);
    setAuthError(null);
    try {
      const data = await authService.login({ email, password });
      // Expected backend response: { id, fullName, email, role, token }
      if (!data.token) {
        throw new Error('Authentication succeeded but no token was provided.');
      }
      const authUser = {
        id: data.id,
        fullName: data.fullName,
        email: data.email,
        role: data.role,
        token: data.token,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(authUser));
      setUser(authUser);
      logger.info('auth.login.succeeded');
      return { success: true, user: authUser };
    } catch (err) {
      const errorMessage =
        err.response?.data?.error ||
        err.response?.data?.message ||
        err.message ||
        'Failed to log in. Please check your credentials.';
      setAuthError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Register a new account.
   * Note: Backend returns token=null on registration, so user is redirected to login.
   */
  const register = async (fullName, email, password) => {
    setLoading(true);
    setAuthError(null);
    try {
      const data = await authService.register({ fullName, email, password });
      logger.info('auth.registration.succeeded');
      return { success: true, data };
    } catch (err) {
      const errorMessage =
        err.response?.data?.error ||
        err.response?.data?.message ||
        err.message ||
        'Registration failed. Please verify the information provided.';
      setAuthError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Log out and wipe credentials
   */
  const logout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
    setAuthError(null);
    logger.info('auth.logout.completed');
  };

  const value = {
    user,
    userId: user?.id || null,
    token: user?.token || null,
    isAuthenticated: !!user?.token,
    loading,
    authError,
    setAuthError,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;

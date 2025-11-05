import React, { createContext, useState, useContext, useEffect } from 'react';
import { getCookie, authAPI } from '../../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);

  const checkAuth = async () => {
    const accessToken = getCookie('access_token');
    
    if (accessToken) {
      try {
        // Получаем информацию о пользователе
        const userData = await authAPI.getMe();
        setUser(userData);
        setIsAuthenticated(true);
        return true;
      } catch (error) {
        console.error('Error fetching user data:', error);
        // Если не удалось получить данные пользователя, но токен есть - считаем авторизованным
        setIsAuthenticated(true);
        return true;
      }
    } else {
      setIsAuthenticated(false);
      setUser(null);
      return false;
    }
  };

  useEffect(() => {
    const initializeAuth = async () => {
      await checkAuth();
      setIsLoading(false);
    };

    initializeAuth();

    const interval = setInterval(checkAuth, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const login = () => {
    checkAuth(); // Обновляем информацию о пользователе после логина
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
  };

  const value = {
    isAuthenticated,
    isLoading,
    user,
    checkAuth,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
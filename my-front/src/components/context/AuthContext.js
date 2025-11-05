import React, { createContext, useState, useContext, useEffect } from 'react';
import { getCookie } from '../../services/api';

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

  const checkAuth = () => {
    const accessToken = getCookie('access_token');
    setIsAuthenticated(!!accessToken);
    return !!accessToken;
  };

  useEffect(() => {
    // Проверяем аутентификацию при загрузке
    checkAuth();
    setIsLoading(false);

    // Периодическая проверка
    const interval = setInterval(checkAuth, 30000);
    return () => clearInterval(interval);
  }, []);

  const login = () => {
    setIsAuthenticated(true);
  };

  const logout = () => {
    setIsAuthenticated(false);
  };

  const value = {
    isAuthenticated,
    isLoading,
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
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getCookie, logout } from '../services/api';
import logo from '../assets/logo.jpg'

const Header = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Проверяем авторизацию при загрузке компонента и при изменении
    const checkAuth = () => {
      const accessToken = getCookie('access_token');
      setIsAuthenticated(!!accessToken);
    };

    checkAuth();

    // Проверяем авторизацию каждые 30 секунд
    const interval = setInterval(checkAuth, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout(); // Эта функция уже удаляет куки и перенаправляет
  };

  return (
    <header className="site-header">
      <div className="container header-inner">
        <div className="brand-group">
          <Link to="/">
            <img className="logo" src={logo} alt="лого" />
          </Link>
          <Link className="brand" to="/">Иван Коротаев</Link>
        </div>
        <nav className="main-nav">
          <Link to="/">Главная</Link>
          <Link to="/blog">Блог</Link>
          
          {isAuthenticated ? (
            <button 
              onClick={handleLogout}
              className="logout-btn"
            >
              Выйти
            </button>
          ) : (
            <Link to="/login">Регистрация/Вход</Link>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
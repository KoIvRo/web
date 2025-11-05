import React from 'react';
import { Link } from 'react-router-dom';
import { deleteCookie } from '../services/api';
import { useAuth } from './context/AuthContext';
import logo from '../assets/logo.jpg';

const Header = () => {
  const { isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    
    logout();

    window.location.href = '/';
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
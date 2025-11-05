import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI, setCookie } from '../../services/api';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();

  // Если пользователь уже авторизован, перенаправляем на главную
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const tokens = await authAPI.login({
        username: formData.username,
        password: formData.password
      });

      setCookie('access_token', tokens.access, 15);
      setCookie('refresh_token', tokens.refresh, 60*24*7);

      // Обновляем состояние аутентификации
      login();

      navigate('/');
      
    } catch (error) {
      console.error('Login error:', error);
      
      if (error.response?.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Ошибка при входе. Проверьте правильность данных.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="hero">
      <div className="container">
        <h2>Вход</h2>
        
        {errors.general && (
          <div className="error-message">
            {errors.general}
          </div>
        )}

        {errors.detail && (
          <div className="error-message">
            {errors.detail}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              name="username"
              placeholder="Логин"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              className={errors.username ? 'error' : ''}
              required
            />
            {errors.username && <span className="field-error">{errors.username}</span>}
          </div>

          <div className="form-group">
            <input
              type="password"
              name="password"
              placeholder="Пароль"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className={errors.password ? 'error' : ''}
              required
            />
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>

          <button 
            type="submit" 
            className="btn primary" 
            disabled={isLoading}
          >
            {isLoading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div style={{ marginTop: '20px' }}>
          <p>Нет аккаунта? <Link to="/register">Зарегистрируйтесь</Link></p>
          <Link to="/" className="btn ghost">На главную</Link>
        </div>
      </div>
    </section>
  );
};

export default Login;
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI, setCookie } from '../../services/api';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password1: '',
    password2: ''
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

    // Клиентская валидация
    if (formData.password1.length < 4) {
      setErrors({ password1: 'Пароль должен содержать минимум 4 символа' });
      setIsLoading(false);
      return;
    }

    if (formData.password1 !== formData.password2) {
      setErrors({ password2: 'Пароли не совпадают' });
      setIsLoading(false);
      return;
    }

    try {
      const response = await authAPI.register({
        username: formData.username,
        email: formData.email || '',
        password1: formData.password1,
        password2: formData.password2
      });

      // Сохраняем токены в куки
      setCookie('access_token', response.access, 15);
      setCookie('refresh_token', response.refresh, 60*24*7);

      // Обновляем состояние аутентификации
      login();

      // Перенаправляем на главную
      navigate('/');
      
    } catch (error) {
      console.error('Registration error:', error);
      
      if (error.response?.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Ошибка при регистрации. Попробуйте еще раз.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // ... остальной код без изменений ...
  return (
    <section className="hero">
      <div className="container">
        <h2>Регистрация</h2>
        
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
              minLength="3"
              maxLength="150"
              required
            />
            {errors.username && <span className="field-error">{errors.username}</span>}
          </div>

          <div className="form-group">
            <input
              type="email"
              name="email"
              placeholder="Почта (опционально)"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className={errors.email ? 'error' : ''}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div className="form-group">
            <input
              type="password"
              name="password1"
              placeholder="Пароль"
              value={formData.password1}
              onChange={(e) => setFormData({...formData, password1: e.target.value})}
              className={errors.password1 ? 'error' : ''}
              minLength="4"
              required
            />
            {errors.password1 && <span className="field-error">{errors.password1}</span>}
          </div>

          <div className="form-group">
            <input
              type="password"
              name="password2"
              placeholder="Подтверждение пароля"
              value={formData.password2}
              onChange={(e) => setFormData({...formData, password2: e.target.value})}
              className={errors.password2 ? 'error' : ''}
              required
            />
            {errors.password2 && <span className="field-error">{errors.password2}</span>}
          </div>

          <button 
            type="submit" 
            className="btn primary" 
            disabled={isLoading}
          >
            {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>

        <div style={{ marginTop: '20px' }}>
          <p>Уже есть аккаунт? <Link to="/login">Войдите</Link></p>
          <Link to="/" className="btn ghost">На главную</Link>
        </div>
      </div>
    </section>
  );
};

export default Register;
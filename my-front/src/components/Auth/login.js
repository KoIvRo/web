import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI, setCookie, getCookie } from '../../services/api';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Если пользователь уже авторизован, перенаправляем на главную
  useEffect(() => {
    const accessToken = getCookie('access_token');
    if (accessToken) {
      navigate('/');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      // Предполагаем, что ваш бэкенд возвращает {access, refresh}
      const tokens = await authAPI.login({
        username: formData.username,
        password: formData.password
      });

      // Сохраняем токены в куки
      setCookie('access_token', tokens.access, 15); // 15 минут
      setCookie('refresh_token', tokens.refresh, 60*24*7); // 7 дней

      // Перенаправляем на главную
      navigate('/');
      
    } catch (error) {
      console.error('Login error:', error);
      
      // Обработка ошибок от API
      if (error.response?.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Ошибка при входе. Проверьте правильность данных.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Очищаем ошибки при изменении поля
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: ''
      });
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

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              name="username"
              placeholder="Имя пользователя"
              value={formData.username}
              onChange={handleChange}
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
              onChange={handleChange}
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
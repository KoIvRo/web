import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI, setCookie, getCookie } from '../../services/api';

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

    // Проверка совпадения паролей
    if (formData.password1 !== formData.password2) {
      setErrors({ password2: 'Пароли не совпадают' });
      setIsLoading(false);
      return;
    }

    try {
      // Отправляем данные для регистрации
      const userData = {
        username: formData.username,
        email: formData.email,
        password: formData.password1
      };

      const response = await authAPI.register(userData);

      // Если регистрация успешна, автоматически логиним пользователя
      // Предположим, что бэкенд возвращает токены при регистрации
      if (response.access && response.refresh) {
        setCookie('access_token', response.access, 15);
        setCookie('refresh_token', response.refresh, 60*24*7);
        navigate('/');
      } else {
        // Если токены не вернулись, перенаправляем на логин
        navigate('/login');
      }
      
    } catch (error) {
      console.error('Registration error:', error);
      
      // Обработка ошибок от API
      if (error.response?.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Ошибка при регистрации. Попробуйте еще раз.' });
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
        <h2>Регистрация</h2>
        
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
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? 'error' : ''}
              required
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div className="form-group">
            <input
              type="password"
              name="password1"
              placeholder="Пароль"
              value={formData.password1}
              onChange={handleChange}
              className={errors.password1 ? 'error' : ''}
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
              onChange={handleChange}
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
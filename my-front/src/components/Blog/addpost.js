import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { blogAPI } from '../../services/api';
import { useAuth } from '../context/AuthContext';

const AddPost = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await blogAPI.createArticle({
        title: formData.title,
        content: formData.content,
        category: formData.category,
        author_id: user.id
      });
      
      navigate('/blog');
    } catch (err) {
      console.error('Error creating post:', err);
      alert('Ошибка при создании поста');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <section className="about">
      <div className="container">
        <h2>Добавить новый пост</h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              name="title"
              placeholder="Заголовок"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
            >
              <option value="">Выберите категорию</option>
              <option value="technology">Технологии</option>
              <option value="programming">Программирование</option>
              <option value="science">Наука</option>
              <option value="other">Другое</option>
            </select>
          </div>

          <div className="form-group">
            <textarea
              name="content"
              placeholder="Содержание поста"
              value={formData.content}
              onChange={handleChange}
              rows="10"
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn primary"
            disabled={loading}
          >
            {loading ? 'Публикация...' : 'Опубликовать'}
          </button>
          <button 
            type="button" 
            className="btn ghost"
            onClick={() => navigate('/blog')}
            style={{ marginLeft: '10px' }}
          >
            Отмена
          </button>
        </form>
      </div>
    </section>
  );
};

export default AddPost;
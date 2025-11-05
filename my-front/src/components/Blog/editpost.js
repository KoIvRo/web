import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { blogAPI } from '../../services/api';

const EditPost = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: ''
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const post = await blogAPI.getArticle(id);
        setFormData({
          title: post.title,
          content: post.content,
          category: post.category
        });
      } catch (err) {
        console.error('Error fetching post:', err);
        navigate('/blog');
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [id, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrors({});

    try {
      await blogAPI.updateArticle(id, formData);
      navigate(`/blog/${id}`);
    } catch (err) {
      console.error('Error updating post:', err);
      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ general: 'Ошибка при обновлении поста' });
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (loading) return <div className="container loading">Загрузка...</div>;

  return (
    <section className="about">
      <div className="container">
        <h2>Редактировать пост</h2>
        
        {errors.general && (
          <div className="error-message">{errors.general}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              name="title"
              placeholder="Заголовок"
              value={formData.title}
              onChange={handleChange}
              className={errors.title ? 'error' : ''}
              required
            />
            {errors.title && <span className="field-error">{errors.title}</span>}
          </div>

          <div className="form-group">
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className={errors.category ? 'error' : ''}
              required
            >
              <option value="technology">Технологии</option>
              <option value="programming">Программирование</option>
              <option value="science">Наука</option>
              <option value="other">Другое</option>
            </select>
            {errors.category && <span className="field-error">{errors.category}</span>}
          </div>

          <div className="form-group">
            <textarea
              name="content"
              placeholder="Содержание поста"
              value={formData.content}
              onChange={handleChange}
              className={errors.content ? 'error' : ''}
              rows="10"
              required
            />
            {errors.content && <span className="field-error">{errors.content}</span>}
          </div>

          <button 
            type="submit" 
            className="btn primary"
            disabled={submitting}
          >
            {submitting ? 'Сохранение...' : 'Сохранить'}
          </button>
        </form>
      </div>
    </section>
  );
};

export default EditPost;
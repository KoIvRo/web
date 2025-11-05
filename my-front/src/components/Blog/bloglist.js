import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { blogAPI } from '../../services/api';
import { useAuth } from '../context/AuthContext';

const BlogList = ({ category = null }) => {
  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const { isAuthenticated, user } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const categoriesData = await blogAPI.getCategories();
        setCategories(categoriesData);
        
        let postsData;
        if (category) {
          const validCategories = categoriesData.map(cat => 
            typeof cat === 'object' ? cat.value : cat
          );
          
          if (!validCategories.includes(category)) {
            setMessage(`Категория '${category}' не найдена`);
            postsData = await blogAPI.getArticles();
          } else {
            postsData = await blogAPI.getArticlesByCategory(category);
          }
        } else {
          postsData = await blogAPI.getArticles();
        }
        
        setPosts(postsData);
      } catch (err) {
        setError('Ошибка при загрузке постов');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [category]);

  const handleDeletePost = async (postId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот пост?')) {
      try {
        await blogAPI.deleteArticle(postId);
        setPosts(posts.filter(post => post.id !== postId));
      } catch (err) {
        console.error('Error deleting post:', err);
        alert('Ошибка при удалении поста');
      }
    }
  };

  const canModifyPost = (post) => {
    return isAuthenticated && user && post.author_id === user.id;
  };

  if (loading) return <div className="container loading">Загрузка...</div>;
  if (error) return <div className="container error">{error}</div>;

  return (
    <section className="blog">
      <div className="container">
        <h2>Блог</h2>
        
        <div className="actions">
          <Link to="/" className="btn ghost">← На главную</Link>
          {isAuthenticated && (
            <Link to="/blog/add" className="btn ghost">Добавить пост</Link>
          )}
        </div>

        <div className="category-filter" style={{ marginBottom: '20px' }}>
          <strong>Категории:</strong>
          <Link 
            to="/blog" 
            className={`btn ${!category ? 'primary' : 'ghost'}`}
            style={{ margin: '5px' }}
          >
            Все
          </Link>
          {categories.map((cat, index) => {
            const catValue = typeof cat === 'object' ? cat.value : cat;
            const catName = typeof cat === 'object' ? cat.name : cat;
            
            return (
              <Link 
                key={index}
                to={`/blog/category/${catValue}`}
                className={`btn ${category === catValue ? 'primary' : 'ghost'}`}
                style={{ margin: '5px' }}
              >
                {catName}
              </Link>
            );
          })}
        </div>

        {message && (
          <div className="alert" style={{ 
            background: '#fff3cd', 
            padding: '10px', 
            borderRadius: '5px', 
            marginBottom: '20px' 
          }}>
            {message}
          </div>
        )}

        <div className="posts">
          {posts.map(post => (
            <article key={post.id} className="post">
              <h3><Link to={`/blog/${post.id}`}>{post.title}</Link></h3>
              <p className="meta">{post.category}</p>
              <p className="meta">{post.author_name || post.author}</p>
              <p className="meta">
                {new Date(post.created_at).toLocaleString('ru-RU', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
              <p>{post.content?.substring(0, 150)}...</p>
              <p><Link to={`/blog/${post.id}`}>Комментарии ({post.comments_count || 0})</Link></p>
              
              {canModifyPost(post) && (
                <div style={{ marginTop: '10px' }}>
                  <Link 
                    to={`/blog/edit/${post.id}`}
                    style={{ color: '#0066cc', textDecoration: 'none', marginRight: '10px' }}
                  >
                    Редактировать
                  </Link>
                  <button 
                    onClick={() => handleDeletePost(post.id)}
                    style={{ 
                      color: 'red', 
                      background: 'none', 
                      border: 'none', 
                      cursor: 'pointer',
                      textDecoration: 'underline'
                    }}
                  >
                    Удалить
                  </button>
                </div>
              )}
            </article>
          ))}
          
          {posts.length === 0 && (
            <p>Постов пока нет.</p>
          )}
        </div>
      </div>
    </section>
  );
};

export default BlogList;
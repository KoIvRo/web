import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { blogAPI } from '../services/api';
import avatar from '../assets/avatar.jpg';

const Home = () => {
  const [latestPosts, setLatestPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLatestPosts = async () => {
      try {
        setLoading(true);
        const posts = await blogAPI.getArticles();
        setLatestPosts(posts.slice(0, 2)); // Берем только 2 последних поста
      } catch (err) {
        setError('Ошибка при загрузке постов');
        console.error('Error fetching posts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLatestPosts();
  }, []);

  const isNewPost = (createdAt) => {
    const today = new Date().toISOString().slice(0, 10);
    return createdAt.slice(0, 10) === today;
  };

  return (
    <>
      <section className="hero">
        <div className="container">
          <img className="avatar" src={avatar} alt="Аватар" />
          <h1>Иван Коротаев</h1>
          <p className="lead">Backend • Python • Django</p>
          <p className="tiny">ДВФУ/ИМКТ/ПМИ/СП</p>

          <div className="actions">
            <a className="btn primary" href="https://t.me/krtvnrm" target="_blank" rel="noopener noreferrer">
              Написать
            </a>
            <a className="btn primary" href="tel:+77777777777">
              Позвонить
            </a>
          </div>
        </div>
      </section>

      <section id="about" className="about">
        <div className="container">
          <h2>Обо мне</h2>
          <p>Студент 2 курса ДВФУ, по направлению системное программирование</p>
          <p>С этого семестра являюсь студентом T - академий по направлению Backend-разработчик</p>
          <ul className="skills">
            <li>Django / Python</li>
            <li>HTML / CSS</li>
            <li>Pygame</li>
          </ul>
        </div>
      </section>

      <section id="blog" className="blog">
        <div className="container">
          <h2>Блог</h2>
          {loading && <p>Загрузка постов...</p>}
          {error && <p className="error">{error}</p>}
          
          <div className="posts">
            {latestPosts.map(post => (
              <article key={post.id} className="post">
                {isNewPost(post.created_at) && (
                  <p className="meta">Новое!</p>
                )}
                <h3><Link to={`/blog/${post.id}`}>{post.title}</Link></h3>
                <p className="meta">{post.category}</p>
                <p className="meta">{post.author}</p>
                <p className="meta">
                  {new Date(post.created_at).toLocaleString('ru-RU', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
                <p>{post.content.substring(0, 150)}...</p>
                <p><Link to={`/blog/${post.id}`}>Комментарии ({post.comments_count || 0})</Link></p>
              </article>
            ))}
            
            {!loading && latestPosts.length === 0 && (
              <p>Постов пока нет.</p>
            )}
          </div>
          
          {latestPosts.length > 0 && (
            <Link className="btn ghost" to="/blog">
              Все посты
            </Link>
          )}
        </div>
      </section>

      <section id="contact" className="contact">
        <div className="container">
          <h2>Контакты</h2>
          <p>Telegram: <a href="https://t.me/krtvnrm" target="_blank" rel="noopener noreferrer">@krtvnrm</a></p>
          <p>Телефон: <a href="tel:+77777777777">+7 777 777 77 77</a></p>
        </div>
      </section>
    </>
  );
};

export default Home;
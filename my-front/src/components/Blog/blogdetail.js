import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { blogAPI } from '../../services/api';
import { useAuth } from '../context/AuthContext';

const BlogDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const { isAuthenticated, user } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const postData = await blogAPI.getArticle(id);
        setPost(postData);
        try {
          const commentsData = await blogAPI.getComments(id);
          setComments(commentsData || []);
        } catch (commentsError) {
          console.error('Error loading comments:', commentsError);
          setComments([]);
        }
      } catch (err) {
        setError('Ошибка при загрузке поста');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim() || !user) return;

    setSubmitting(true);
    try {
      await blogAPI.createComment({
        text: commentText,
        post_id: parseInt(id),
        author_id: user.id
      });
      window.location.reload();
      
    } catch (err) {
      console.error('Error creating comment:', err);
      console.error('Error response:', err.response);

      if (err.response?.status !== 201) {
        alert('Ошибка при отправке комментария: ' + (err.response?.data?.detail || 'Неизвестная ошибка'));
      } else {
        window.location.reload();
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот комментарий?')) {
      try {
        await blogAPI.deleteComment(commentId);
        window.location.reload();
      } catch (err) {
        console.error('Error deleting comment:', err);
        alert('Ошибка при удалении комментария');
      }
    }
  };

  const handleDeletePost = async () => {
    if (window.confirm('Вы уверены, что хотите удалить этот пост?')) {
      try {
        await blogAPI.deleteArticle(id);
        navigate('/blog');
      } catch (err) {
        console.error('Error deleting post:', err);
        alert('Ошибка при удалении поста');
      }
    }
  };

  const canModifyPost = () => {
    return isAuthenticated && user && post && post.author_id === user.id;
  };

  const canModifyComment = () => {
    return isAuthenticated && user;
  };

  const renderComment = (comment) => {
    if (!comment) return null;

    return (
      <div key={comment.id} className="comment" style={{ 
        background: '#f8f9fa', 
        padding: '15px', 
        margin: '10px 0', 
        borderRadius: '5px' 
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>{comment.author_name || comment.author || 'Неизвестный автор'}</strong>
          <small style={{ color: '#666' }}>
            {comment.created_at ? new Date(comment.created_at).toLocaleString('ru-RU', {
              day: '2-digit',
              month: '2-digit',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            }) : 'Дата неизвестна'}
          </small>
        </div>
        <p style={{ margin: '10px 0 0 0', whiteSpace: 'pre-wrap' }}>
          {comment.text || 'Текст комментария отсутствует'}
        </p>
        
        {canModifyComment() && (
          <div style={{ marginTop: '10px' }}>
            <button 
              onClick={() => handleDeleteComment(comment.id)}
              style={{ 
                color: 'red', 
                background: 'none', 
                border: 'none', 
                cursor: 'pointer',
                textDecoration: 'underline',
                fontSize: '14px'
              }}
            >
              Удалить
            </button>
          </div>
        )}
      </div>
    );
  };

  if (loading) return <div className="container loading">Загрузка...</div>;
  if (error) return <div className="container error">{error}</div>;
  if (!post) return <div className="container">Пост не найден</div>;

  return (
    <section className="blog">
      <div className="container">
        <div style={{ marginBottom: '20px' }}>
          <Link to="/blog" className="btn ghost">← К списку постов</Link>
          <Link to="/" className="btn ghost" style={{ marginLeft: '10px' }}>На главную</Link>
        </div>

        <article className="post">
          <h2>{post.title}</h2>
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
          <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {post.content}
          </div>
          
          {canModifyPost() && (
            <div style={{ marginTop: '20px' }}>
              <Link 
                to={`/blog/edit/${post.id}`}
                style={{ color: '#0066cc', textDecoration: 'none', marginRight: '10px' }}
              >
                Редактировать
              </Link>
              <button 
                onClick={handleDeletePost}
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

        <div className="comments" style={{ marginTop: '40px' }}>
          <h3>Комментарии ({post.comments_count || comments.length})</h3>
          
          {comments.length > 0 ? (
            comments.map(comment => renderComment(comment))
          ) : (
            <p style={{ color: '#666', textAlign: 'center' }}>Комментариев пока нет</p>
          )}

          {isAuthenticated ? (
            <div className="comment-form" style={{ marginTop: '30px' }}>
              <h4>Оставить комментарий</h4>
              <form onSubmit={handleSubmitComment}>
                <div style={{ marginBottom: '15px' }}>
                  <textarea
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Введите ваш комментарий..."
                    style={{
                      width: '100%',
                      minHeight: '100px',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '5px',
                      resize: 'vertical'
                    }}
                    required
                  />
                </div>
                <button 
                  type="submit" 
                  className="btn primary"
                  disabled={submitting || !user}
                >
                  {submitting ? 'Отправка...' : 'Отправить комментарий'}
                </button>
              </form>
            </div>
          ) : (
            <p style={{ textAlign: 'center', marginTop: '20px' }}>
              <Link to="/login">Войдите</Link>, чтобы оставить комментарий
            </p>
          )}
        </div>
      </div>
    </section>
  );
};

export default BlogDetail;
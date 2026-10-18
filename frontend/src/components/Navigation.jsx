import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const Navigation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const username = authService.getUsername();

  const handleLogout = () => {
    authService.logout();
    navigate('/');
    window.location.reload();
  };

  return (
    <nav className="nav">
      <div className="container">
        <ul>
          <li>
            <Link 
              to="/" 
              className={location.pathname === '/' ? 'active' : ''}
            >
              Hotels
            </Link>
          </li>
          <li>
            <Link 
              to="/summaries" 
              className={location.pathname === '/summaries' ? 'active' : ''}
            >
              Review Summaries
            </Link>
          </li>
          <li>
            <Link 
              to="/analyze" 
              className={location.pathname === '/analyze' ? 'active' : ''}
            >
              Sentiment Analyzer
            </Link>
          </li>

          {!username ? (
            <>
              <li style={{ marginLeft: '1rem' }}>
                <Link 
                  to="/login" 
                  className={location.pathname === '/login' ? 'active' : ''}
                >
                  Login
                </Link>
              </li>
              <li style={{ marginLeft: '0.5rem' }}>
                <Link to="/register" className={location.pathname === '/register' ? 'active' : ''}>
                  Sign up
                </Link>
              </li>
            </>
          ) : (
            <li style={{ marginLeft: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: '#667eea', fontWeight: 600 }}>{username}</span>
              <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem' }}>
                Logout
              </button>
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;
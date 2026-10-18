import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../services/api';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      setStatus({ type: 'error', text: 'No token provided' });
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus(null);
    if (!password || password.length < 6) {
      setStatus({ type: 'error', text: 'Password must be at least 6 characters' });
      return;
    }
    if (password !== confirm) {
      setStatus({ type: 'error', text: 'Passwords do not match' });
      return;
    }
    setLoading(true);
    try {
      await authService.resetPassword(token, password);
      setStatus({ type: 'success', text: 'Password updated. Redirecting to login...' });
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setStatus({ type: 'error', text: err.response?.data?.detail || 'Reset failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 600, margin: '0 auto' }}>
        <h2>Set a new password</h2>

        {status && (
          <div className={status.type === 'error' ? 'error' : 'success'}>
            {status.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>New password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-control"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Confirm password</label>
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className="form-control"
              disabled={loading}
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn" type="submit" disabled={loading || !token}>
              {loading ? 'Updating...' : 'Update password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;

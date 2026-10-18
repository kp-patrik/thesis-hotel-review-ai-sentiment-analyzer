import React, { useState } from 'react';
import { authService } from '../services/api';

const RequestPasswordReset = () => {
  const [value, setValue] = useState('');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus(null);
    if (!value.trim()) {
      setStatus({ type: 'error', text: 'Please enter your username or email' });
      return;
    }
    setLoading(true);
    try {
      await authService.requestPasswordReset(value.trim());
      setStatus({ type: 'success', text: 'If that account exists, a reset link was sent.' });
    } catch (err) {
      setStatus({ type: 'error', text: err.response?.data?.detail || 'Request failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 600, margin: '0 auto' }}>
        <h2>Password reset</h2>
        <p style={{ color: '#666' }}>Enter your username or email and we'll send a password reset link if the account exists.</p>

        {status && (
          <div className={status.type === 'error' ? 'error' : 'success'}>
            {status.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username or Email</label>
            <input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="form-control"
              disabled={loading}
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn" type="submit" disabled={loading}>
              {loading ? 'Sending...' : 'Send reset link'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RequestPasswordReset;

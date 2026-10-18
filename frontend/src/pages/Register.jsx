import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const Register = () => {
  const [form, setForm] = useState({ username: '', password: '', email: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!form.username.trim() || !form.password.trim()) {
      setError('Please enter username and password');
      return;
    }

    setLoading(true);
    try {
      await authService.register(
        form.username.trim(),
        form.password,
        form.email.trim() || undefined
      );
      setSuccess('Account created. You can now log in.');
      setTimeout(() => navigate('/login'), 1000);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (detail) {
        setError(detail);
      } else if (err.request) {
        setError('Could not reach the backend. Make sure the API is running at http://localhost:8000.');
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 500, margin: '0 auto' }}>
        <h2>Create account</h2>

        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              className="form-control"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label>Email (optional)</label>
            <input
              name="email"
              value={form.email}
              onChange={handleChange}
              className="form-control"
              disabled={loading}
              type="email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              className="form-control"
              disabled={loading}
              placeholder="Choose a strong password"
              minLength={6}
              required
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn" type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create account'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/login')} disabled={loading}>
              Sign in
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;

import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { authService } from '../services/api';

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [status, setStatus] = useState({ type: 'loading', text: 'Verifying your email...' });

  useEffect(() => {
    if (!token) {
      setStatus({ type: 'error', text: 'No verification token was provided.' });
      return;
    }

    authService.verifyEmail(token)
      .then(() => setStatus({ type: 'success', text: 'Your email has been verified successfully.' }))
      .catch((error) => {
        setStatus({
          type: 'error',
          text: error.response?.data?.detail || 'This verification link is invalid or expired.'
        });
      });
  }, [token]);

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 600, margin: '0 auto' }}>
        <h2>Email verification</h2>
        <div className={status.type === 'error' ? 'error' : status.type === 'success' ? 'success' : 'loading'}>
          {status.text}
        </div>
        {status.type !== 'loading' && (
          <Link to="/login" className="btn" style={{ display: 'inline-block', marginTop: '1rem' }}>
            Go to login
          </Link>
        )}
      </div>
    </div>
  );
};

export default VerifyEmail;

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

export default function Signup() {
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    // Clear error when user starts typing
    if (error) setError('');
  };

  const validateForm = () => {
    if (!form.name.trim()) {
      setError('Name is required');
      return false;
    }
    if (!form.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(form.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Client-side validation
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const res = await api.post('/auth/signup', form);
      
      // Handle successful signup
      if (res.data.token) {
        // Auto-login after successful signup
        login(res.data.token, res.data.user || { name: form.name, email: form.email });
        navigate('/dashboard');
      } else {
        // If no token returned, redirect to login
        navigate('/login', { 
          state: { message: 'Account created successfully. Please login.' }
        });
      }
    } catch (err) {
      console.error('Signup error:', err);
      
      // Handle different error scenarios
      if (err.response?.data?.message) {
        setError(err.response.data.message);
      } else if (err.response?.status === 409) {
        setError('An account with this email already exists');
      } else if (err.response?.status >= 500) {
        setError('Server error. Please try again later');
      } else if (!navigator.onLine) {
        setError('No internet connection. Please check your connection and try again');
      } else {
        setError('Signup failed. Please try again');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Sign Up</h2>
        {error && <div className="error-msg">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="name">Name</label>
          <input 
            id="name" 
            name="name" 
            type="text"
            value={form.name} 
            onChange={handleChange} 
            disabled={loading}
            required 
            autoComplete="name"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input 
            id="email" 
            name="email" 
            type="email" 
            value={form.email} 
            onChange={handleChange} 
            disabled={loading}
            required 
            autoComplete="email"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input 
            id="password" 
            name="password" 
            type="password" 
            value={form.password} 
            onChange={handleChange} 
            disabled={loading}
            required 
            autoComplete="new-password"
            minLength="6"
          />
        </div>
        
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Creating Account...' : 'Sign Up'}
        </button>
        
        <p className="auth-link">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  );
}
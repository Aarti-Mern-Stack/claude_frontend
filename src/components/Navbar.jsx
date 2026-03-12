import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">MyApp</Link>
      <div className="navbar-links">
        {user ? (
          <>
            <span className="navbar-user">Hi, {user.name || user.email}</span>
            <Link to="/dashboard">Dashboard</Link>
            <button onClick={handleLogout} className="btn btn-logout">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/signup">Signup</Link>
          </>
        )}
      </div>
    </nav>
  );
}

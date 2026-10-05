import React, { useState } from 'react';
import axios from 'axios';

function Login({ onLoginSuccess }) {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    console.log('Intentando login con:', formData);
    try {
      const params = new URLSearchParams();
      params.append('username', formData.username);
      params.append('password', formData.password);

      const response = await axios.post('http://127.0.0.1:8000/token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      console.log('Respuesta recibida:', response.data);
      localStorage.setItem('token', response.data.access_token);
      onLoginSuccess();
    } catch (err) {
      console.error('Error detallado del login:', err.response || err);
      setError(err.response?.data?.detail || 'Error de conexión con el servidor');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Acceso Administrador</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Usuario</label>
            <input 
              type="text" 
              value={formData.username} 
              onChange={e => setFormData({...formData, username: e.target.value})} 
              required 
            />
          </div>
          <div className="form-group">
            <label>Contraseña</label>
            <input 
              type="password" 
              value={formData.password} 
              onChange={e => setFormData({...formData, password: e.target.value})} 
              required 
            />
          </div>
          {error && <p className="error-msg">{error}</p>}
          <button type="submit" className="btn-login">Entrar</button>
        </form>
      </div>
    </div>
  );
}

export default Login;

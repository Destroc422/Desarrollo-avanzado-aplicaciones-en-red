import React, { useState } from 'react';
import { useAuth } from '../../features/auth/AuthContext';
import { getApiErrorMessage } from '../../api/http';

export default function Login({ onCancel }) {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try { await login({ username, password }); }
    catch (err) { setError(getApiErrorMessage(err, 'No se pudo iniciar sesión.')); }
    finally { setBusy(false); }
  }

  return (
    <section className="auth-card" aria-labelledby="login-title">
      <h2 id="login-title">Iniciar sesión</h2>
      <p>Accede a tu cuenta o al panel del equipo.</p>
      <form onSubmit={submit}>
        <label>Usuario<input autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} required /></label>
        <label>Contraseña<input type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        {error && <p className="error-msg" role="alert">{error}</p>}
        <button className="button button-primary" disabled={busy}>{busy ? 'Ingresando…' : 'Entrar'}</button>
        {onCancel && <button className="button button-quiet" type="button" onClick={onCancel}>Volver</button>}
      </form>
    </section>
  );
}

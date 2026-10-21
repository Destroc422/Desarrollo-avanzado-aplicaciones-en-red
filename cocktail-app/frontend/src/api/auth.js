import api from './http';

export async function login(credentials) {
  const form = new URLSearchParams();
  form.append('username', credentials.username);
  form.append('password', credentials.password);
  const { data } = await api.post('/auth/token', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return data;
}

export async function register(payload) {
  const { data } = await api.post('/auth/register', payload);
  return data;
}

export async function getCurrentUser() {
  const { data } = await api.get('/auth/me');
  return data;
}

export async function logout() {
  await api.post('/auth/logout');
}

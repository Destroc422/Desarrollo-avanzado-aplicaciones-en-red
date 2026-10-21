import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { getCurrentUser, login as loginRequest, logout as logoutRequest, register as registerRequest } from '../../api/auth';
import { AUTH_UNAUTHORIZED_EVENT } from '../../api/http';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const current = await getCurrentUser();
      setUser(current);
      return current;
    } catch {
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
    const clearSession = () => setUser(null);
    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, clearSession);
    return () => window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, clearSession);
  }, [refreshUser]);

  const login = useCallback(async (credentials) => {
    const current = await loginRequest(credentials);
    setUser(current);
    return current;
  }, []);

  const register = useCallback(async (payload) => {
    const current = await registerRequest(payload);
    setUser(current);
    return current;
  }, []);

  const logout = useCallback(async () => {
    try { await logoutRequest(); } finally { setUser(null); }
  }, []);

  const value = useMemo(() => ({ user, loading, login, register, logout, refreshUser }), [user, loading, login, register, logout, refreshUser]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth debe utilizarse dentro de AuthProvider.');
  return value;
}

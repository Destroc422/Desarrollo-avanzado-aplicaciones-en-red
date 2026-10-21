import api from './http';

export const getBusinessInfo = async () => (await api.get('/business-info')).data;
export const listServiceAddons = async () => (await api.get('/service-addons')).data;
export const listServiceAddonsAdmin = async () => (await api.get('/service-addons/admin')).data;
export const createServiceAddon = async (payload) => (await api.post('/service-addons', payload)).data;
export const updateServiceAddon = async (id, payload) => (await api.put(`/service-addons/${id}`, payload)).data;
export const deleteServiceAddon = async (id) => api.delete(`/service-addons/${id}`);
export const searchExternalRecipes = async (params) => (await api.get('/external-catalog/recipes', { params })).data;

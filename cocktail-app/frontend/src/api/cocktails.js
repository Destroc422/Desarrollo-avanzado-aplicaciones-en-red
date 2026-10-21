import api from './http';

export const listCocktails = async (params = {}) => (await api.get('/cocktails', { params })).data;
export const listCocktailCategories = async () => (await api.get('/cocktails/categories')).data;
export const getCocktail = async (id) => (await api.get(`/cocktails/${id}`)).data;
export const listCocktailsAdmin = async () => (await api.get('/cocktails/admin')).data;
export const createCocktail = async (payload) => (await api.post('/cocktails', payload)).data;
export const updateCocktail = async (id, payload) => (await api.put(`/cocktails/${id}`, payload)).data;
export const deleteCocktail = async (id) => api.delete(`/cocktails/${id}`);
export const uploadCocktailImage = async (id, file) => {
  const form = new FormData();
  form.append('file', file);
  return (await api.post(`/uploads/cocktail/${id}`, form)).data;
};

import api from './http';

export const createOrder = async (payload) => (await api.post('/orders', payload)).data;
export const listMyOrders = async () => (await api.get('/orders/mine')).data;
export const listAllOrders = async () => (await api.get('/orders/admin')).data;
export const getPaymentConfig = async (orderId) => (await api.get(`/orders/${orderId}/payment-config`)).data;
export const updateOrderStatus = async (orderId, status) =>
  (await api.patch(`/orders/${orderId}/status`, { status })).data;

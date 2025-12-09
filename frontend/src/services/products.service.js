import api from './api';

const productsService = {
    getAll: async (params) => {
        const response = await api.get('/productos/', { params });
        return response.data;
    },

    getById: async (id) => {
        const response = await api.get(`/productos/${id}/`);
        return response.data;
    },

    create: async (data) => {
        const response = await api.post('/productos/', data);
        return response.data;
    },

    update: async (id, data) => {
        const response = await api.put(`/productos/${id}/`, data);
        return response.data;
    },

    delete: async (id) => {
        const response = await api.delete(`/productos/${id}/`);
        return response.data;
    },

    // Helper para calcular precio con IVA
    calculateTotal: (price, tax) => {
        const p = parseFloat(price) || 0;
        const t = parseFloat(tax) || 0;
        return p * (1 + t / 100);
    }
};

export default productsService;

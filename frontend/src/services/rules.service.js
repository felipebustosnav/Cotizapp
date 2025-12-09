import api from './api';

const rulesService = {
    getAll: async () => {
        const response = await api.get('/reglas-oferta/');
        return response.data;
    },

    create: async (data) => {
        const response = await api.post('/reglas-oferta/', data);
        return response.data;
    },

    update: async (id, data) => {
        const response = await api.put(`/reglas-oferta/${id}/`, data);
        return response.data;
    },

    delete: async (id) => {
        const response = await api.delete(`/reglas-oferta/${id}/`);
        return response.data;
    }
};

export default rulesService;

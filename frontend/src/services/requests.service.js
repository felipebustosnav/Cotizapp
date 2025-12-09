import api from './api';

const requestsService = {
    getAll: async () => {
        const response = await api.get('/solicitudes/');
        return response.data;
    },

    getById: async (id) => {
        const response = await api.get(`/solicitudes/${id}/`);
        return response.data;
    },

    create: async (payload) => {
        const response = await api.post('/solicitudes/', payload);
        return response.data;
    },

    approve: async (id) => {
        const response = await api.post(`/solicitudes/${id}/aprobar/`);
        return response.data;
    },

    reject: async (id, motivo) => {
        const response = await api.post(`/solicitudes/${id}/rechazar/`, { motivo });
        return response.data;
    },

    delete: async (id) => {
        const response = await api.delete(`/solicitudes/${id}/`);
        return response.data;
    }
};

export default requestsService;

import api from './api';

const taxesService = {
    /**
     * Obtiene todos los impuestos de la empresa
     */
    getAll: async (params = {}) => {
        const response = await api.get('/impuestos/', { params });
        return response.data;
    },

    /**
     * Obtiene solo los impuestos activos
     */
    getActive: async () => {
        const response = await api.get('/impuestos/activos/');
        return response.data;
    },

    /**
     * Obtiene un impuesto por ID
     */
    getById: async (id) => {
        const response = await api.get(`/impuestos/${id}/`);
        return response.data;
    },

    /**
     * Crea un nuevo impuesto
     */
    create: async (data) => {
        const response = await api.post('/impuestos/', data);
        return response.data;
    },

    /**
     * Actualiza un impuesto existente
     */
    update: async (id, data) => {
        const response = await api.put(`/impuestos/${id}/`, data);
        return response.data;
    },

    /**
     * Elimina (desactiva) un impuesto
     */
    delete: async (id) => {
        const response = await api.delete(`/impuestos/${id}/`);
        return response.data;
    },

    /**
     * Activa/Desactiva un impuesto
     */
    toggleActive: async (id, activo) => {
        const response = await api.patch(`/impuestos/${id}/`, { activo });
        return response.data;
    }
};

export default taxesService;

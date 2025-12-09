import api from './api';

const quotationsService = {
    getAll: async (params) => {
        const response = await api.get('/cotizaciones/', { params });
        return response.data;
    },

    getById: async (id) => {
        const response = await api.get(`/cotizaciones/${id}/`);
        return response.data;
    },

    create: async (data) => {
        const response = await api.post('/cotizaciones/', data);
        return response.data;
    },

    update: async (id, data) => {
        const response = await api.put(`/cotizaciones/${id}/`, data);
        return response.data;
    },

    delete: async (id) => {
        const response = await api.delete(`/cotizaciones/${id}/`);
        return response.data;
    },

    generatePdf: async (id) => {
        const response = await api.get(`/cotizaciones/${id}/pdf/`, {
            responseType: 'blob'
        });
        return response.data;
    },

    approve: async (id) => {
        const response = await api.post(`/cotizaciones/${id}/aprobar/`);
        return response.data;
    },

    markAsAccepted: async (id) => {
        const response = await api.post(`/cotizaciones/${id}/marcar_aceptada/`);
        return response.data;
    },

    reject: async (id, motivo) => {
        const response = await api.post(`/cotizaciones/${id}/rechazar/`, { motivo });
        return response.data;
    },

    resend: async (id) => {
        const response = await api.post(`/cotizaciones/${id}/reenviar/`);
        return response.data;
    },

    requestChange: async (id, mensaje) => {
        const response = await api.post(`/cotizaciones/${id}/solicitar_cambio/`, { mensaje });
        return response.data;
    },

    getPendingStats: async () => {
        const response = await api.get('/cotizaciones/pending_stats/');
        return response.data;
    },

    // Manejo de estados y colores
    getStatusInfo: (status) => {
        const states = {
            BORRADOR: { label: 'Borrador', class: 'badge-secondary' },
            ENVIADA: { label: 'Enviada', class: 'badge-info' },
            ACEPTADA: { label: 'Aceptada', class: 'badge-success' },
            RECHAZADA: { label: 'Rechazada', class: 'badge-danger' }
        };
        return states[status] || states.BORRADOR;
    }
};

export default quotationsService;

import api from './api';

const publicService = {
    getCompanyInfo: async (slug) => {
        const response = await api.get(`/autoatencion/${slug}/`);
        return response.data;
    },

    createQuotation: async (slug, data) => {
        const response = await api.post(`/autoatencion/${slug}/cotizar/`, data);
        return response.data;
    },

    getQuotationByUuid: async (uuid) => {
        const response = await api.get('/cotizaciones/public_detail/', { params: { uuid } });
        return response.data;
    },

    acceptQuotation: async (uuid) => {
        const response = await api.post('/cotizaciones/public_accept/', { uuid });
        return response.data;
    },

    rejectQuotation: async (uuid, motivo) => {
        const response = await api.post('/cotizaciones/public_reject/', { uuid, motivo });
        return response.data;
    }
};

export default publicService;

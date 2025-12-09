import api from './api';

const companyService = {
    // Obtener datos de la empresa del usuario actual
    getMyCompany: async () => {
        try {
            const response = await api.get('/empresa/mi_empresa/');
            return response.data;
        } catch (error) {
            console.error('Error fetching company:', error);
            throw error;
        }
    },

    // Actualizar datos de la empresa (soporta archivos)
    update: async (id, data) => {
        try {
            // Si hay archivos, usar Multipart/Form-Data
            const isMultipart = data instanceof FormData;

            const config = {
                headers: {
                    // No establecer Content-Type para FormData, dejar que el navegador/axios lo maneje
                    ...(isMultipart ? {} : { 'Content-Type': 'application/json' })
                }
            };

            const response = await api.patch(`/empresa/${id}/`, data, config);
            return response.data;
        } catch (error) {
            console.error('Error updating company:', error);
            throw error;
        }
    }
};

export default companyService;

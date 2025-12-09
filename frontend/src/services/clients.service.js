import api from './api';

const clientsService = {
    getAll: async (params) => {
        const response = await api.get('/clientes/', { params });
        return response.data;
    },

    getById: async (id) => {
        const response = await api.get(`/clientes/${id}/`);
        return response.data;
    },

    create: async (data) => {
        const response = await api.post('/clientes/', data);
        return response.data;
    },

    update: async (id, data) => {
        const response = await api.put(`/clientes/${id}/`, data);
        return response.data;
    },

    delete: async (id) => {
        const response = await api.delete(`/clientes/${id}/`);
        return response.data;
    },

    // Validador de RUT Chileno
    validateRut: (rut) => {
        if (!rut) return true; // Permitir vacío si no es requerido

        // Limpiar formato
        let valor = rut.replace(/\./g, '').replace(/-/g, '');

        // Aislar Cuerpo y Dígito Verificador
        let cuerpo = valor.slice(0, -1);
        let dv = valor.slice(-1).toUpperCase();

        // Si no cumple con el mínimo ej. (n.nnn.nnn)
        if (cuerpo.length < 7) {
            return false;
        }

        // Calcular Dígito Verificador
        let suma = 0;
        let multiplo = 2;

        // Para cada dígito del Cuerpo
        for (let i = 1; i <= cuerpo.length; i++) {
            // Obtener su Producto con el Múltiplo Correspondiente
            let index = multiplo * valor.charAt(cuerpo.length - i);

            // Sumar al Contador General
            suma = suma + index;

            // Consolidar Múltiplo dentro del rango [2,7]
            if (multiplo < 7) {
                multiplo = multiplo + 1;
            } else {
                multiplo = 2;
            }
        }

        // Calcular Dígito Verificador en base al Módulo 11
        let dvEsperado = 11 - (suma % 11);

        // Casos Especiales (0 y K)
        dv = (dv == 'K') ? 10 : dv;
        dv = (dv == 0) ? 11 : dv;

        // Validar que el Cuerpo coincide con su Dígito Verificador
        if (dvEsperado != dv) {
            return false;
        }

        return true;
    },

    formatRut: (rut) => {
        if (!rut) return '';
        let valor = rut.replace(/\./g, '').replace(/-/g, '');
        if (valor.length > 1) {
            let cuerpo = valor.slice(0, -1);
            let dv = valor.slice(-1).toUpperCase();
            return `${cuerpo}-${dv}`;
        }
        return valor;
    }
};

export default clientsService;

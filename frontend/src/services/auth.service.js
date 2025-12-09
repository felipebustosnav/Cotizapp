import api from './api';

const authService = {
    // Login
    login: async (email, password) => {
        const response = await api.post('/auth/login/', { email, password });
        const { access, refresh } = response.data;

        // Guardar tokens
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);

        return response.data;
    },

    // Logout
    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },

    // Obtener usuario actual
    registerCompany: async (data) => {
        try {
            const response = await api.post('/auth/register-company/', data);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    getCurrentUser: async () => {
        const response = await api.get('/usuarios/me/');
        localStorage.setItem('user', JSON.stringify(response.data));
        return response.data;
    },

    // Verificar si está autenticado
    isAuthenticated: () => {
        return !!localStorage.getItem('access_token');
    },

    // Obtener usuario del localStorage
    getUser: () => {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },
};

export default authService;

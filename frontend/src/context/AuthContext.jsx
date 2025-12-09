import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/auth.service';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Verificar si hay un usuario en localStorage al cargar
        const loadUser = async () => {
            try {
                if (authService.isAuthenticated()) {
                    const userData = authService.getUser();
                    if (userData) {
                        setUser(userData);
                    } else {
                        // Si no hay datos del usuario, obtenerlos del servidor
                        const currentUser = await authService.getCurrentUser();
                        setUser(currentUser);
                    }
                }
            } catch (error) {
                console.error('Error loading user:', error);
                authService.logout();
            } finally {
                setLoading(false);
            }
        };

        loadUser();
    }, []);

    const login = async (email, password) => {
        try {
            await authService.login(email, password);
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Error al iniciar sesión',
            };
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    const value = {
        user,
        login,
        logout,
        loading,
        isAuthenticated: !!user,
        isAdmin: user?.rol === 'ADMIN',
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default AuthContext;

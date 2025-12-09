import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, allowPasswordChange = false }) => {
    const { isAuthenticated, loading, user } = useAuth();

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="spinner"></div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // Force password change if required and not already on the change page
    if (user?.cambio_password_obligatorio && !allowPasswordChange) {
        return <Navigate to="/change-password" replace />;
    }

    return children;
};

export default ProtectedRoute;

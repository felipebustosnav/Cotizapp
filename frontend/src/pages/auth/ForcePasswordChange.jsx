import React, { useState } from 'react';
import { Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import authService from '../../services/auth.service';

const ForcePasswordChange = () => {
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    // Auth context to refresh user data
    const { logout } = useAuth(); // We might need to refresh context user instead of full logout/login?
    // Actually simpler to just refresh user data
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (newPassword !== confirmPassword) {
            setError("Las nuevas contraseñas no coinciden.");
            return;
        }

        if (newPassword.length < 8) {
            setError("La nueva contraseña debe tener al menos 8 caracteres.");
            return;
        }

        setLoading(true);

        try {
            await api.post('/auth/change-password/', {
                old_password: oldPassword,
                new_password: newPassword,
                confirm_new_password: confirmPassword
            });

            // Password changed successfully.
            // Refresh user data to clear the flag
            await authService.getCurrentUser();

            // Reload page or navigate to home to trigger context update?
            // Since AuthContext doesn't expose a 'refreshUser' method easily without page reload or custom logic.
            // A full reload works:
            window.location.href = '/';

        } catch (err) {
            console.error(err);
            if (err.response && err.response.data) {
                // Formatting Django errors
                const data = err.response.data;
                let msg = "Error al cambiar contraseña.";
                if (data.old_password) msg = data.old_password[0];
                if (data.new_password) msg = data.new_password[0];
                if (data.detail) msg = data.detail;
                setError(msg);
            } else {
                setError("Error de conexión. Intente nuevamente.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="d-flex justify-content-center align-items-center vh-100 bg-light">
            <Card className="shadow-lg p-4" style={{ width: '400px' }}>
                <Card.Body>
                    <div className="text-center mb-4">
                        <i className="bi bi-shield-lock-fill text-warning" style={{ fontSize: '3rem' }}></i>
                        <h4 className="mt-2 text-dark fw-bold">Seguridad de Cuenta</h4>
                        <p className="text-muted small">
                            Por razones de seguridad, debes cambiar tu contraseña temporal antes de continuar.
                        </p>
                    </div>

                    {error && <Alert variant="danger" className="small">{error}</Alert>}

                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>Contraseña Temporal (Actual)</Form.Label>
                            <Form.Control
                                type="password"
                                required
                                value={oldPassword}
                                onChange={(e) => setOldPassword(e.target.value)}
                                placeholder="Ingresa la contraseña que recibiste"
                            />
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Nueva Contraseña</Form.Label>
                            <Form.Control
                                type="password"
                                required
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                placeholder="Mínimo 8 caracteres"
                            />
                        </Form.Group>

                        <Form.Group className="mb-4">
                            <Form.Label>Confirmar Nueva Contraseña</Form.Label>
                            <Form.Control
                                type="password"
                                required
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="Repite la nueva contraseña"
                            />
                        </Form.Group>

                        <div className="d-grid gap-2">
                            <Button variant="primary" type="submit" disabled={loading}>
                                {loading ? <Spinner size="sm" animation="border" /> : 'Establecer Contraseña'}
                            </Button>
                            <Button variant="link" size="sm" className="text-muted text-decoration-none" onClick={logout}>
                                Cerrar Sesión
                            </Button>
                        </div>
                    </Form>
                </Card.Body>
            </Card>
        </div>
    );
};

export default ForcePasswordChange;

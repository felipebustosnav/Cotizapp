import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { FiMail, FiLock, FiAlertCircle } from 'react-icons/fi';
import './Login.css';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const result = await login(email, password);

            if (result.success) {
                navigate('/');
            } else {
                setError(result.error || 'Error al iniciar sesión');
            }
        } catch (err) {
            setError('Error de conexión. Intente nuevamente.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1>CotizApp</h1>
                    <p>Inicia sesión en tu cuenta</p>
                </div>

                {error && (
                    <div className="alert-custom alert-danger">
                        <FiAlertCircle size={20} />
                        <span>{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group-custom">
                        <label className="form-label-custom">
                            <FiMail size={16} />
                            Correo electrónico
                        </label>
                        <input
                            type="email"
                            className="form-control-custom"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="tu@email.com"
                            required
                            autoFocus
                        />
                    </div>

                    <div className="form-group-custom">
                        <label className="form-label-custom">
                            <FiLock size={16} />
                            Contraseña
                        </label>
                        <input
                            type="password"
                            className="form-control-custom"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn-custom btn-primary btn-lg"
                        disabled={loading}
                        style={{ width: '100%', justifyContent: 'center' }}
                    >
                        {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                    </button>
                </form>

                <div className="login-footer">
                    <p style={{ marginBottom: '5px' }}>¿Olvidaste tu contraseña?</p>
                    <p>¿No tienes una cuenta? <Link to="/register" style={{ color: 'var(--primary-color)', fontWeight: 'bold' }}>Regístrate aquí</Link></p>
                </div>
            </div>

            <div className="login-info">
                <h2>Sistema de Cotizaciones para PYMEs</h2>
                <p style={{ fontSize: '1.1rem', fontWeight: '500', marginBottom: '20px' }}>
                    🎉 <strong>100% Gratuito</strong> - Diseñado especialmente para pequeñas y medianas empresas
                </p>
                <ul>
                    <li>✓ Gestión de productos y clientes</li>
                    <li>✓ Creación de cotizaciones profesionales</li>
                    <li>✓ Generación de PDFs automática</li>
                    <li>✓ Link de autoatención para clientes</li>
                    <li>✓ Sin límites, sin cargos ocultos</li>
                </ul>
            </div>
        </div>
    );
};

export default Login;

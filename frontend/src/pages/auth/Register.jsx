import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import authService from '../../services/auth.service';
import { FiMail, FiLock, FiUser, FiBriefcase, FiPhone, FiCreditCard, FiAlertCircle, FiCheckCircle } from 'react-icons/fi';
import './Login.css'; // Reutilizamos estilos de login

const Register = () => {
    const navigate = useNavigate();
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    const { register, handleSubmit, watch, formState: { errors } } = useForm();
    const password = watch('password');

    const onSubmit = async (data) => {
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            await authService.registerCompany(data);
            setSuccess('Cuenta creada exitosamente. Redirigiendo al login...');

            setTimeout(() => {
                navigate('/login');
            }, 2000);

        } catch (err) {
            console.error(err);
            const errorMsg = err.response?.data?.detail || 'Error al registrar empresa. Intente nuevamente.';
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card" style={{ maxWidth: '500px' }}> {/* Un poco más ancho */}
                <div className="login-header">
                    <h1>Crear Cuenta</h1>
                    <p>Registra tu empresa y comienza a cotizar</p>
                </div>

                {error && (
                    <div className="alert-custom alert-danger">
                        <FiAlertCircle size={20} />
                        <span>{error}</span>
                    </div>
                )}

                {success && (
                    <div className="alert-custom alert-success">
                        <FiCheckCircle size={20} />
                        <span>{success}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit(onSubmit)} className="login-form">

                    {/* Sección Empresa */}
                    <div style={{ marginBottom: '15px' }}>
                        <h4 className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase' }}>Datos de Empresa</h4>

                        <div className="form-group-custom">
                            <label className="form-label-custom">
                                <FiBriefcase size={16} /> Nombre Empresa *
                            </label>
                            <input
                                {...register('empresa_nombre', { required: 'Nombre de empresa es obligatorio' })}
                                className="form-control-custom"
                                placeholder="Ej: Mi Pyme SpA"
                            />
                            {errors.empresa_nombre && <span className="form-error">{errors.empresa_nombre.message}</span>}
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                            <div className="form-group-custom">
                                <label className="form-label-custom">
                                    <FiCreditCard size={16} /> RUT (Opcional)
                                </label>
                                <input
                                    {...register('rut')}
                                    className="form-control-custom"
                                    placeholder="76.123.456-7"
                                />
                            </div>
                            <div className="form-group-custom">
                                <label className="form-label-custom">
                                    <FiPhone size={16} /> Teléfono
                                </label>
                                <input
                                    {...register('telefono')}
                                    className="form-control-custom"
                                    placeholder="+569..."
                                />
                            </div>
                        </div>
                    </div>

                    {/* Sección Usuario */}
                    <div style={{ marginBottom: '15px', borderTop: '1px solid #eee', paddingTop: '15px' }}>
                        <h4 className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase' }}>Datos Administrador</h4>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                            <div className="form-group-custom">
                                <label className="form-label-custom">
                                    <FiUser size={16} /> Nombre *
                                </label>
                                <input
                                    {...register('first_name', { required: 'Obligatorio' })}
                                    className="form-control-custom"
                                />
                                {errors.first_name && <span className="form-error">{errors.first_name.message}</span>}
                            </div>
                            <div className="form-group-custom">
                                <label className="form-label-custom">
                                    <FiUser size={16} /> Apellido *
                                </label>
                                <input
                                    {...register('last_name', { required: 'Obligatorio' })}
                                    className="form-control-custom"
                                />
                                {errors.last_name && <span className="form-error">{errors.last_name.message}</span>}
                            </div>
                        </div>

                        <div className="form-group-custom">
                            <label className="form-label-custom">
                                <FiMail size={16} /> Email *
                            </label>
                            <input
                                type="email"
                                {...register('email', {
                                    required: 'Email es obligatorio',
                                    pattern: {
                                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                        message: "Email inválido"
                                    }
                                })}
                                className="form-control-custom"
                                placeholder="admin@empresa.com"
                            />
                            {errors.email && <span className="form-error">{errors.email.message}</span>}
                        </div>

                        <div className="form-group-custom">
                            <label className="form-label-custom">
                                <FiLock size={16} /> Contraseña *
                            </label>
                            <input
                                type="password"
                                {...register('password', {
                                    required: 'Contraseña obligatoria',
                                    minLength: {
                                        value: 6,
                                        message: "Mínimo 6 caracteres"
                                    }
                                })}
                                className="form-control-custom"
                                placeholder="••••••••"
                            />
                            {errors.password && <span className="form-error">{errors.password.message}</span>}
                        </div>

                        <div className="form-group-custom">
                            <label className="form-label-custom">
                                <FiLock size={16} /> Confirmar Contraseña *
                            </label>
                            <input
                                type="password"
                                {...register('confirm_password', {
                                    required: 'Confirme su contraseña',
                                    validate: value => value === password || "Las contraseñas no coinciden"
                                })}
                                className="form-control-custom"
                                placeholder="••••••••"
                            />
                            {errors.confirm_password && <span className="form-error">{errors.confirm_password.message}</span>}
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="btn-custom btn-primary btn-lg"
                        disabled={loading}
                        style={{ width: '100%', justifyContent: 'center', marginTop: '10px' }}
                    >
                        {loading ? 'Creando cuenta...' : 'Registrar Empresa'}
                    </button>
                </form>

                <div className="login-footer">
                    <p>¿Ya tienes una cuenta? <Link to="/login" style={{ color: 'var(--primary-color)', fontWeight: 'bold' }}>Inicia Sesión</Link></p>
                </div>
            </div>

            <div className="login-info">
                <h2>Únete a CotizApp - Gratis para PYMEs</h2>
                <p style={{ fontSize: '1.1rem', fontWeight: '500', marginBottom: '20px' }}>
                    🎉 <strong>Totalmente Gratuito</strong> - Sin costos ocultos, sin límites
                </p>
                <ul>
                    <li>✓ Portal de autoatención propio</li>
                    <li>✓ Logo y marca personalizada</li>
                    <li>✓ Gestión ilimitada de productos</li>
                    <li>✓ Exportación a PDF y WhatsApp</li>
                    <li>✓ Ideal para pequeñas y medianas empresas</li>
                </ul>
            </div>
        </div>
    );
};

export default Register;

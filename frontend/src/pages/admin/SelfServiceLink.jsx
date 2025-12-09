import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import authService from '../../services/auth.service';
import { FiLink, FiCopy, FiExternalLink, FiGlobe, FiInfo } from 'react-icons/fi';

const SelfServiceLink = () => {
    const { user } = useAuth();
    const [localCompanySlug, setLocalCompanySlug] = useState(null);

    useEffect(() => {
        const fetchUserData = async () => {
            // Si el usuario del contexto ya tiene el slug, usarlo
            if (user?.empresa_slug || user?.empresa?.slug_autoatencion) {
                setLocalCompanySlug(user.empresa_slug || user.empresa.slug_autoatencion);
                return;
            }

            // Si no, intentar refescar los datos del usuario desde el backend
            try {
                const updatedUser = await authService.getCurrentUser();
                if (updatedUser?.empresa_slug) {
                    setLocalCompanySlug(updatedUser.empresa_slug);
                }
            } catch (error) {
                console.error("Error refreshing user data", error);
            }
        };
        fetchUserData();
    }, [user]);

    // Fallback inteligente
    const slugToUse = localCompanySlug || user?.empresa_slug || user?.empresa?.slug_autoatencion || 'mi-empresa';
    const publicUrl = `${window.location.origin}/autoatencion/${slugToUse}`;

    const copyToClipboard = () => {
        navigator.clipboard.writeText(publicUrl);
        alert('¡Enlace copiado al portapapeles!');
    };

    return (
        <div className="container-custom">
            <div className="card-header-custom" style={{ marginTop: '20px', borderBottom: 'none' }}>
                <div>
                    <h2>Link de Autoatención</h2>
                    <p className="text-muted">Comparte este enlace con tus clientes para que soliciten cotizaciones</p>
                </div>
            </div>

            <div className="card-custom" style={{ textAlign: 'center', padding: '60px 20px' }}>
                <div style={{
                    width: '80px',
                    height: '80px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--orange-light)',
                    color: 'var(--primary-orange)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px auto'
                }}>
                    <FiGlobe size={40} />
                </div>

                <h3 style={{ marginBottom: '10px' }}>Tu Portal de Cotizaciones 24/7</h3>
                <p className="text-muted" style={{ maxWidth: '600px', margin: '0 auto 30px auto' }}>
                    Tus clientes pueden ingresar a este enlace para ver tu catálogo (si lo habilitas) y solicitar cotizaciones directamente. Las solicitudes aparecerán en tu panel como "Borrador".
                </p>

                <div className="alert-custom alert-info" style={{ maxWidth: '600px', margin: '0 auto 30px auto', textAlign: 'left', display: 'flex', gap: '10px' }}>
                    <FiInfo size={20} style={{ minWidth: '20px' }} />
                    <span>
                        <strong>Tip:</strong> Puedes personalizar el mensaje de bienvenida y las notificaciones que reciben tus clientes en la sección de <a href="/configuracion" style={{ color: 'inherit', textDecoration: 'underline' }}>Configuración de Empresa</a>.
                    </span>
                </div>

                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '10px',
                    maxWidth: '600px',
                    margin: '0 auto',
                    flexWrap: 'wrap'
                }}>
                    <div style={{
                        flex: 1,
                        padding: '12px 15px',
                        backgroundColor: 'var(--gray-100)',
                        borderRadius: '8px',
                        border: '1px solid var(--gray-300)',
                        fontFamily: 'monospace',
                        color: 'var(--text-dark)',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                    }}>
                        {publicUrl}
                    </div>

                    <button className="btn-custom btn-primary" onClick={copyToClipboard}>
                        <FiCopy size={18} style={{ marginRight: '5px' }} /> Copiar
                    </button>

                    <a
                        href={publicUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-custom btn-secondary"
                        style={{ textDecoration: 'none', display: 'flex', alignItems: 'center' }}
                    >
                        <FiExternalLink size={18} style={{ marginRight: '5px' }} /> Abrir
                    </a>
                </div>
            </div>
        </div >
    );
};

export default SelfServiceLink;

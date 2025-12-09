import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    FiHome,
    FiPackage,
    FiUsers,
    FiFileText,
    FiPercent,
    FiLink,
    FiSettings,
    FiMenu,
    FiX,
    FiBarChart2,
    FiBriefcase,
    FiCheck,
    FiInbox
} from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import './Sidebar.css';

import companyService from '../../services/company.service';
import quotationsService from '../../services/quotations.service';
import requestsService from '../../services/requests.service';
import { useNotifications } from '../../context/NotificationContext';

const Sidebar = () => {
    const location = useLocation();
    const { user } = useAuth();
    const { refreshTrigger } = useNotifications();
    const [isOpen, setIsOpen] = useState(false);
    const [logoUrl, setLogoUrl] = useState(null);
    const [companyName, setCompanyName] = useState('');
    const [pendingCount, setPendingCount] = useState(0); // Borradores Públicos
    const [requestCount, setRequestCount] = useState(0); // Solicitudes de Cambio

    React.useEffect(() => {
        const fetchCompanyData = async () => {
            try {
                const data = await companyService.getMyCompany();
                setCompanyName(data.nombre || '');
                if (data.logo_url) {
                    setLogoUrl(data.logo_url);
                }
            } catch (err) {
                console.error("Error loading company data", err);
            }
        };
        fetchCompanyData();
    }, []);

    // Auto-refresh pending quotations count every 30 seconds
    useEffect(() => {
        const fetchPendingStats = async () => {
            try {
                console.log('Fetching pending stats...');
                const stats = await quotationsService.getPendingStats();
                console.log('Pending stats received:', stats);
                // Backend returns { count: N }, but checking both just in case
                setPendingCount(stats.count !== undefined ? stats.count : (stats.pendientes || 0));

                if (user?.rol === 'ADMIN') {
                    const reqs = await requestsService.getAll();
                    const results = Array.isArray(reqs) ? reqs : (reqs.results || []);
                    const pendingReqs = results.filter(r => r.estado === 'PENDIENTE').length;
                    setRequestCount(pendingReqs);
                }
            } catch (err) {
                console.error('Error fetching pending stats:', err);
            }
        };

        // Fetch inicial
        fetchPendingStats();

        // Polling cada 30 segundos
        const interval = setInterval(fetchPendingStats, 30000);

        // Cleanup
        return () => clearInterval(interval);
    }, [refreshTrigger, user]); // Se ejecuta cuando refreshTrigger cambia

    const menuItems = [
        { path: '/', icon: FiHome, label: 'Dashboard' },
        { path: '/productos', icon: FiPackage, label: 'Productos' },
        { path: '/clientes', icon: FiUsers, label: 'Clientes' },
        { path: '/cotizaciones', icon: FiFileText, label: 'Cotizaciones', badge: pendingCount },
        { path: '/impuestos', icon: FiPercent, label: 'Impuestos' },
        // Panel de Solicitudes para el Empleado (sus propias solicitudes)
        // Panel de Solicitudes para el Empleado (sus propias solicitudes) - Solo visible si NO es admin
        ...(user?.rol !== 'ADMIN' ? [
            { path: '/mis-solicitudes', icon: FiInbox, label: 'Mis Solicitudes' }
        ] : []),
        ...(user?.rol === 'ADMIN' ? [
            { path: '/solicitudes', icon: FiCheck, label: 'Gestión Solicitudes', badge: requestCount },
            { path: '/reportes', icon: FiBarChart2, label: 'Reportes' },
            { path: '/empleados', icon: FiBriefcase, label: 'Empleados' },
            { path: '/configuracion', icon: FiSettings, label: 'Configuración' },
        ] : []),
        { path: '/autoatencion', icon: FiLink, label: 'Link Autoatención' },
    ];

    const toggleSidebar = () => {
        setIsOpen(!isOpen);
    };

    return (
        <>
            {/* Botón hamburguesa para móvil */}
            <button className="sidebar-toggle" onClick={toggleSidebar}>
                {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>

            {/* Overlay para móvil */}
            {isOpen && <div className="sidebar-overlay" onClick={toggleSidebar} />}

            {/* Sidebar */}
            <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-logo" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {/* 1. Marca CotizApp (Estilo Login) */}
                        <div style={{ display: 'flex', alignItems: 'center', paddingLeft: '5px' }}>
                            <span style={{
                                fontFamily: 'var(--font-headings)',
                                fontSize: '28px',
                                fontWeight: '700',
                                background: 'linear-gradient(135deg, var(--primary-orange), var(--accent-coral))',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text',
                                letterSpacing: '-0.5px',
                                lineHeight: '1.2'
                            }}>CotizApp</span>
                        </div>

                        {/* 2. Información de Empresa */}
                        <div className="sidebar-company-data" style={{ paddingLeft: '5px' }}>
                            {logoUrl ? (
                                <img src={logoUrl} alt="Logo Empresa" className="sidebar-logo-img" style={{ maxHeight: '40px', objectFit: 'contain', margin: '0', display: 'block' }} />
                            ) : (
                                companyName && (
                                    <div style={{ fontSize: '13px', color: 'var(--gray-600)', fontWeight: '500', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                        {companyName}
                                    </div>
                                )
                            )}
                        </div>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {menuItems.map((item) => {
                        const Icon = item.icon;

                        // Si es cotizaciones y hay pendientes, agregar query param al link
                        const isCotizaciones = item.path === '/cotizaciones';
                        const linkTo = (isCotizaciones && pendingCount > 0)
                            ? `${item.path}?pending=true`
                            : item.path;

                        // Verificar active exacto para path base, ignorando query params para estilo visual básico,
                        // pero usamos location.pathname para coincidencia exacta de ruta
                        const isActive = location.pathname === item.path;

                        return (
                            <Link
                                key={item.path}
                                to={linkTo}
                                className={`sidebar-item ${isActive ? 'sidebar-item-active' : ''}`}
                                onClick={() => setIsOpen(false)}
                                style={{ position: 'relative' }}
                            >
                                <Icon size={20} />
                                <span>{item.label}</span>
                                {item.badge > 0 && (
                                    <span style={{
                                        position: 'absolute',
                                        right: '15px',
                                        top: '50%',
                                        transform: 'translateY(-50%)',
                                        backgroundColor: 'var(--danger-red)',
                                        color: 'white',
                                        borderRadius: '12px',
                                        padding: '2px 8px',
                                        fontSize: '12px',
                                        fontWeight: 'bold',
                                        minWidth: '20px',
                                        textAlign: 'center'
                                    }}>
                                        {item.badge}
                                    </span>
                                )}
                            </Link>
                        );
                    })}
                </nav>

                {/* Usuario info (bottom) */}
                <div className="sidebar-user">
                    <div className="sidebar-user-avatar">
                        {user?.first_name?.[0]}{user?.last_name?.[0]}
                    </div>
                    <div className="sidebar-user-info">
                        <p className="sidebar-user-name">{user?.first_name} {user?.last_name}</p>
                        <p className="sidebar-user-role">
                            {user?.rol === 'ADMIN' ? 'Administrador' : 'Empleado'}
                        </p>
                    </div>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;

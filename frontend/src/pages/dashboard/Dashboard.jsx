import React, { useEffect, useState } from 'react';
import { FiFileText, FiUsers, FiPackage, FiDollarSign, FiPlus } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './Dashboard.css';

const Dashboard = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        cotizaciones: 0,
        clientes: 0,
        productos: 0,
        ingresos: 0,
    });
    const [recentQuotations, setRecentQuotations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            // Obtener estadísticas
            const [cotizacionesRes, clientesRes, productosRes] = await Promise.all([
                api.get('/cotizaciones/'),
                api.get('/clientes/'),
                api.get('/productos/'),
            ]);

            setStats({
                cotizaciones: cotizacionesRes.data.count || cotizacionesRes.data.results?.length || 0,
                clientes: clientesRes.data.count || clientesRes.data.results?.length || 0,
                productos: productosRes.data.count || productosRes.data.results?.length || 0,
                ingresos: calculateIngresos(cotizacionesRes.data.results || []),
            });

            // Obtener cotizaciones recientes (últimas 5)
            const recent = (cotizacionesRes.data.results || []).slice(0, 5);
            setRecentQuotations(recent);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const calculateIngresos = (cotizaciones) => {
        return cotizaciones
            .filter((c) => c.estado === 'ACEPTADA')
            .reduce((sum, c) => sum + parseFloat(c.total || 0), 0);
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('es-CL', {
            style: 'currency',
            currency: 'CLP',
        }).format(value);
    };

    const getStatusBadge = (status) => {
        const badges = {
            BORRADOR: 'badge-secondary',
            ENVIADA: 'badge-info',
            ACEPTADA: 'badge-success',
            RECHAZADA: 'badge-danger',
        };
        return badges[status] || 'badge-secondary';
    };

    const getStatusLabel = (status) => {
        const labels = {
            BORRADOR: 'Borrador',
            ENVIADA: 'Enviada',
            ACEPTADA: 'Aceptada',
            RECHAZADA: 'Rechazada',
        };
        return labels[status] || status;
    };

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <div>
                    <h1>Dashboard</h1>
                    <p>Bienvenido a tu panel de control</p>
                </div>
                <button
                    className="btn-custom btn-primary btn-lg"
                    onClick={() => navigate('/cotizaciones/nuevo')}
                >
                    <FiPlus size={20} />
                    Nueva Cotización
                </button>
            </div>

            {/* Tarjetas de estadísticas */}
            <div className="dashboard-stats">
                <div className="card-stat">
                    <div className="card-stat-icon">
                        <FiFileText size={32} />
                    </div>
                    <div>
                        <div className="card-stat-number">{stats.cotizaciones}</div>
                        <div className="card-stat-label">Total Cotizaciones</div>
                    </div>
                </div>

                <div className="card-stat">
                    <div className="card-stat-icon">
                        <FiUsers size={32} />
                    </div>
                    <div>
                        <div className="card-stat-number">{stats.clientes}</div>
                        <div className="card-stat-label">Clientes Activos</div>
                    </div>
                </div>

                <div className="card-stat">
                    <div className="card-stat-icon">
                        <FiPackage size={32} />
                    </div>
                    <div>
                        <div className="card-stat-number">{stats.productos}</div>
                        <div className="card-stat-label">Productos</div>
                    </div>
                </div>

                <div className="card-stat">
                    <div className="card-stat-icon">
                        <FiDollarSign size={32} />
                    </div>
                    <div>
                        <div className="card-stat-number">{formatCurrency(stats.ingresos)}</div>
                        <div className="card-stat-label">Ingresos del Mes</div>
                    </div>
                </div>
            </div>

            {/* Cotizaciones recientes */}
            <div className="card-custom">
                <div className="card-header-custom">
                    <h3>Cotizaciones Recientes</h3>
                    <button
                        className="btn-custom btn-secondary btn-sm"
                        onClick={() => navigate('/cotizaciones')}
                    >
                        Ver todas
                    </button>
                </div>

                {recentQuotations.length === 0 ? (
                    <p className="text-muted">No hay cotizaciones recientes</p>
                ) : (
                    <table className="table-custom">
                        <thead>
                            <tr>
                                <th>Número</th>
                                <th>Cliente</th>
                                <th>Fecha</th>
                                <th>Total</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recentQuotations.map((cotizacion) => (
                                <tr
                                    key={cotizacion.id}
                                >
                                    <td>{cotizacion.numero}</td>
                                    <td>{cotizacion.cliente_info?.nombre || 'N/A'}</td>
                                    <td>{new Date(cotizacion.fecha_creacion).toLocaleDateString('es-CL')}</td>
                                    <td>{formatCurrency(cotizacion.total)}</td>
                                    <td>
                                        <span className={`badge-custom ${getStatusBadge(cotizacion.estado)}`}>
                                            {getStatusLabel(cotizacion.estado)}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div >
    );
};

export default Dashboard;

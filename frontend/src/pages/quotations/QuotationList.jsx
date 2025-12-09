import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiPlus, FiSearch, FiEdit2, FiTrash2, FiFileText, FiDownload, FiCheckSquare, FiSend, FiDollarSign, FiPlayCircle, FiFlag } from 'react-icons/fi';
import quotationsService from '../../services/quotations.service';
import { useAuth } from '../../context/AuthContext';

const QuotationList = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user } = useAuth();

    const [quotations, setQuotations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [actionModal, setActionModal] = useState({ show: false, quotationId: null, quotationNumber: '' });
    const [showBanner, setShowBanner] = useState(true);

    // --- Hooks ---

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        console.log('URL params changed:', location.search);
        if (params.get('pending') === 'true') {
            console.log('Setting filter to BORRADOR from URL param');
            setStatusFilter('BORRADOR');
        } else if (!statusFilter) {
            // Si no hay param y no hay filtro, limpiar o dejar default
        }
        fetchQuotations(); // Force fetch on location change just in case
    }, [location]);

    useEffect(() => {
        console.log('Status filter changed to:', statusFilter);
        fetchQuotations();
    }, [statusFilter]); // eslint-disable-line react-hooks/exhaustive-deps

    // --- Functions ---

    const fetchQuotations = async () => {
        try {
            setLoading(true);
            const params = {};
            if (statusFilter) params.estado = statusFilter;

            console.log('Fetching quotations with params:', params);
            const data = await quotationsService.getAll(params);
            console.log('Quotations fetched:', data.results ? data.results.length : data.length);
            setQuotations(data.results || data);
        } catch (err) {
            console.error('Error fetching quotations:', err);
            setError('Error al cargar cotizaciones');
        } finally {
            setLoading(false);
        }
    };

    const handleDecision = async (id, type) => {
        try {
            setLoading(true);
            if (type === 'ACCEPT') {
                await quotationsService.markAsAccepted(id);
                alert('¡Venta confirmada exitosamente!');
            } else if (type === 'REJECT') {
                // Advertencia sobre detención de mensajes automáticos
                const confirmacion = window.confirm("Si la marcas como rechazada, la generación de mensajería automática se detendrá para esta cotización.\n\n¿Deseas continuar?");

                if (confirmacion) {
                    // Pedir motivo opcional
                    const motivo = window.prompt("Indica el motivo del rechazo (Opcional):");
                    if (motivo !== null) {
                        await quotationsService.reject(id, motivo);
                        alert('Venta marcada como rechazada.');
                    }
                }
            }
            setActionModal({ show: false, quotationId: null, quotationNumber: '' });
            fetchQuotations();
        } catch (err) {
            console.error('Error processing decision:', err);
            alert('Error al procesar la acción.');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('¿Estás seguro de que deseas eliminar esta cotización?')) {
            try {
                await quotationsService.delete(id);
                setQuotations(quotations.filter(q => q.id !== id));
            } catch (err) {
                console.error('Error deleting quotation:', err);
                alert('No se pudo eliminar la cotización.');
            }
        }
    };

    const handleDownloadPdf = async (id, numero) => {
        try {
            const blob = await quotationsService.generatePdf(id);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `cotizacion-${numero}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Error downloading PDF:', err);
            alert('Error al generar el PDF');
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(amount);
    };

    const filteredQuotations = quotations.filter(q =>
        q.cliente_info?.nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        q.numero?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading && quotations.length === 0) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="container-custom">
            <div className="card-header-custom" style={{ marginTop: '20px', borderBottom: 'none' }}>
                <div>
                    <h2>Gestión de Cotizaciones</h2>
                    <p className="text-muted">Crea y administra tus cotizaciones comerciales</p>
                </div>
                <button className="btn-custom btn-primary" onClick={() => navigate('/cotizaciones/nuevo')}>
                    <FiPlus size={20} /> Nueva Cotización
                </button>
            </div>

            {error && <div className="alert-custom alert-danger">{error}</div>}

            <div className="card-custom">
                <div style={{ display: 'flex', gap: '15px', marginBottom: '20px', flexWrap: 'wrap' }}>
                    <div className="header-search" style={{ flex: 1, minWidth: '300px' }}>
                        <FiSearch size={20} />
                        <input
                            type="text"
                            placeholder="Buscar por cliente o número..."
                            className="header-search-input"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <select
                        className="form-control-custom"
                        style={{ width: '200px' }}
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="">Todos los estados</option>
                        <option value="BORRADOR">Borrador</option>
                        <option value="ENVIADA">Enviada</option>
                        <option value="ACEPTADA">Aceptada</option>
                        <option value="RECHAZADA">Rechazada</option>
                    </select>
                </div>

                {/* Banner Sugerencia Mensajería Automática (Solo Admin) */}
                {showBanner && user?.rol === 'ADMIN' && (
                    <div style={{
                        backgroundColor: '#eff6ff',
                        border: '1px solid #bfdbfe',
                        borderRadius: '8px',
                        padding: '15px',
                        marginBottom: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        position: 'relative'
                    }}>
                        <button
                            onClick={() => setShowBanner(false)}
                            style={{
                                position: 'absolute',
                                top: '10px',
                                right: '10px',
                                background: 'none',
                                border: 'none',
                                color: '#93c5fd',
                                cursor: 'pointer',
                                fontSize: '18px',
                                lineHeight: 1
                            }}
                        >
                            &times;
                        </button>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                            <div style={{
                                backgroundColor: '#3b82f6',
                                color: 'white',
                                borderRadius: '50%',
                                width: '40px',
                                height: '40px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '20px'
                            }}>
                                🚀
                            </div>
                            <div>
                                <h4 style={{ margin: 0, color: '#1e40af', fontSize: '16px' }}>¡Aumenta tus ventas con Mensajería Automática!</h4>
                                <p style={{ margin: '5px 0 0 0', color: '#3b82f6', fontSize: '14px' }}>
                                    Activa el seguimiento automático de ofertas y recupera clientes indecisos.
                                </p>
                            </div>
                        </div>
                        <button
                            className="btn-custom"
                            style={{ backgroundColor: 'white', color: '#3b82f6', border: '1px solid #3b82f6', marginRight: '20px' }}
                            onClick={() => navigate('/configuracion')}
                        >
                            Configurar Ahora
                        </button>
                    </div>
                )}

                {filteredQuotations.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                        <FiFileText size={48} color="var(--gray-400)" />
                        <p className="text-muted" style={{ marginTop: '10px' }}>No se encontraron cotizaciones</p>
                    </div>
                ) : (
                    <div className="table-responsive">
                        <table className="table-custom">
                            <thead>
                                <tr>
                                    <th>Número</th>
                                    <th>Cliente</th>
                                    <th>Fecha</th>
                                    <th>Total</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredQuotations.map((quotation) => {
                                    const statusInfo = quotationsService.getStatusInfo(quotation.estado);
                                    return (
                                        <tr key={quotation.id}>
                                            <td><span style={{ fontWeight: 'bold' }}>{quotation.numero}</span></td>
                                            <td>{quotation.cliente_info?.nombre || 'N/A'}</td>
                                            <td>{new Date(quotation.fecha_creacion).toLocaleDateString('es-CL')}</td>
                                            <td style={{ fontWeight: 'bold' }}>{formatCurrency(quotation.total)}</td>
                                            <td>
                                                <span className={`badge-custom ${statusInfo.class}`}>
                                                    {statusInfo.label}
                                                </span>
                                            </td>
                                            <td>
                                                <div style={{ display: 'flex', gap: '8px' }}>
                                                    {/* Botón Revisar/Aprobar (Visible para Empleados o Admin en Borrador) */}
                                                    {quotation.estado === 'BORRADOR' && (
                                                        <button
                                                            className="btn-icon"
                                                            onClick={() => navigate(`/cotizaciones/editar/${quotation.id}?mode=approval`)}
                                                            title="Revisar / Aprobar Envío"
                                                            style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--success-green)' }}
                                                        >
                                                            <FiPlayCircle size={20} style={{ pointerEvents: 'none' }} />
                                                        </button>
                                                    )}

                                                    {/* Botón Solicitar Cambio (Solo Empleados) */}
                                                    {user?.rol === 'EMPLEADO' && quotation.estado === 'BORRADOR' && (
                                                        <button
                                                            className="btn-icon"
                                                            onClick={() => navigate(`/cotizaciones/editar/${quotation.id}?mode=request`)}
                                                            title="Solicitar Cambio al Administrador"
                                                            style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--primary-orange)' }}
                                                        >
                                                            <FiFlag size={18} style={{ pointerEvents: 'none' }} />
                                                        </button>
                                                    )}

                                                    {/* Botón Editar (Solo Admin) */}
                                                    {user?.rol === 'ADMIN' && quotation.estado === 'BORRADOR' && (
                                                        <button
                                                            className="btn-icon"
                                                            onClick={() => navigate(`/cotizaciones/editar/${quotation.id}`)}
                                                            title="Editar"
                                                            style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--primary-orange)' }}
                                                        >
                                                            <FiEdit2 size={18} style={{ pointerEvents: 'none' }} />
                                                        </button>
                                                    )}

                                                    {/* Botón Eliminar (Solo Admin) */}
                                                    {user?.rol === 'ADMIN' && (
                                                        <button
                                                            className="btn-icon"
                                                            onClick={() => handleDelete(quotation.id)}
                                                            title="Eliminar"
                                                            style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--danger-red)' }}
                                                        >
                                                            <FiTrash2 size={18} style={{ pointerEvents: 'none' }} />
                                                        </button>
                                                    )}

                                                    <button
                                                        className="btn-icon"
                                                        onClick={() => handleDownloadPdf(quotation.id, quotation.numero)}
                                                        title="Descargar PDF"
                                                        style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--blue-600)' }}
                                                    >
                                                        <FiDownload size={18} style={{ pointerEvents: 'none' }} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Modal de Decisión de Venta */}
            {
                actionModal.show && (
                    <div style={{
                        position: 'fixed',
                        top: 0, left: 0, right: 0, bottom: 0,
                        backgroundColor: 'rgba(0,0,0,0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000
                    }}>
                        <div className="card-custom" style={{ width: '400px', padding: '30px', textAlign: 'center', position: 'relative' }}>
                            <button
                                onClick={() => setActionModal({ show: false, quotationId: null })}
                                style={{ position: 'absolute', top: '15px', right: '15px', border: 'none', background: 'none', cursor: 'pointer' }}
                            >
                                <FiPlus style={{ transform: 'rotate(45deg)' }} size={24} />
                            </button>

                            <h3 style={{ marginBottom: '20px' }}>Gestionar Venta #{actionModal.quotationNumber}</h3>
                            <p className="text-muted" style={{ marginBottom: '30px' }}>
                                ¿Cuál es el resultado de esta cotización enviada?
                            </p>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                                <button
                                    className="btn-custom"
                                    style={{ backgroundColor: '#10b981', color: 'white', justifyContent: 'center' }}
                                    onClick={() => handleDecision(actionModal.quotationId, 'ACCEPT')}
                                >
                                    <FiCheckSquare style={{ marginRight: '8px' }} /> CONFIRMAR VENTA
                                </button>

                                <button
                                    className="btn-custom"
                                    style={{ backgroundColor: '#ef4444', color: 'white', justifyContent: 'center' }}
                                    onClick={() => handleDecision(actionModal.quotationId, 'REJECT')}
                                >
                                    <FiTrash2 style={{ marginRight: '8px' }} /> RECHAZAR VENTA
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
        </div >
    );
};

export default QuotationList;

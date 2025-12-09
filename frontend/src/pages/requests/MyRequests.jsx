import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiTrash2, FiClock, FiCheckCircle, FiXCircle, FiFileText, FiBox } from 'react-icons/fi';
import Swal from 'sweetalert2';
import requestsService from '../../services/requests.service';
import { useAuth } from '../../context/AuthContext';

const MyRequests = () => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { user } = useAuth();

    useEffect(() => {
        loadRequests();
    }, []);

    const loadRequests = async () => {
        try {
            setLoading(true);
            const data = await requestsService.getAll();
            // Backend filters by user automatically
            const reqs = Array.isArray(data) ? data : (data.results || []);
            setRequests(reqs);
        } catch (err) {
            console.error(err);
            setError('Error al cargar sus solicitudes.');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        const result = await Swal.fire({
            title: '¿Eliminar notificación?',
            text: "Esta acción solo eliminará el registro de la solicitud de tu lista.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: 'var(--danger-red)',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        });

        if (result.isConfirmed) {
            try {
                await requestsService.delete(id);
                setRequests(requests.filter(r => r.id !== id));
                Swal.fire('Eliminado', 'La solicitud ha sido eliminada de tu lista.', 'success');
            } catch (err) {
                console.error(err);
                Swal.fire('Error', 'No se pudo eliminar la solicitud.', 'error');
            }
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'PENDIENTE':
                return <span className="badge-custom badge-warning"><FiClock /> Pendiente</span>;
            case 'APROBADA':
                return <span className="badge-custom badge-success"><FiCheckCircle /> Aprobada</span>;
            case 'RECHAZADA':
                return <span className="badge-custom badge-danger"><FiXCircle /> Rechazada</span>;
            default:
                return <span className="badge-custom badge-secondary">{status}</span>;
        }
    };

    const getTypeIcon = (type) => {
        return type === 'PRODUCTO' ? <FiBox /> : <FiFileText />;
    };

    return (
        <div className="container-custom">
            <h1 style={{ marginBottom: '20px' }}>Mis Solicitudes de Cambio</h1>

            {error && <div className="alert-custom alert-danger">{error}</div>}

            <div className="card-custom">
                {loading ? (
                    <div className="loading-overlay"><div className="spinner"></div></div>
                ) : requests.length === 0 ? (
                    <div className="empty-state">
                        <p className="text-muted">No tienes solicitudes pendientes ni recientes.</p>
                    </div>
                ) : (
                    <div className="table-responsive">
                        <table className="table-custom">
                            <thead>
                                <tr>
                                    <th>Tipo</th>
                                    <th>Entidad</th>
                                    <th>Fecha Solicitud</th>
                                    <th>Estado</th>
                                    <th>Resolución / Comentario</th>
                                    <th style={{ width: '100px' }}>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {requests.map((request) => (
                                    <tr key={request.id}>
                                        <td style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            {getTypeIcon(request.tipo_entidad)}
                                            {request.tipo_entidad}
                                        </td>
                                        <td>
                                            {request.entidad_nombre || `#${request.entidad_id}`}
                                        </td>
                                        <td>
                                            {new Date(request.fecha_solicitud).toLocaleDateString()}
                                        </td>
                                        <td>
                                            {getStatusBadge(request.estado)}
                                        </td>
                                        <td>
                                            {request.estado !== 'PENDIENTE' ? (
                                                <div style={{ fontSize: '0.9rem' }}>
                                                    {request.estado === 'RECHAZADA' && (
                                                        <span className="text-danger">
                                                            <strong>Motivo:</strong> {request.comentario_resolucion || 'Sin motivo especificado'}
                                                        </span>
                                                    )}
                                                    {request.estado === 'APROBADA' && (
                                                        <span className="text-success">
                                                            Los cambios han sido aplicados.
                                                        </span>
                                                    )}
                                                </div>
                                            ) : (
                                                <span className="text-muted">-</span>
                                            )}
                                        </td>
                                        <td>
                                            {request.estado !== 'PENDIENTE' && (
                                                <button
                                                    onClick={() => handleDelete(request.id)}
                                                    title="Eliminar de mi lista"
                                                    style={{
                                                        border: 'none',
                                                        background: 'transparent',
                                                        cursor: 'pointer',
                                                        padding: '5px',
                                                        color: 'var(--danger-red)',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center'
                                                    }}
                                                >
                                                    <FiTrash2 size={18} />
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MyRequests;

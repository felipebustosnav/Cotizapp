import React, { useState, useEffect } from 'react';
import { FiCheck, FiX, FiEye, FiClock, FiUser, FiBox, FiFileText } from 'react-icons/fi';
import requestsService from '../../services/requests.service';
import Swal from 'sweetalert2';

import { useNavigate } from 'react-router-dom';

const RequestsPanel = () => {
    const navigate = useNavigate();
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedRequest, setSelectedRequest] = useState(null);

    useEffect(() => {
        loadRequests();
    }, []);

    const loadRequests = async () => {
        try {
            setLoading(true);
            const data = await requestsService.getAll();
            // Filtrar solo pendientes o mostrar todas con filtro?
            // El usuario pide "panel de Solicitudes el cual tendrá un badge e indicará cuantas solicitudes tiene por aprobar"
            // Asumo tabla principal PENDIENTES.
            const results = Array.isArray(data) ? data : (data.results || []);
            setRequests(results);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (req) => {
        const result = await Swal.fire({
            title: '¿Aprobar solicitud?',
            text: `Se aplicarán los cambios a ${req.tipo_entidad} #${req.entidad_id}`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: 'var(--success-green)',
            confirmButtonText: 'Sí, aprobar'
        });

        if (result.isConfirmed) {
            try {
                await requestsService.approve(req.id);
                Swal.fire('Aprobado', 'Los cambios se han aplicado exitosamente.', 'success');
                loadRequests();
                setSelectedRequest(null);
            } catch (error) {
                Swal.fire('Error', 'No se pudo aprobar la solicitud.', 'error');
            }
        }
    };

    const handleReject = async (req) => {
        const { value: motivo } = await Swal.fire({
            title: 'Rechazar Solicitud',
            input: 'textarea',
            inputLabel: 'Motivo del rechazo',
            inputPlaceholder: 'Ingresa el motivo...',
            showCancelButton: true,
            confirmButtonColor: 'var(--danger-red)'
        });

        if (motivo) {
            try {
                await requestsService.reject(req.id, motivo);
                Swal.fire('Rechazado', 'La solicitud ha sido rechazada.', 'success');
                loadRequests();
                setSelectedRequest(null);
            } catch (error) {
                Swal.fire('Error', 'No se pudo rechazar la solicitud.', 'error');
            }
        }
    };

    const pendingRequests = requests.filter(r => r.estado === 'PENDIENTE');

    return (
        <div className="container-custom">
            <h1 style={{ marginBottom: '20px', color: 'var(--text-dark)' }}>Solicitudes de Cambio</h1>

            <div className="card-custom">
                {loading ? (
                    <div style={{ padding: '20px', textAlign: 'center' }}>Cargando...</div>
                ) : (
                    <div className="table-responsive">
                        <table className="table-custom">
                            <thead>
                                <tr>
                                    <th>Empleado</th>
                                    <th>Fecha</th>
                                    <th>Área</th>
                                    <th>Estado</th>
                                    <th style={{ textAlign: 'right' }}>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pendingRequests.length === 0 ? (
                                    <tr><td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>No hay solicitudes pendientes.</td></tr>
                                ) : (
                                    pendingRequests.map(req => (
                                        <tr key={req.id}>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <FiUser />
                                                    <span>{req.solicitante_info?.first_name} {req.solicitante_info?.last_name}</span>
                                                </div>
                                            </td>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <FiClock />
                                                    {new Date(req.fecha_solicitud).toLocaleString('es-CL')}
                                                </div>
                                            </td>
                                            <td>
                                                <span className={`badge-custom ${req.tipo_entidad === 'PRODUCTO' ? 'badge-primary' : 'badge-warning'}`}>
                                                    {req.tipo_entidad === 'PRODUCTO' ? <FiBox /> : <FiFileText />} {req.tipo_entidad}
                                                </span>
                                            </td>
                                            <td>
                                                <span className="badge-custom badge-secondary">PENDIENTE</span>
                                            </td>
                                            <td style={{ textAlign: 'right' }}>
                                                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '5px' }}>
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            const route = req.tipo_entidad === 'PRODUCTO'
                                                                ? `/productos/editar/${req.entidad_id}`
                                                                : `/cotizaciones/editar/${req.entidad_id}`;
                                                            navigate(`${route}?requestId=${req.id}`);
                                                        }}
                                                        title="Revisar"
                                                        style={{ border: 'none', background: 'transparent', cursor: 'pointer', padding: '5px', color: 'var(--primary-orange)' }}
                                                    >
                                                        <FiEye size={20} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Modal Detalle */}
            {selectedRequest && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }}>
                    <div className="card-custom" style={{ width: '90%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                            <h3>Detalle Solicitud #{selectedRequest.id}</h3>
                            <button onClick={() => setSelectedRequest(null)} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer' }}><FiX /></button>
                        </div>

                        <div style={{ marginBottom: '20px' }}>
                            <p><strong>Empleado:</strong> {selectedRequest.solicitante_info?.first_name} {selectedRequest.solicitante_info?.last_name}</p>
                            <p><strong>Entidad:</strong> {selectedRequest.tipo_entidad} #{selectedRequest.entidad_id}</p>
                            <p><strong>Datos Propuestos:</strong></p>
                            <pre style={{
                                backgroundColor: '#f8f9fa',
                                padding: '10px',
                                borderRadius: '5px',
                                overflowX: 'auto',
                                fontSize: '12px'
                            }}>
                                {JSON.stringify(selectedRequest.datos_propuestos, null, 2)}
                            </pre>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                            <button className="btn-custom btn-secondary" onClick={() => setSelectedRequest(null)}>Cerrar</button>
                            <button className="btn-custom btn-danger" onClick={() => handleReject(selectedRequest)}>Rechazar</button>
                            <button className="btn-custom btn-primary" onClick={() => handleApprove(selectedRequest)}>Aprobar</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RequestsPanel;

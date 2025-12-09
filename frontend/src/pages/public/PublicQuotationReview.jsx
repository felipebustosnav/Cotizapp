import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { FiCheck, FiX, FiDownload, FiInfo, FiAlertCircle } from 'react-icons/fi';
import publicService from '../../services/public.service';
import quotationsService from '../../services/quotations.service';

const PublicQuotationReview = () => {
    const { uuid } = useParams();
    const [quotation, setQuotation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        loadQuotation();
    }, [uuid]);

    const loadQuotation = async () => {
        try {
            setLoading(true);
            const data = await publicService.getQuotationByUuid(uuid);
            setQuotation(data);
        } catch (err) {
            console.error('Error loading quotation:', err);
            setError('No pudimos encontrar la cotización o el enlace ha expirado.');
        } finally {
            setLoading(false);
        }
    };

    const handleAccept = async () => {
        if (!window.confirm('¿Estás seguro de que deseas aceptar esta cotización?')) return;

        try {
            setActionLoading(true);
            await publicService.acceptQuotation(uuid);
            setSuccessMessage('¡Cotización aceptada exitosamente! Nos pondremos en contacto contigo.');
            loadQuotation(); // Recargar estado
        } catch (err) {
            console.error('Error accepting:', err);
            alert('Error al aceptar la cotización. Intenta nuevamente.');
        } finally {
            setActionLoading(false);
        }
    };

    const handleReject = async () => {
        if (!window.confirm('¿Estás seguro de que deseas rechazar esta cotización?')) return;

        // Pedir motivo opcional
        const motivo = window.prompt("Indica el motivo del rechazo (Opcional):");

        try {
            setActionLoading(true);
            // Enviar motivo en el body
            await publicService.rejectQuotation(uuid, motivo);
            setSuccessMessage('Has rechazado la cotización.');
            loadQuotation(); // Recargar estado
        } catch (err) {
            console.error('Error rejecting:', err);
            alert('Error al rechazar la cotización. Intenta nuevamente.');
        } finally {
            setActionLoading(false);
        }
    };

    const handleDownload = async () => {
        try {
            const downloadUrl = `http://localhost:8000/api/cotizaciones/download_public/?uuid=${uuid}`;

            // Crear un elemento <a> temporal para forzar la descarga
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.setAttribute('download', `Cotizacion_${quotation.numero}.pdf`); // Sugerir nombre
            link.setAttribute('target', '_blank'); // Abrir en nueva pestaña por si acaso falla la descarga directa
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

        } catch (err) {
            console.error('Download error:', err);
            alert('Error al iniciar la descarga.');
        }
    };

    const formatCurrency = (val) => {
        return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(val);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('es-CL');
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    if (error) {
        return (
            <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--background-cream)' }}>
                <div className="card-custom" style={{ textAlign: 'center', padding: '40px', maxWidth: '500px' }}>
                    <FiAlertCircle size={48} color="var(--danger-red)" />
                    <h3 style={{ marginTop: '20px' }}>Enlace Inválido</h3>
                    <p className="text-muted">{error}</p>
                </div>
            </div>
        );
    }

    if (!quotation) return null;

    const isFinished = ['ACEPTADA', 'RECHAZADA'].includes(quotation.estado);
    const empresa = quotation.empresa_data || {}; // Asumiendo que el serializer trae datos de empresa anidados o planos

    // Si el serializer usa 'empresa' como ID, necesitamos los datos expandidos. 
    // CotizacionSerializer usa EmpresaSerializer para el campo 'empresa' normalmente.
    // Verificamos: class CotizacionSerializer... empresa = EmpresaSerializer(read_only=True)
    // Así que quotation.empresa debería ser un objeto.

    return (
        <div style={{ minHeight: '100vh', backgroundColor: 'var(--background-cream)', padding: '20px 0' }}>
            <div className="container-custom" style={{ maxWidth: '900px' }}>

                {/* Header Empresa */}
                <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                    {/* Logo handling simple */}
                    <h1 style={{ color: 'var(--primary-orange)', fontWeight: 'bold' }}>Cotización #{quotation.numero}</h1>
                    <p className="text-muted">Fecha: {formatDate(quotation.fecha_creacion)}</p>
                </div>

                {successMessage && (
                    <div style={{
                        backgroundColor: quotation.estado === 'ACEPTADA' ? '#d1fae5' : '#fee2e2',
                        color: quotation.estado === 'ACEPTADA' ? '#065f46' : '#991b1b',
                        padding: '20px',
                        borderRadius: '8px',
                        marginBottom: '30px',
                        textAlign: 'center',
                        border: `1px solid ${quotation.estado === 'ACEPTADA' ? '#34d399' : '#f87171'}`
                    }}>
                        <h3>{successMessage}</h3>
                    </div>
                )}

                {!successMessage && (
                    <>
                        {/* Mostrar estado Finalizado solo si NO hay oferta activa para salvarla */}
                        {isFinished && !quotation.oferta_activa && (
                            <div style={{
                                backgroundColor: '#f3f4f6',
                                padding: '20px',
                                borderRadius: '8px',
                                marginBottom: '30px',
                                textAlign: 'center',
                                color: '#4b5563'
                            }}>
                                <h3>Esta cotización ya ha sido {quotation.estado.toLowerCase()}.</h3>
                            </div>
                        )}

                        {/* Detalles de Cotización (Tabla) */}
                        <div className="card-custom">

                            {quotation.oferta_activa && (
                                <div style={{
                                    backgroundColor: '#fff7ed',
                                    border: '1px solid #fdba74',
                                    borderRadius: '8px',
                                    padding: '15px',
                                    marginBottom: '20px',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    flexWrap: 'wrap',
                                    gap: '10px'
                                }}>
                                    <div>
                                        <h4 style={{ margin: 0, color: '#c2410c', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <FiCheck /> ¡Oferta Disponible!
                                        </h4>
                                        <p style={{ margin: '5px 0 0 0', color: '#9a3412', fontSize: '14px' }}>
                                            Acepta ahora y obtén un <strong>{quotation.oferta_activa.descuento_porcentaje}% de descuento</strong>.
                                        </p>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <span style={{ fontSize: '12px', color: '#9a3412', display: 'block' }}>Válida hasta:</span>
                                        <strong>{new Date(quotation.oferta_activa.fecha_vencimiento).toLocaleString()}</strong>
                                    </div>
                                </div>
                            )}

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--gray-200)', paddingBottom: '15px', marginBottom: '20px' }}>
                                <h3 onClick={() => console.log('Quotation Data:', quotation)}>Detalle de Productos</h3>
                                <button
                                    className="btn-custom btn-secondary btn-sm"
                                    onClick={handleDownload}
                                >
                                    <FiDownload /> Descargar PDF
                                </button>
                            </div>

                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ background: '#f9fafb', color: '#6b7280', fontSize: '13px', textAlign: 'left' }}>
                                        <th style={{ padding: '10px' }}>Producto</th>
                                        <th style={{ padding: '10px', textAlign: 'center' }}>Cant.</th>
                                        <th style={{ padding: '10px', textAlign: 'right' }}>Precio Unit.</th>
                                        <th style={{ padding: '10px', textAlign: 'right' }}>Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {quotation.detalles && quotation.detalles.map((detalle, index) => (
                                        <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                                            <td style={{ padding: '12px 10px' }}>
                                                <div style={{ fontWeight: '500' }}>{detalle.producto_nombre || detalle.producto}</div>
                                            </td>
                                            <td style={{ padding: '12px 10px', textAlign: 'center' }}>{detalle.cantidad}</td>
                                            <td style={{ padding: '12px 10px', textAlign: 'right' }}>{formatCurrency(detalle.precio_unitario)}</td>
                                            <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '500' }}>{formatCurrency(detalle.total)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colSpan="3" style={{ padding: '15px 10px', textAlign: 'right', fontWeight: 'bold' }}>Subtotal:</td>
                                        <td style={{ padding: '15px 10px', textAlign: 'right' }}>{formatCurrency(quotation.subtotal)}</td>
                                    </tr>
                                    <tr>
                                        <td colSpan="3" style={{ padding: '5px 10px', textAlign: 'right', fontWeight: 'bold' }}>Impuestos:</td>
                                        <td style={{ padding: '5px 10px', textAlign: 'right' }}>{formatCurrency(quotation.impuesto)}</td>
                                    </tr>
                                    {quotation.oferta_activa ? (
                                        <>
                                            <tr>
                                                <td colSpan="3" style={{ padding: '5px 10px', textAlign: 'right', fontWeight: 'bold', color: '#9ca3af', textDecoration: 'line-through' }}>
                                                    Total Original:
                                                </td>
                                                <td style={{ padding: '5px 10px', textAlign: 'right', color: '#9ca3af', textDecoration: 'line-through' }}>
                                                    {formatCurrency(quotation.total)}
                                                </td>
                                            </tr>
                                            <tr style={{ backgroundColor: '#fff7ed' }}>
                                                <td colSpan="3" style={{ padding: '10px 10px', textAlign: 'right', fontWeight: 'bold', color: '#f97316' }}>
                                                    Descuento Especial ({quotation.oferta_activa.descuento_porcentaje}%):
                                                </td>
                                                <td style={{ padding: '10px 10px', textAlign: 'right', fontWeight: 'bold', color: '#f97316' }}>
                                                    - {formatCurrency(quotation.total - quotation.oferta_activa.nuevo_total)}
                                                </td>
                                            </tr>
                                            <tr style={{ fontSize: '20px', borderTop: '2px solid #f97316' }}>
                                                <td colSpan="3" style={{ padding: '15px 10px', textAlign: 'right', fontWeight: 'bold', color: '#f97316' }}>
                                                    Total Oferta:
                                                </td>
                                                <td style={{ padding: '15px 10px', textAlign: 'right', fontWeight: 'bold', color: '#f97316' }}>
                                                    {formatCurrency(quotation.oferta_activa.nuevo_total)}
                                                </td>
                                            </tr>
                                        </>
                                    ) : (
                                        <tr style={{ fontSize: '18px' }}>
                                            <td colSpan="3" style={{ padding: '15px 10px', textAlign: 'right', fontWeight: 'bold', color: 'var(--primary-orange)' }}>Total:</td>
                                            <td style={{ padding: '15px 10px', textAlign: 'right', fontWeight: 'bold', color: 'var(--primary-orange)' }}>{formatCurrency(quotation.total)}</td>
                                        </tr>
                                    )}
                                </tfoot>
                            </table>
                        </div>

                        {/* Mostrar Botones si NO está finalizada O si TIENE oferta activa (para salvarla) */}
                        {(!isFinished || quotation.oferta_activa) && (
                            <div className="card-custom" style={{ marginTop: '20px', textAlign: 'center' }}>
                                <h3 style={{ marginBottom: '20px' }}>
                                    {quotation.oferta_activa ? '¡Oferta Especial Disponible!' : '¿Qué deseas hacer?'}
                                </h3>
                                <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
                                    {/* Botón rechazar (solo si no estaba rechazada ya, o para rechazar la nueva oferta) */}
                                    <button
                                        className="btn-custom"
                                        style={{ backgroundColor: '#ef4444', color: 'white', flex: 1, maxWidth: '200px' }}
                                        onClick={handleReject}
                                        disabled={actionLoading}
                                    >
                                        <FiX /> {quotation.estado === 'RECHAZADA' ? 'Rechazar Oferta' : 'Rechazar'}
                                    </button>
                                    <button
                                        className="btn-custom"
                                        style={{ backgroundColor: '#10b981', color: 'white', flex: 1, maxWidth: '200px' }}
                                        onClick={handleAccept}
                                        disabled={actionLoading}
                                    >
                                        <FiCheck /> {quotation.oferta_activa ? 'Aceptar Oferta' : 'Aceptar Cotización'}
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}

                {/* Footer simple */}
                <div style={{
                    textAlign: 'center',
                    marginTop: '40px',
                    color: 'var(--gray-400)',
                    fontSize: '14px'
                }}>
                    <p>Powered by 🧾 CotizApp</p>
                </div>

            </div>
        </div>
    );
};

export default PublicQuotationReview;

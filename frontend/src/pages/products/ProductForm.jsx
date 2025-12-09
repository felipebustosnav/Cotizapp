
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { FiSave, FiArrowLeft, FiCheck, FiX } from 'react-icons/fi';
import productsService from '../../services/products.service';
import requestsService from '../../services/requests.service';
import taxesService from '../../services/taxes.service';
import TaxSelector from '../../components/TaxSelector';
import TaxQuickCreate from '../../components/TaxQuickCreate';
import Swal from 'sweetalert2';

const ProductForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const mode = queryParams.get('mode');
    const requestId = queryParams.get('requestId');

    const isRequestMode = mode === 'request';
    const isReviewMode = !!requestId;
    const isEditing = !!id;

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [selectedTaxes, setSelectedTaxes] = useState([]);
    const [showTaxModal, setShowTaxModal] = useState(false);

    // For Review Mode
    const [changedFields, setChangedFields] = useState(new Set());
    const [currentProduct, setCurrentProduct] = useState(null);
    const [requestData, setRequestData] = useState(null);

    const { register, handleSubmit, formState: { errors }, reset, watch } = useForm({
        defaultValues: {
            nombre: '',
            descripcion: '',
            sku: '',
            marca: '',
            tipo: 'PRODUCTO',
            precio: '',
            activo: true
        }
    });

    const precio = watch('precio');
    const impuestoTotal = selectedTaxes.reduce((sum, tax) => sum + parseFloat(tax.porcentaje || 0), 0);
    const precioFinal = precio ? parseFloat(precio) * (1 + impuestoTotal / 100) : 0;

    useEffect(() => {
        if (isReviewMode) {
            loadReviewData();
        } else if (isEditing) {
            loadProduct();
        }
    }, [id, isEditing, isReviewMode, requestId]);

    const loadReviewData = async () => {
        try {
            setLoading(true);
            const [reqData, prodData] = await Promise.all([
                requestsService.getById(requestId),
                productsService.getById(id)
            ]);

            setRequestData(reqData);
            setCurrentProduct(prodData);

            // Populate form with PROPOSED data
            const proposed = reqData.datos_propuestos;
            reset(proposed);

            // Determine changed fields
            const changes = new Set();
            Object.keys(proposed).forEach(key => {
                // Simple comparison (loose equality for numbers/strings)
                if (proposed[key] != prodData[key]) {
                    // Ignore unnecessary type mismatches if content is same
                    if (String(proposed[key]) !== String(prodData[key])) {
                        changes.add(key);
                    }
                }
            });

            // Handle Taxes special case (ID Array vs Object Array)
            // If we wanted to compare taxes, we'd need more logic. 
            // For now, loading taxes from PRODUCT (Current) to show baseline, 
            // or we request Tax Objects if we want to show Proposed Taxes.
            // Simplified: If proposed keys include impuestos, we assume change.
            // Handle Taxes: If proposed data has impuestos_ids, load them
            if (proposed.impuestos_ids && Array.isArray(proposed.impuestos_ids)) {
                try {
                    // Fetch all active taxes to map IDs to Objects
                    const allTaxes = await taxesService.getAll(); // Or getActive()
                    const taxesList = Array.isArray(allTaxes) ? allTaxes : (allTaxes.results || []);

                    const proposedTaxes = taxesList.filter(t => proposed.impuestos_ids.includes(t.id));
                    setSelectedTaxes(proposedTaxes);
                } catch (taxErr) {
                    console.error("Error matching proposed taxes:", taxErr);
                    // Fallback to current if matching fails
                    setSelectedTaxes(prodData.impuestos || []);
                }
            } else if (prodData.impuestos) {
                // If no changes propopsed to taxes, show current
                setSelectedTaxes(prodData.impuestos);
            }

            setChangedFields(changes);

        } catch (err) {
            console.error(err);
            setError('Error cargando datos de revisión.');
        } finally {
            setLoading(false);
        }
    };

    const loadProduct = async () => {
        try {
            setLoading(true);
            const product = await productsService.getById(id);
            reset(product);
            if (product.impuestos && product.impuestos.length > 0) {
                setSelectedTaxes(product.impuestos);
            }
        } catch (err) {
            console.error('Error loading product:', err);
            setError('Error al cargar los datos del producto');
        } finally {
            setLoading(false);
        }
    };

    const onSubmit = async (data) => {
        if (isReviewMode) return; // Review mode uses specific buttons

        setLoading(true);
        setError('');
        try {
            const productData = {
                ...data,
                impuestos_ids: selectedTaxes.map(tax => tax.id)
            };

            if (isRequestMode) {
                await requestsService.create({
                    tipo_entidad: 'PRODUCTO',
                    entidad_id: id,
                    datos_propuestos: productData
                });
                alert('Solicitud de cambio enviada correctamente.');
            } else if (isEditing) {
                await productsService.update(id, productData);
            } else {
                await productsService.create(productData);
            }
            navigate('/productos');
        } catch (err) {
            console.error('Error saving:', err);
            setError('Error al guardar. Verifique los datos.');
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async () => {
        try {
            const result = await Swal.fire({
                title: '¿Aprobar cambios?',
                text: "Se actualizará el producto con los datos propuestos.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: 'var(--success-green)',
                confirmButtonText: 'Sí, aprobar'
            });

            if (result.isConfirmed) {
                setLoading(true);
                await requestsService.approve(requestId);
                Swal.fire('Aprobado', 'Cambios aplicados exitosamente.', 'success');
                navigate('/solicitudes');
            }
        } catch (error) {
            Swal.fire('Error', 'No se pudo aprobar la solicitud.', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleReject = async () => {
        const { value: motivo } = await Swal.fire({
            title: 'Rechazar Solicitud',
            input: 'textarea',
            inputLabel: 'Motivo del rechazo',
            showCancelButton: true,
            confirmButtonColor: 'var(--danger-red)'
        });

        if (motivo) {
            try {
                setLoading(true);
                await requestsService.reject(requestId, motivo);
                Swal.fire('Rechazado', 'Solicitud rechazada.', 'success');
                navigate('/solicitudes');
            } catch (error) {
                Swal.fire('Error', 'No se pudo rechazar.', 'error');
            } finally {
                setLoading(false);
            }
        }
    };

    const handleTaxCreated = (newTax) => {
        setSelectedTaxes([...selectedTaxes, newTax]);
        if (window.refreshTaxSelector) window.refreshTaxSelector();
    };

    // Helper for input styles (Highlighted logic removed per user request)
    const getInputStyle = (fieldName) => ({});

    if (loading && isEditing && !watch('nombre') && !isReviewMode) {
        return <div className="loading-overlay"><div className="spinner"></div></div>;
    }

    return (
        <div className="container-custom">
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '25px' }}>
                <button
                    onClick={() => navigate(isReviewMode ? '/solicitudes' : '/productos')}
                    className="btn-back-custom"
                    style={{
                        background: 'white',
                        border: '1px solid var(--gray-300)',
                        borderRadius: '50%',
                        width: '40px',
                        height: '40px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginRight: '15px',
                        cursor: 'pointer',
                        boxShadow: '0 2px 5px rgba(0,0,0,0.05)',
                        transition: 'all 0.2s ease',
                        color: 'var(--text-dark)'
                    }}
                    onMouseOver={(e) => { e.currentTarget.style.transform = 'translateX(-3px)'; e.currentTarget.style.borderColor = 'var(--primary-orange)'; }}
                    onMouseOut={(e) => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.borderColor = 'var(--gray-300)'; }}
                    title="Volver"
                >
                    <FiArrowLeft size={20} />
                </button>
                <h1 style={{ margin: 0, fontSize: '1.8rem' }}>
                    {isReviewMode ? `Revisar Solicitud #${requestId}` :
                        (isRequestMode ? 'Solicitar Cambio en Producto' : (isEditing ? 'Editar Producto' : 'Nuevo Producto'))}
                </h1>
            </div>

            {error && <div className="alert-custom alert-danger">{error}</div>}

            {isReviewMode && (
                <div className="alert-custom alert-warning" style={{ marginBottom: '20px' }}>
                    <FiCheck /> Revisando cambios propuestos por {requestData?.solicitante_info?.first_name}.
                </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="card-custom">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>

                    {/* Columna Izquierda */}
                    <div>
                        <div className="form-group-custom">
                            <label className="form-label-custom">Nombre</label>
                            <input
                                {...register('nombre', { required: 'El nombre es obligatorio' })}
                                className="form-control-custom"
                                style={getInputStyle('nombre')}
                                readOnly={isReviewMode}
                            />
                            {errors.nombre && <span className="error-text">{errors.nombre.message}</span>}
                        </div>

                        <div className="form-group-custom">
                            <label className="form-label-custom">Marca</label>
                            <input
                                {...register('marca')}
                                className="form-control-custom"
                                style={getInputStyle('marca')}
                                readOnly={isReviewMode}
                            />
                        </div>

                        <div className="form-group-custom">
                            <label className="form-label-custom">SKU</label>
                            <input
                                {...register('sku')}
                                className="form-control-custom"
                                style={getInputStyle('sku')}
                                readOnly={isReviewMode}
                            />
                        </div>

                        <div className="form-group-custom">
                            <label className="form-label-custom">Tipo *</label>
                            <select {...register('tipo')} className="form-control-custom" disabled={isReviewMode}>
                                <option value="PRODUCTO">Producto Físico</option>
                                <option value="SERVICIO">Servicio</option>
                            </select>
                        </div>
                    </div>

                    {/* Columna Derecha */}
                    <div>
                        <div className="form-group-custom">
                            <label className="form-label-custom">Precio Neto</label>
                            <div className="input-group" style={{ display: 'flex', alignItems: 'center' }}>
                                <span className="input-group-text" style={{ height: '100%', display: 'flex', alignItems: 'center', padding: '0 10px', background: '#f3f4f6', border: '1px solid #d1d5db', borderRight: 'none', borderRadius: '4px 0 0 4px' }}>$</span>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('precio', { required: 'El precio es obligatorio', min: 0 })}
                                    className="form-control-custom"
                                    style={{ ...getInputStyle('precio'), borderRadius: '0 4px 4px 0', flex: 1 }}
                                    readOnly={isReviewMode}
                                />
                            </div>
                            {errors.precio && <span className="error-text">{errors.precio.message}</span>}
                        </div>



                        <div className="form-group-custom">
                            <TaxSelector
                                selectedTaxes={selectedTaxes}
                                onChange={setSelectedTaxes}
                                onQuickCreate={() => setShowTaxModal(true)}
                                readOnly={isReviewMode}
                            />
                            {precioFinal > 0 && (
                                <span style={{ fontSize: '12px', color: 'var(--gray-600)', display: 'block', marginTop: '5px' }}>
                                    Precio Final aprox: ${precioFinal.toLocaleString('es-CL')}
                                    (Impuesto total: {impuestoTotal.toFixed(2)}%)
                                </span>
                            )}
                        </div>

                        <div className="form-group-custom">
                            <label className="form-label-custom">
                                <input
                                    type="checkbox"
                                    {...register('activo')}
                                    style={{ marginRight: '10px', transform: 'scale(1.2)', ...getInputStyle('activo') }}
                                    disabled={isReviewMode}
                                />
                                Producto Activo (Visible en cotizaciones)
                            </label>
                        </div>
                    </div>
                </div>

                <div className="form-group-custom" style={{ marginTop: '10px' }}>
                    <label className="form-label-custom">Descripción</label>
                    <textarea
                        {...register('descripcion')}
                        className="form-control-custom"
                        rows="4"
                        style={getInputStyle('descripcion')}
                        readOnly={isReviewMode}
                    />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '15px', marginTop: '20px' }}>
                    <button type="button" className="btn-custom btn-secondary" onClick={() => navigate(isReviewMode ? '/solicitudes' : '/productos')}>
                        Cancelar
                    </button>

                    {isReviewMode ? (
                        <>
                            <button type="button" className="btn-custom btn-danger" onClick={handleReject} disabled={loading}>
                                <FiX size={20} /> Rechazar
                            </button>
                            <button type="button" className="btn-custom btn-success" onClick={handleApprove} disabled={loading} style={{ backgroundColor: 'var(--success-green)', color: 'white' }}>
                                <FiCheck size={20} /> Aprobar Cambios
                            </button>
                        </>
                    ) : (
                        <button type="submit" className="btn-custom btn-primary" disabled={loading}>
                            <FiSave size={20} />
                            {loading
                                ? 'Procesando...'
                                : (isRequestMode ? 'Enviar Solicitud' : (isEditing ? 'Guardar Cambios' : 'Guardar Producto'))}
                        </button>
                    )}
                </div>
            </form>

            <TaxQuickCreate
                isOpen={showTaxModal}
                onClose={() => setShowTaxModal(false)}
                onTaxCreated={handleTaxCreated}
            />
        </div>
    );
};

export default ProductForm;

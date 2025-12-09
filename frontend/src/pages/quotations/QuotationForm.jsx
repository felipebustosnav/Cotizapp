import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { FiSave, FiArrowLeft, FiPlus, FiTrash2, FiCheck, FiX, FiInfo } from 'react-icons/fi';
import Select from 'react-select'; // Importar React Select
import Swal from 'sweetalert2';
import quotationsService from '../../services/quotations.service';
import requestsService from '../../services/requests.service';
import clientsService from '../../services/clients.service';
import productsService from '../../services/products.service';

import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

const QuotationForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const { user, isAdmin } = useAuth();
    const { triggerRefresh } = useNotifications();
    const isEditing = !!id;

    // Check if we are in approval mode
    const queryParams = new URLSearchParams(location.search);
    const isApprovalMode = queryParams.get('mode') === 'approval';
    const isRequestMode = queryParams.get('mode') === 'request';
    const requestId = queryParams.get('requestId');
    const isReviewMode = !!requestId;

    const [loading, setLoading] = useState(false);
    const [clients, setClients] = useState([]);
    const [products, setProducts] = useState([]);
    const [error, setError] = useState('');
    const [isReadOnly, setIsReadOnly] = useState(false);

    // Review Mode state
    const [requestData, setRequestData] = useState(null);

    // Quick Client Creation State
    const [showClientModal, setShowClientModal] = useState(false);
    const [newClient, setNewClient] = useState({ nombre: '', rut: '', email: '', telefono: '', direccion: '' });
    const [clientModalError, setClientModalError] = useState('');

    const { register, control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm({
        defaultValues: {
            cliente: null, // Cambiado a objecto o null para react-select
            fecha_vencimiento: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 15 días por defecto
            estado: 'BORRADOR',
            notas: '',
            canal_preferencia: 'EMAIL',
            detalles: [{ producto_id: null, cantidad: 1, precio_unitario: 0, impuesto: 19 }]
        }
    });

    const { fields, append, remove } = useFieldArray({
        control,
        name: "detalles"
    });

    // Watchers para cálculos en tiempo real
    const detallesWatch = watch('detalles');
    const [totals, setTotals] = useState({ neto: 0, iva: 0, total: 0 });

    useEffect(() => {
        loadDependencies();
    }, []);

    useEffect(() => {
        if (clients.length > 0 && products.length > 0) {
            if (isReviewMode) {
                loadReviewData();
            } else if (isEditing) {
                loadQuotation();
            }
        }
    }, [id, clients, products, isReviewMode, requestId]);

    // Calcular totales cuando cambian los detalles
    useEffect(() => {
        calculateTotals(detallesWatch);
    }, [JSON.stringify(detallesWatch)]);

    const loadDependencies = async () => {
        try {
            setLoading(true);
            const [clientsData, productsData] = await Promise.all([
                clientsService.getAll(),
                productsService.getAll()
            ]);

            // Asegurar que sean arrays
            const receivedClients = Array.isArray(clientsData) ? clientsData : (clientsData.results || []);
            const receivedProducts = Array.isArray(productsData) ? productsData : (productsData.results || []);

            setClients(receivedClients);
            setProducts(receivedProducts);
        } catch (err) {
            console.error('Error loading dependencies:', err);
            setError('Error al cargar clientes o productos');
        } finally {
            if (!isEditing && !isReviewMode) setLoading(false);
        }
    };

    const loadReviewData = async () => {
        try {
            setLoading(true);
            const reqData = await requestsService.getById(requestId);
            setRequestData(reqData);

            // Populate form with PROPOSED data
            const proposed = reqData.datos_propuestos;

            // Prepare client for Select
            const clientObj = clients.find(c => c.id === proposed.cliente);
            const selectedClient = clientObj ? {
                value: clientObj.id,
                label: `${clientObj.nombre} ${clientObj.rut ? `(${clientObj.rut})` : ''}`
            } : null;

            // Format details for form
            const formattedDetails = proposed.detalles.map(d => {
                const prodObj = products.find(p => p.id === d.producto);
                return {
                    producto_id: prodObj ? {
                        value: prodObj.id,
                        label: prodObj.nombre,
                        price: prodObj.precio,
                        tax: prodObj.impuesto_total
                    } : null,
                    cantidad: d.cantidad,
                    precio_unitario: d.precio_unitario,
                    impuesto: d.impuesto,
                };
            });

            reset({
                ...proposed,
                cliente: selectedClient,
                fecha_vencimiento: proposed.fecha_vencimiento?.split('T')[0],
                detalles: formattedDetails
            });
            setIsReadOnly(true); // Review is always read-only

        } catch (err) {
            console.error(err);
            setError('Error cargando datos de revisión.');
        } finally {
            setLoading(false);
        }
    };

    const [quotationData, setQuotationData] = useState(null);

    const loadQuotation = async () => {
        try {
            setLoading(true);
            const quotation = await quotationsService.getById(id);
            setQuotationData(quotation);

            // Preparar cliente para Select
            const clientObj = clients.find(c => c.id === (quotation.cliente?.id || quotation.cliente));
            const selectedClient = clientObj ? {
                value: clientObj.id,
                label: `${clientObj.nombre} ${clientObj.rut ? `(${clientObj.rut})` : ''}`
            } : null;

            // Formatear datos para el formulario
            const formData = {
                ...quotation,
                cliente: selectedClient,
                fecha_vencimiento: quotation.fecha_vencimiento?.split('T')[0],
                canal_preferencia: quotation.canal_preferencia || 'EMAIL',
                detalles: quotation.detalles.map(d => {
                    const prodId = d.producto?.id || d.producto;
                    const prodObj = products.find(p => p.id === prodId);
                    return {
                        producto_id: prodObj ? {
                            value: prodObj.id,
                            label: prodObj.nombre, // Solo nombre
                            price: prodObj.precio,
                            tax: prodObj.impuesto_total
                        } : null,
                        cantidad: d.cantidad,
                        precio_unitario: d.precio_unitario,
                        impuesto: d.impuesto, // Mapear el impuesto guardado
                    };
                })
            };

            // Determinar restricciones de edición
            // Requerimiento: "nadie puede editar la cotización una vez creada" (se asume: una vez salida de BORRADOR)
            // Admin solo puede cambiar estado (ENVIADA <-> ACEPTADA <-> RECHAZADA)

            const isBorrador = quotation.estado === 'BORRADOR';

            // Si no es borrador, el contenido es read-only para TODOS
            const contentLocked = !isBorrador;

            // RESTRICCIÓN EMPLEADO: Siempre ReadOnly en edición
            const isEmployee = user?.rol === 'EMPLEADO';
            if (isEditing && isEmployee) {
                // Si es modo solicitud, permitimos editar (para proponer cambios)
                setIsReadOnly(!isRequestMode);
            } else {
                setIsReadOnly(contentLocked);
            }

            // Si es admin, puede cambiar el estado incluso si el contenido está bloqueado
            // Pero NO puede volver a BORRADOR
            if (isAdmin && !isBorrador) {
                // Permitimos guardar cambios de estado
                // El formulario visualmente estará bloqueado (isReadOnly), pero habilitaremos específicamente el select de estado
            } else if (!isBorrador && !isEmployee) { // Warning solo si no es employee (employee ya sabe que es read only)
                setError('Esta cotización está finalizada o enviada. Solo lectura.');
            }

            reset(formData);
        } catch (err) {
            console.error('Error loading quotation:', err);
            setError('Error al cargar la cotización');
        } finally {
            setLoading(false);
        }
    };

    const calculateTotals = (items) => {
        if (!items) return;

        let neto = 0;
        let iva = 0;

        items.forEach(item => {
            const cantidad = parseFloat(item.cantidad) || 0;
            const precio = parseFloat(item.precio_unitario) || 0;
            const impuesto = parseFloat(item.impuesto) || 0;

            const subtotal = cantidad * precio;
            neto += subtotal;
            iva += subtotal * (impuesto / 100);
        });

        setTotals({
            neto,
            iva,
            total: neto + iva
        });
    };

    const handleProductChange = (index, selectedOption) => {
        if (selectedOption) {
            setValue(`detalles.${index}.precio_unitario`, selectedOption.price);
            setValue(`detalles.${index}.impuesto`, selectedOption.tax);
        } else {
            // Optional: reset values if cleared
            setValue(`detalles.${index}.precio_unitario`, 0);
            setValue(`detalles.${index}.impuesto`, 19);
        }
    };

    const onSubmit = async (data) => {
        setLoading(true);
        setError('');

        // Preparar payload
        const payload = {
            cliente: data.cliente?.value, // Extraer ID del objeto Select
            // fecha_vencimiento se asigna automáticamente en el backend (30 días)
            estado: data.estado,
            notas: data.notas,
            canal_preferencia: data.canal_preferencia,
            detalles: data.detalles.map(d => ({
                producto: d.producto_id?.value, // Extraer ID del objeto Select
                cantidad: d.cantidad,
                precio_unitario: d.precio_unitario,
                impuesto: d.impuesto
            }))
        };

        try {
            // Validaciones adicionales antes de guardar
            if (!payload.cliente) {
                setError('Seleccione un cliente.');
                setLoading(false);
                return;
            }

            const selectedClient = clients.find(c => c.id === parseInt(payload.cliente));

            // Validar RUT obligatorio
            if (!selectedClient?.rut) {
                setError('El cliente seleccionado NO tiene RUT registrado. Actualice el cliente antes de generar la cotización.');
                setLoading(false);
                return;
            }

            // Validar Teléfono para WhatsApp
            if (data.canal_preferencia === 'WHATSAPP' && (!selectedClient?.telefono || selectedClient.telefono.length < 8)) {
                setError('El cliente seleccionado NO tiene un teléfono válido para WhatsApp. Actualice el cliente o cambie el canal.');
                setLoading(false);
                return;
            }

            // Validar productos vacíos
            if (payload.detalles.some(d => !d.producto)) {
                setError('Todos los items deben tener un producto seleccionado.');
                setLoading(false);
                return;
            }

            // Si es Modo Solicitud de Cambio
            if (isRequestMode) {
                await requestsService.create({
                    tipo_entidad: 'COTIZACION',
                    entidad_id: id,
                    datos_propuestos: {
                        ...payload,
                        cliente: payload.cliente, // ID
                        fecha_vencimiento: undefined // Dejar que backend maneje o enviar explicitamente
                    }
                });
                alert('Solicitud de cambio enviada correctamente.');
                navigate('/cotizaciones');
                return;
            }

            let response;
            if (isEditing) {
                response = await quotationsService.update(id, payload);
            } else {
                response = await quotationsService.create(payload);
            }

            // Si hay link de WhatsApp (creación interna con canal WhatsApp), abrirlo
            if (response && response.whatsapp_link) {
                window.open(response.whatsapp_link, '_blank');
            }

            navigate('/cotizaciones');
        } catch (err) {
            console.error('Error saving quotation:', err);
            setError('Error al guardar la cotización. Verifique los campos.');
        } finally {
            setLoading(false);
        }
    };

    const onError = (errors) => {
        console.error("Form validation errors:", errors);
    };

    const handleApprove = async () => {
        if (!window.confirm('¿Estás seguro de aprobar esta cotización? Pasará a estado ENVIADA.')) return;

        try {
            setLoading(true);
            const res = await quotationsService.approve(id);
            alert(res.message);

            if (res.whatsapp_link) {
                window.open(res.whatsapp_link, '_blank');
            }

            navigate('/cotizaciones');
            triggerRefresh(); // Actualizar badge inmediatamente
        } catch (err) {
            console.error('Error approving:', err);
            const errorMsg = err.response?.data?.error || 'Error al aprobar la cotización.';
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const handleReject = async () => {
        if (!window.confirm('¿Rechazar esta cotización?')) return;

        // Pedir motivo opcional
        const motivo = window.prompt("Indica el motivo del rechazo (Opcional):");

        try {
            setLoading(true);
            await quotationsService.reject(id, motivo);
            alert('Cotización rechazada correctamente');
            navigate('/cotizaciones');
            triggerRefresh(); // Actualizar badge inmediatamente
        } catch (err) {
            console.error('Error rejecting:', err);
            setError('Error al rechazar la cotización.');
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (val) => {
        return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(val);
    };

    // --- Quick Client Creation Logic ---
    const handleCreateClient = async (e) => {
        e.preventDefault();
        setClientModalError('');

        if (!newClient.nombre || !newClient.rut) {
            setClientModalError('Nombre y RUT son obligatorios.');
            return;
        }

        try {
            setLoading(true);
            const createdClient = await clientsService.create({
                ...newClient,
                empresa: user?.empresa // Asegurar que se asocie a la empresa del usuario
            });

            // Recargar lista de clientes
            const updatedClients = await clientsService.getAll();
            const clientsArray = Array.isArray(updatedClients) ? updatedClients : (updatedClients.results || []);
            setClients(clientsArray);

            // Seleccionar el nuevo cliente
            const newOption = {
                value: createdClient.id,
                label: `${createdClient.nombre} ${createdClient.rut ? `(${createdClient.rut})` : ''}`
            };
            setValue('cliente', newOption);

            // Cerrar y limpiar
            setShowClientModal(false);
            setNewClient({ nombre: '', rut: '', email: '', telefono: '', direccion: '' });
            alert('Cliente creado exitosamente');
        } catch (err) {
            console.error('Error creating client:', err);
            setClientModalError('Error al crear cliente. Verifique que el RUT no exista.');
        } finally {
            setLoading(false);
        }
    };

    // Prepare options for Select
    const clientOptions = clients.map(c => ({
        value: c.id,
        label: `${c.nombre} ${c.rut ? `(${c.rut})` : ''}`
    }));

    const productOptions = products
        .filter(p => p.activo)
        .map(p => ({
            value: p.id,
            label: p.nombre, // Solo nombre, sin precio
            price: p.precio,
            tax: p.impuesto_total || 0
        }));

    // Custom styles for React Select to match design
    const customStyles = {
        control: (provided, state) => ({
            ...provided,
            borderRadius: '8px',
            borderColor: state.isFocused ? 'var(--primary-orange)' : 'var(--gray-300)',
            boxShadow: state.isFocused ? '0 0 0 2px rgba(255, 107, 53, 0.2)' : 'none',
            padding: '2px',
            '&:hover': {
                borderColor: 'var(--primary-orange)'
            }
        }),
        option: (provided, state) => ({
            ...provided,
            backgroundColor: state.isSelected
                ? 'var(--primary-orange)'
                : state.isFocused
                    ? 'var(--orange-light)'
                    : 'white',
            color: state.isSelected ? 'white' : 'var(--text-dark)',
            cursor: 'pointer'
        })
    };

    const handleApproveRequest = async () => {
        try {
            const result = await Swal.fire({
                title: '¿Aprobar cambios?',
                text: "Se actualizará la cotización con los datos propuestos.",
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

    const handleRejectRequest = async () => {
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

    if (loading && isEditing && !quotationData) {
        return <div className="loading-overlay"><div className="spinner"></div></div>;
    }

    return (
        <div className="container-custom">

            {/* --- Header con Nuevo Estilo de Botón --- */}
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '25px', borderBottom: '1px solid var(--gray-200)', paddingBottom: '15px' }}>
                <button
                    onClick={() => navigate(isReviewMode ? '/solicitudes' : '/cotizaciones')}
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
                <div>
                    <h1 style={{ margin: 0, fontSize: '1.8rem' }}>
                        {isReviewMode ? `Revisar Solicitud #${requestId}` :
                            (isRequestMode ? 'Solicitar Cambio en Cotización' : (isEditing ? `Editar Cotización #${id}` : 'Nueva Cotización'))}
                    </h1>
                </div>
            </div>

            {/* Banner de Revisión */}
            {isReviewMode && (
                <div className="alert-custom alert-warning" style={{ marginBottom: '20px' }}>
                    <FiCheck /> Revisando cambios propuestos por {requestData?.solicitante_info?.first_name}.
                </div>
            )}

            <form onSubmit={handleSubmit(onSubmit, onError)} className="card-custom">
                {error && <div className="alert-custom alert-danger" style={{ marginBottom: '20px' }}>{error}</div>}

                {/* --- Encabezado --- */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '30px' }}>


                    <div className="form-group-custom">
                        <label className="form-label-custom" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            Cliente *
                            <button
                                type="button"
                                onClick={() => setShowClientModal(true)}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    color: 'var(--primary-orange)',
                                    cursor: 'pointer',
                                    fontSize: '13px',
                                    fontWeight: 'bold',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '5px'
                                }}
                            >
                                <FiPlus size={14} /> Nuevo Cliente
                            </button>
                        </label>
                        <Controller
                            name="cliente"
                            control={control}
                            rules={{ required: 'Selecciona un cliente' }}
                            render={({ field }) => (
                                <Select
                                    {...field}
                                    options={clientOptions}
                                    placeholder="Buscar cliente..."
                                    styles={customStyles}
                                    isDisabled={isApprovalMode || isReadOnly}
                                    isClearable
                                />
                            )}
                        />
                        {errors.cliente && <span className="form-error">{errors.cliente.message}</span>}
                    </div>

                    <div className="form-group-custom">
                        <label className="form-label-custom">Fecha de Vencimiento *</label>
                        <input
                            type="date"
                            {...register('fecha_vencimiento', { required: true })}
                            className="form-control-custom"
                            disabled={isApprovalMode || isReadOnly}
                        />
                    </div>

                    {isEditing && (
                        <div className="form-group-custom">
                            <label className="form-label-custom">Estado</label>
                            <select
                                {...register('estado')}
                                className="form-control-custom"
                                disabled={!isAdmin && isReadOnly} // Admin puede editar estado siempre, otros no si está readOnly
                            >
                                {/* Si es Borrador, mostramos opciones normales (o solo Borrador/Enviada) */}
                                {quotationData?.estado === 'BORRADOR' && <option value="BORRADOR">Borrador</option>}

                                {/* Admin puede mover entre estos estados, pero no volver a Borrador si ya salió */}
                                <option value="ENVIADA">Enviada</option>
                                <option value="ACEPTADA">Aceptada</option>
                                <option value="RECHAZADA">Rechazada</option>
                            </select>
                            {isAdmin && isReadOnly && <small className="text-muted">Modo Admin: Solo cambio de estado permitido.</small>}
                        </div>
                    )}

                    <div className="form-group-custom">
                        <label className="form-label-custom">Canal Preferencia</label>
                        <div style={{ display: 'flex', gap: '15px', marginTop: '8px' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
                                <input
                                    type="radio"
                                    value="EMAIL"
                                    {...register('canal_preferencia')}
                                    disabled={isApprovalMode || isReadOnly}
                                /> Email
                            </label>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
                                <input
                                    type="radio"
                                    value="WHATSAPP"
                                    {...register('canal_preferencia')}
                                    disabled={isApprovalMode || isReadOnly}
                                /> WhatsApp
                            </label>
                        </div>
                    </div>
                </div>

                {/* --- Detalles (Productos) --- */}
                <div style={{ marginBottom: '30px' }}>
                    <h4 style={{ borderBottom: '1px solid var(--gray-200)', paddingBottom: '10px' }}>Items</h4>

                    <table className="table-custom" style={{ marginTop: '10px' }}>
                        <thead>
                            <tr>
                                <th style={{ width: '40%' }}>Producto / Servicio</th>
                                <th style={{ width: '15%' }}>Precio Unit.</th>
                                <th style={{ width: '10%' }}>Cant.</th>
                                <th style={{ width: '15%' }}>Impuesto %</th>
                                <th style={{ width: '15%' }}>Total</th>
                                <th style={{ width: '5%' }}></th>
                            </tr>
                        </thead>
                        <tbody>
                            {fields.map((field, index) => {
                                // Safe parsing for calculations
                                const precio = parseFloat(watch(`detalles.${index}.precio_unitario`) || 0);
                                const cantidad = parseFloat(watch(`detalles.${index}.cantidad`) || 0);
                                const impuesto = parseFloat(watch(`detalles.${index}.impuesto`) || 0); // Default to 0 if NaN

                                const subtotal = precio * cantidad;
                                // If you want to show total line WITH tax:
                                const totalLinea = subtotal * (1 + (impuesto / 100));

                                return (
                                    <tr key={field.id}>
                                        <td>
                                            <Controller
                                                name={`detalles.${index}.producto_id`}
                                                control={control}
                                                rules={{ required: true }}
                                                render={({ field: { onChange, value, ref } }) => (
                                                    <Select
                                                        ref={ref}
                                                        options={products.map(p => ({
                                                            value: p.id,
                                                            label: p.nombre,
                                                            price: p.precio,
                                                            tax: p.impuesto_total
                                                        }))}
                                                        value={value}
                                                        onChange={(val) => {
                                                            onChange(val);
                                                            handleProductChange(index, val);
                                                        }}
                                                        placeholder="Buscar producto..."
                                                        isDisabled={isReadOnly}
                                                        isClearable
                                                    />
                                                )}
                                            />
                                        </td>
                                        <td>
                                            <div style={{ position: 'relative' }}>
                                                <span style={{ position: 'absolute', left: '8px', top: '10px', fontSize: '12px' }}>$</span>
                                                <input
                                                    type="number"
                                                    {...register(`detalles.${index}.precio_unitario`)}
                                                    className="form-control-custom"
                                                    style={{ paddingLeft: '20px', paddingRight: '5px', backgroundColor: '#f3f4f6' }}
                                                    readOnly // Bloquear edición de precios por requerimiento
                                                />
                                            </div>
                                        </td>
                                        <td>
                                            <input
                                                type="number"
                                                min="1"
                                                {...register(`detalles.${index}.cantidad`)}
                                                className="form-control-custom"
                                                style={{ textAlign: 'center' }}
                                                disabled={isReadOnly}
                                            />
                                        </td>
                                        <td>
                                            <input
                                                type="number"
                                                {...register(`detalles.${index}.impuesto`)}
                                                className="form-control-custom"
                                                readOnly
                                                style={{ backgroundColor: 'var(--gray-100)', textAlign: 'center' }}
                                            />
                                        </td>
                                        <td style={{ fontWeight: 'bold', textAlign: 'right' }}>
                                            {formatCurrency(totalLinea)}
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            {!isReadOnly && (
                                                <button
                                                    type="button"
                                                    onClick={() => remove(index)}
                                                    className="btn-icon"
                                                    style={{ color: 'var(--danger-red)', border: 'none', background: 'none', cursor: 'pointer' }}
                                                >
                                                    <FiTrash2 size={18} />
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>

                    {!isReadOnly && (
                        <button
                            type="button"
                            className="btn-custom btn-secondary btn-sm"
                            style={{ marginTop: '15px' }}
                            onClick={() => append({ producto_id: null, cantidad: 1, precio_unitario: 0, impuesto: 19 })}
                        >
                            <FiPlus size={16} /> Agregar Item
                        </button>
                    )}
                </div>

                {/* --- Totales --- */}
                < div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '30px' }}>
                    <div style={{ width: '300px', backgroundColor: 'var(--gray-50)', padding: '20px', borderRadius: '12px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                            <span>Subtotal Neto:</span>
                            <strong>{formatCurrency(totals.neto)}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                            <span>Impuesto (IVA):</span>
                            <strong>{formatCurrency(totals.iva)}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '2px solid var(--gray-300)', paddingTop: '10px', fontSize: '1.2em' }}>
                            <span>TOTAL:</span>
                            <strong style={{ color: 'var(--primary-orange)' }}>{formatCurrency(totals.total)}</strong>
                        </div>
                    </div>
                </div >

                {/* --- Bloque de Información de Decisión --- */}
                {quotationData && quotationData.estado !== 'BORRADOR' && (
                    <div className="card-custom" style={{ marginTop: '20px', marginBottom: '30px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', padding: '15px', borderRadius: '8px' }}>
                        <h4 style={{ fontSize: '16px', color: '#475569', marginBottom: '15px' }}>Historial de Decisión (Envío)</h4>
                        <div style={{ fontSize: '14px', color: '#334155' }}>
                            {quotationData.es_decision_automatica ? (
                                <p style={{ marginBottom: '5px' }}><strong>Decisión:</strong> <span style={{ color: '#059669' }}>Aprobación Automática (Sistema)</span></p>
                            ) : (
                                <p style={{ marginBottom: '5px' }}>
                                    <strong>Decisión tomada por:</strong> {quotationData.usuario_decision_nombre || `Cliente (${quotationData.cliente_info?.nombre || 'Web'})`}
                                </p>
                            )}

                            {quotationData.fecha_decision && (
                                <p style={{ marginBottom: '5px' }}><strong>Fecha de decisión:</strong> {new Date(quotationData.fecha_decision).toLocaleString()}</p>
                            )}

                            {quotationData.motivo_rechazo && (
                                <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#fee2e2', borderRadius: '4px', borderLeft: '4px solid #ef4444' }}>
                                    <strong>Motivo de rechazo:</strong> <br />
                                    {quotationData.motivo_rechazo}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* --- Notas --- */}
                < div className="form-group-custom" >
                    <label className="form-label-custom">Notas Adicionales</label>
                    <textarea
                        {...register('notas')}
                        className="form-control-custom"
                        rows="3"
                        placeholder="Términos, condiciones, comentarios..."
                        disabled={isApprovalMode || isReadOnly}
                    />
                </div >

                {/* --- Botones --- */}
                {
                    isReviewMode ? (
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '15px', marginTop: '30px', paddingTop: '20px', borderTop: '1px solid var(--gray-200)' }}>
                            <button type="button" className="btn-custom btn-secondary" onClick={() => navigate('/solicitudes')}>
                                Cancelar
                            </button>
                            <button type="button" className="btn-custom btn-danger" onClick={handleRejectRequest} disabled={loading}>
                                <FiX size={20} /> Rechazar
                            </button>
                            <button type="button" className="btn-custom btn-success" onClick={handleApproveRequest} disabled={loading} style={{ backgroundColor: 'var(--success-green)', color: 'white' }}>
                                <FiCheck size={20} /> Aprobar Cambios
                            </button>
                        </div>
                    ) : (
                        (!isApprovalMode) && (
                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '15px', marginTop: '30px', paddingTop: '20px', borderTop: '1px solid var(--gray-200)' }}>
                                <button type="button" className="btn-custom btn-secondary" onClick={() => navigate('/cotizaciones')}>
                                    Cancelar
                                </button>

                                {/* Mostrar botón de guardar si no es ReadOnly O si es Admin (para cambiar estado) */}
                                {(!isReadOnly || isAdmin || isRequestMode) && (
                                    <button type="submit" className="btn-custom btn-primary" disabled={loading}>
                                        <FiSave size={20} />
                                        {loading
                                            ? 'Procesando...'
                                            : (isRequestMode ? 'Enviar Solicitud de Cambio' : (isEditing ? 'Guardar Cambios' : 'Enviar Cotización'))
                                        }
                                    </button>
                                )}
                            </div>
                        )
                    )
                }
            </form >
            {/* --- Modal Crear Cliente Rápido --- */}
            {showClientModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000
                }}>
                    <div className="card-custom" style={{ width: '500px', padding: '25px', position: 'relative' }}>
                        <button
                            onClick={() => setShowClientModal(false)}
                            style={{ position: 'absolute', top: '15px', right: '15px', background: 'none', border: 'none', cursor: 'pointer' }}
                        >
                            <FiX size={24} />
                        </button>

                        <h3 style={{ marginBottom: '20px', color: 'var(--primary-orange)' }}>Nuevo Cliente</h3>

                        {clientModalError && <div className="alert-custom alert-danger" style={{ marginBottom: '15px' }}>{clientModalError}</div>}

                        <form onSubmit={handleCreateClient}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                                <div className="form-group-custom">
                                    <label className="form-label-custom">Nombre *</label>
                                    <input
                                        type="text"
                                        className="form-control-custom"
                                        value={newClient.nombre}
                                        onChange={e => setNewClient({ ...newClient, nombre: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="form-group-custom">
                                    <label className="form-label-custom">RUT *</label>
                                    <input
                                        type="text"
                                        className="form-control-custom"
                                        value={newClient.rut}
                                        onChange={e => setNewClient({ ...newClient, rut: e.target.value })}
                                        required
                                        placeholder="12345678-9"
                                    />
                                </div>
                                <div className="form-group-custom">
                                    <label className="form-label-custom">Email</label>
                                    <input
                                        type="email"
                                        className="form-control-custom"
                                        value={newClient.email}
                                        onChange={e => setNewClient({ ...newClient, email: e.target.value })}
                                    />
                                </div>
                                <div className="form-group-custom">
                                    <label className="form-label-custom">Teléfono</label>
                                    <input
                                        type="text"
                                        className="form-control-custom"
                                        value={newClient.telefono}
                                        onChange={e => setNewClient({ ...newClient, telefono: e.target.value })}
                                        placeholder="+569..."
                                    />
                                </div>
                            </div>
                            <div className="form-group-custom" style={{ marginTop: '15px' }}>
                                <label className="form-label-custom">Dirección</label>
                                <input
                                    type="text"
                                    className="form-control-custom"
                                    value={newClient.direccion}
                                    onChange={e => setNewClient({ ...newClient, direccion: e.target.value })}
                                />
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
                                <button type="button" className="btn-custom btn-secondary" onClick={() => setShowClientModal(false)}>
                                    Cancelar
                                </button>
                                <button type="submit" className="btn-custom btn-primary">
                                    Guardar Cliente
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div >
    );
};

export default QuotationForm;

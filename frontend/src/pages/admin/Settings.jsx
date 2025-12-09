import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { FiSave, FiSettings, FiImage, FiExternalLink, FiTrash2 } from 'react-icons/fi';
import companyService from '../../services/company.service';
import { useAuth } from '../../context/AuthContext';

import rulesService from '../../services/rules.service';

const Settings = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [company, setCompany] = useState(null);
    const [logoPreview, setLogoPreview] = useState(null);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // State for Rules
    const [rules, setRules] = useState([]);
    const [deletedRules, setDeletedRules] = useState([]);

    const { register, handleSubmit, setValue, getValues, watch, formState: { errors } } = useForm();
    const logoFile = watch('logo_file');

    const insertTag = (fieldName, tag) => {
        // Obtenemos el elemento del DOM para manipular la posición del cursor
        const textarea = document.querySelector(`textarea[name="${fieldName}"]`);

        if (textarea) {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = textarea.value;
            const before = text.substring(0, start);
            const after = text.substring(end, text.length);
            const newValue = before + tag + after;

            // Actualizamos el estado del formulario
            setValue(fieldName, newValue, { shouldValidate: true, shouldDirty: true });

            // Re-enfocamos y movemos el cursor después del tag insertado
            setTimeout(() => {
                textarea.focus();
                textarea.setSelectionRange(start + tag.length, start + tag.length);
            }, 0);
        } else {
            // Fallback si no encontramos el DOM (raro)
            const current = getValues(fieldName) || '';
            setValue(fieldName, current + tag, { shouldValidate: true, shouldDirty: true });
        }
    };

    useEffect(() => {
        loadCompany();
    }, []);

    // Actualizar previsualización del logo
    useEffect(() => {
        if (logoFile && logoFile.length > 0) {
            const file = logoFile[0];
            const reader = new FileReader();
            reader.onloadend = () => {
                setLogoPreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    }, [logoFile]);

    const loadCompany = async () => {
        try {
            setLoading(true);
            const data = await companyService.getMyCompany();
            setCompany(data);

            // Setear valores del formulario
            setValue('nombre', data.nombre);
            setValue('rut', data.rut);
            setValue('direccion', data.direccion);
            setValue('telefono', data.telefono);
            setValue('email', data.email);
            setValue('mensaje_autoatencion', data.mensaje_autoatencion);
            setValue('autoaprobar_cotizaciones', data.autoaprobar_cotizaciones);
            setValue('mensaje_correo_cotizacion', data.mensaje_correo_cotizacion);
            setValue('mensaje_whatsapp_cotizacion', data.mensaje_whatsapp_cotizacion);
            setValue('mensajeria_automatica_activa', data.mensajeria_automatica_activa);

            if (data.logo_url) {
                setLogoPreview(data.logo_url);
            }

            // Cargar reglas
            try {
                const rulesData = await rulesService.getAll();
                // Manejar posible paginación o respuesta inesperada
                if (Array.isArray(rulesData)) {
                    setRules(rulesData);
                } else if (rulesData && Array.isArray(rulesData.results)) {
                    setRules(rulesData.results);
                } else {
                    console.warn("Formato de reglas inesperado:", rulesData);
                    setRules([]);
                }
            } catch (e) {
                console.error("Error loading rules", e);
                setRules([]);
            }
        } catch (err) {
            console.error('Error loading company:', err);
            setError('Error al cargar datos de la empresa');
        } finally {
            setLoading(false);
        }
    };

    // Handlers for Rules
    const handleAddRule = () => {
        setRules([...rules, {
            orden: rules.length + 1,
            tiempo_espera_valor: 1,
            tiempo_espera_unidad: 'MINUTOS', // Default para testing rápido
            descuento_porcentaje: 5,
            tiempo_validez_valor: 24,
            tiempo_validez_unidad: 'HORAS'
        }]);
    };

    const handleRemoveRule = (index) => {
        const ruleToRemove = rules[index];
        if (ruleToRemove.id) {
            setDeletedRules([...deletedRules, ruleToRemove.id]);
        }
        const newRules = rules.filter((_, i) => i !== index);
        // Reordenar
        const reordered = newRules.map((r, i) => ({ ...r, orden: i + 1 }));
        setRules(reordered);
    };

    const handleRuleChange = (index, field, value) => {
        const newRules = [...rules];
        newRules[index][field] = value;
        setRules(newRules);
    };

    const onSubmit = async (data) => {
        setSaving(true);
        setError('');
        setSuccess('');

        try {
            const formData = new FormData();
            formData.append('nombre', data.nombre);
            formData.append('direccion', data.direccion);
            formData.append('telefono', data.telefono);
            formData.append('email', data.email);
            formData.append('mensaje_autoatencion', data.mensaje_autoatencion);
            formData.append('autoaprobar_cotizaciones', data.autoaprobar_cotizaciones);
            formData.append('mensaje_correo_cotizacion', data.mensaje_correo_cotizacion);
            formData.append('mensaje_whatsapp_cotizacion', data.mensaje_whatsapp_cotizacion);
            formData.append('mensajeria_automatica_activa', data.mensajeria_automatica_activa ? 'True' : 'False');

            // Solo agregar logo si se seleccionó uno nuevo
            if (data.logo_file && data.logo_file.length > 0) {
                formData.append('logo', data.logo_file[0]);
            }

            const updatedCompany = await companyService.update(company.id, formData);
            setCompany(updatedCompany);

            // Guardar reglas si está activo (o siempre, según preferencia)
            // Procesar eliminaciones
            for (const id of deletedRules) {
                await rulesService.delete(id);
            }
            setDeletedRules([]); // Limpiar

            // Procesar creaciones/actualizaciones
            const rulesPromises = rules.map(rule => {
                const ruleData = {
                    ...rule,
                    orden: rule.orden,
                    empresa: company.id
                };

                if (rule.id) {
                    return rulesService.update(rule.id, ruleData);
                } else {
                    return rulesService.create(ruleData);
                }
            });

            await Promise.all(rulesPromises);

            // Recargar reglas con manejo seguro de respuesta
            try {
                const refreshedRules = await rulesService.getAll();
                if (Array.isArray(refreshedRules)) {
                    setRules(refreshedRules);
                } else if (refreshedRules && Array.isArray(refreshedRules.results)) {
                    setRules(refreshedRules.results);
                } else {
                    setRules([]);
                }
            } catch (e) {
                console.error("Error reloading rules:", e);
                // No limpiar reglas si falla la recarga para no asustar al usuario,
                // o quizás sí para mostrar estado real. Mantenemos las que estaban en memoria o vacío?
                // Mejor no hacer nada si falla, el usuario verá el success de guardado al menos.
            }

            setSuccess('Configuración guardada correctamente.');

            // Recargar página si se subió un logo para reflejar cambios en sidebar
            if (data.logo_file && data.logo_file.length > 0) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }

        } catch (err) {
            console.error('Error updating company:', err);
            setError('Error al guardar cambios.');
        } finally {
            setSaving(false);
        }
    };

    const handleRemoveLogo = async () => {
        if (!window.confirm('¿Estás seguro de que deseas eliminar el logo?')) {
            return;
        }

        setSaving(true);
        setError('');
        setSuccess('');

        try {
            const formData = new FormData();
            formData.append('nombre', company.nombre);
            formData.append('direccion', company.direccion);
            formData.append('telefono', company.telefono);
            formData.append('email', company.email);
            formData.append('mensaje_autoatencion', company.mensaje_autoatencion);
            formData.append('logo', ''); // Enviar string vacío para eliminar logo

            const updatedCompany = await companyService.update(company.id, formData);
            setCompany(updatedCompany);
            setLogoPreview(null);
            setSuccess('Logo eliminado correctamente.');

            // Recargar página para reflejar cambios en sidebar
            setTimeout(() => {
                window.location.reload();
            }, 1000);

        } catch (err) {
            console.error('Error removing logo:', err);
            setError('Error al eliminar logo.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="container-custom">
            <div className="card-header-custom" style={{ marginTop: '20px', borderBottom: 'none' }}>
                <div>
                    <h2>Configuración de Empresa</h2>
                    <p className="text-muted">Personaliza tu marca y portal de autoatención</p>
                </div>
            </div>

            {error && <div className="alert-custom alert-danger">{error}</div>}
            {success && <div className="alert-custom alert-success">{success}</div>}

            {/* Formulario Global */}
            <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '30px' }}>

                {/* Columna Izquierda: Datos */}
                <div className="card-custom">
                    <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <FiSettings /> Datos Generales
                    </h3>

                    <div className="form-group-custom">
                        <label className="form-label-custom">Nombre Empresa *</label>
                        <input
                            {...register('nombre', { required: 'El nombre es obligatorio' })}
                            className="form-control-custom"
                        />
                        {errors.nombre && <span className="form-error">{errors.nombre.message}</span>}
                    </div>

                    <div className="form-group-custom">
                        <label className="form-label-custom">RUT (Solo lectura)</label>
                        <input
                            {...register('rut')}
                            className="form-control-custom"
                            disabled
                            style={{ backgroundColor: 'var(--gray-100)' }}
                        />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div className="form-group-custom">
                            <label className="form-label-custom">Teléfono</label>
                            <input
                                {...register('telefono')}
                                className="form-control-custom"
                            />
                        </div>
                        <div className="form-group-custom">
                            <label className="form-label-custom">Email Contacto</label>
                            <input
                                {...register('email')}
                                className="form-control-custom"
                            />
                        </div>
                    </div>

                    <div className="form-group-custom">
                        <label className="form-label-custom">Dirección</label>
                        <input
                            {...register('direccion')}
                            className="form-control-custom"
                        />
                    </div>

                    <div className="form-group-custom" style={{ marginTop: '20px' }}>
                        <div style={{ padding: '15px', backgroundColor: 'var(--blue-50)', borderRadius: '8px', marginBottom: '10px' }}>
                            <label className="form-label-custom" style={{ color: 'var(--blue-800)' }}>Portal de Autoatención</label>
                            <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: '5px' }}>
                                <input
                                    readOnly
                                    value={`${window.location.origin}/autoatencion/${company?.slug_autoatencion || ''}`}
                                    className="form-control-custom"
                                    style={{ fontSize: '13px', backgroundColor: 'white' }}
                                />
                                <a
                                    href={`${window.location.origin}/autoatencion/${company?.slug_autoatencion || ''}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="btn-custom btn-secondary btn-sm"
                                    title="Abrir enlace"
                                >
                                    <FiExternalLink />
                                </a>
                            </div>
                        </div>

                        <label className="form-label-custom">Mensaje de Bienvenida (Autoatención)</label>
                        <textarea
                            {...register('mensaje_autoatencion')}
                            className="form-control-custom"
                            rows="4"
                            placeholder="Ej: Bienvenido a nuestro portal de cotizaciones. Selecciona tus productos y te responderemos a la brevedad."
                        />
                        <p className="text-muted" style={{ fontSize: '12px', marginTop: '5px' }}>
                            Este mensaje aparecerá en la parte superior del formulario público de cotización.
                        </p>
                    </div>

                    <div className="form-group-custom" style={{ marginTop: '20px' }}>
                        <h4 style={{ fontSize: '16px', marginBottom: '15px' }}>Personalización de Mensajes</h4>

                        <div style={{ marginBottom: '15px' }}>
                            <label className="form-label-custom">Mensaje Correo Electrónico</label>
                            <textarea
                                {...register('mensaje_correo_cotizacion')}
                                className="form-control-custom"
                                rows="4"
                                placeholder="Ej: Estimado {cliente_nombre}, adjunto su cotización #{cotizacion_numero}..."
                            />
                            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
                                {[
                                    { tag: '{cliente_nombre}', label: 'Nombre Cliente' },
                                    { tag: '{cotizacion_numero}', label: 'N° Cotización' },
                                    { tag: '{empresa_nombre}', label: 'Nombre Empresa' },
                                    { tag: '{total}', label: 'Monto Total' },
                                    { tag: '{empresa_logo}', label: 'Logo Empresa' }
                                ].map(item => (
                                    <button
                                        key={item.tag}
                                        type="button"
                                        onClick={() => insertTag('mensaje_correo_cotizacion', item.tag)}
                                        className="badge"
                                        style={{
                                            border: 'none',
                                            cursor: 'pointer',
                                            padding: '8px 12px',
                                            fontSize: '12px',
                                            backgroundColor: 'var(--info-blue)',
                                            color: 'var(--white)',
                                            borderRadius: '20px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '5px',
                                            fontWeight: '500'
                                        }}
                                        title={`Insertar ${item.label}`}
                                    >
                                        + {item.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <label className="form-label-custom">Mensaje WhatsApp</label>
                            <textarea
                                {...register('mensaje_whatsapp_cotizacion')}
                                className="form-control-custom"
                                rows="3"
                                placeholder="Ej: Hola {cliente_nombre}, aquí tienes tu cotización #{cotizacion_numero}..."
                            />
                            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
                                {[
                                    { tag: '{cliente_nombre}', label: 'Nombre Cliente' },
                                    { tag: '{cotizacion_numero}', label: 'N° Cotización' },
                                    { tag: '{empresa_nombre}', label: 'Nombre Empresa' }
                                ].map(item => (
                                    <button
                                        key={item.tag}
                                        type="button"
                                        onClick={() => insertTag('mensaje_whatsapp_cotizacion', item.tag)}
                                        className="badge"
                                        style={{
                                            border: 'none',
                                            cursor: 'pointer',
                                            padding: '8px 12px',
                                            fontSize: '12px',
                                            backgroundColor: 'var(--success-green)',
                                            color: '#fff',
                                            borderRadius: '20px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '5px',
                                            fontWeight: '500'
                                        }}
                                        title={`Insertar ${item.label}`}
                                    >
                                        + {item.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="form-group-custom" style={{ marginTop: '20px', padding: '15px', backgroundColor: 'var(--gray-50)', borderRadius: '8px' }}>
                        <label className="form-label-custom" style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', marginBottom: 0 }}>
                            <input
                                type="checkbox"
                                {...register('autoaprobar_cotizaciones')}
                                style={{ width: '18px', height: '18px', accentColor: 'var(--primary-orange)' }}
                            />
                            <span>Habilitar Auto-aprobación de Cotizaciones</span>
                        </label>
                        <p className="text-muted" style={{ fontSize: '12px', marginTop: '5px', marginLeft: '28px' }}>
                            Si se activa, las cotizaciones recibidas por el link de autoatención se marcarán automáticamente como <strong>ENVIADA</strong> en lugar de BORRADOR.
                        </p>
                    </div>

                    {/* Sección Mensajería Automática */}
                    <div style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
                        <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '1.2rem' }}>
                            <FiSettings /> Mensajería Automática (Fidelización)
                        </h3>

                        <div className="form-check form-switch mb-4">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                id="mensajeriaSwitch"
                                {...register('mensajeria_automatica_activa')}
                            />
                            <label className="form-check-label ms-2" htmlFor="mensajeriaSwitch">
                                Habilitar envío automático de ofertas
                            </label>
                        </div>

                        {watch('mensajeria_automatica_activa') && (
                            <div className="table-responsive">
                                <table className="table">
                                    <thead>
                                        <tr>
                                            <th>Orden</th>
                                            <th>Esperar</th>
                                            <th>Unidad</th>
                                            <th>Descuento (%)</th>
                                            <th>Validez</th>
                                            <th>Unidad</th>
                                            <th>Acción</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {Array.isArray(rules) && rules.map((rule, index) => (
                                            <tr key={index}>
                                                <td>{index + 1}</td>
                                                <td>
                                                    <input
                                                        type="number"
                                                        className="form-control form-control-sm"
                                                        value={rule.tiempo_espera_valor}
                                                        onChange={(e) => handleRuleChange(index, 'tiempo_espera_valor', e.target.value)}
                                                        min="1"
                                                    />
                                                </td>
                                                <td>
                                                    <select
                                                        className="form-select form-select-sm"
                                                        value={rule.tiempo_espera_unidad}
                                                        onChange={(e) => handleRuleChange(index, 'tiempo_espera_unidad', e.target.value)}
                                                    >
                                                        <option value="MINUTOS">Minutos</option>
                                                        <option value="HORAS">Horas</option>
                                                        <option value="DIAS">Días</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <input
                                                        type="number"
                                                        className="form-control form-control-sm"
                                                        value={rule.descuento_porcentaje}
                                                        onChange={(e) => handleRuleChange(index, 'descuento_porcentaje', e.target.value)}
                                                        min="1" max="100"
                                                    />
                                                </td>
                                                <td>
                                                    <input
                                                        type="number"
                                                        className="form-control form-control-sm"
                                                        value={rule.tiempo_validez_valor}
                                                        onChange={(e) => handleRuleChange(index, 'tiempo_validez_valor', e.target.value)}
                                                        min="1"
                                                    />
                                                </td>
                                                <td>
                                                    <select
                                                        className="form-select form-select-sm"
                                                        value={rule.tiempo_validez_unidad}
                                                        onChange={(e) => handleRuleChange(index, 'tiempo_validez_unidad', e.target.value)}
                                                    >
                                                        <option value="MINUTOS">Minutos</option>
                                                        <option value="HORAS">Horas</option>
                                                        <option value="DIAS">Días</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <button
                                                        type="button"
                                                        className="btn btn-outline-danger btn-sm"
                                                        onClick={() => handleRemoveRule(index)}
                                                    >
                                                        <FiTrash2 />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                <button
                                    type="button"
                                    className="btn btn-outline-primary btn-sm"
                                    onClick={handleAddRule}
                                >
                                    + Agregar Regla
                                </button>
                                <p className="text-muted mt-2" style={{ fontSize: '0.8rem' }}>
                                    Las ofertas se envían secuencialmente. Cada nueva oferta invalida la anterior.
                                </p>
                            </div>
                        )}
                    </div>


                    <div style={{ marginTop: '30px', textAlign: 'right' }}>
                        <button type="submit" className="btn-custom btn-primary" disabled={saving}>
                            <FiSave size={18} style={{ marginRight: '8px' }} />
                            {saving ? 'Guardando...' : 'Guardar Cambios'}
                        </button>
                    </div>
                </div>

                {/* Columna Derecha: Logo */}
                <div className="card-custom" style={{ height: 'fit-content' }}>
                    <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <FiImage /> Logo Corporativo
                    </h3>

                    <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                        <div style={{
                            width: '200px',
                            height: '200px',
                            borderRadius: '50%',
                            border: '2px dashed var(--gray-300)',
                            margin: '0 auto',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            overflow: 'hidden',
                            backgroundColor: 'white',
                            position: 'relative'
                        }}>
                            {logoPreview ? (
                                <img
                                    src={logoPreview}
                                    alt="Logo Preview"
                                    style={{ width: '100%', height: '100%', objectFit: 'contain', padding: '10px' }}
                                />
                            ) : (
                                <div style={{ color: 'var(--gray-400)' }}>
                                    <FiImage size={48} />
                                    <p>Sin Logo</p>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="form-group-custom">
                        <label className="btn-custom btn-secondary" style={{ width: '100%', display: 'block', textAlign: 'center', cursor: 'pointer' }}>
                            Seleccionar Imagen
                            <input
                                type="file"
                                accept="image/*"
                                {...register('logo_file')}
                                style={{ display: 'none' }}
                            />
                        </label>

                        {logoPreview && (
                            <button
                                type="button"
                                onClick={handleRemoveLogo}
                                className="btn-custom btn-danger"
                                style={{ width: '100%', marginTop: '10px' }}
                                disabled={saving}
                            >
                                <FiTrash2 size={16} style={{ marginRight: '8px' }} />
                                Quitar Logo
                            </button>
                        )}

                        <p className="text-muted" style={{ fontSize: '12px', textAlign: 'center', marginTop: '10px' }}>
                            Recomendado: PNG o JPG, fondo transparente.
                        </p>

                    </div>
                </div>

            </form>
        </div>
    );
};

export default Settings;

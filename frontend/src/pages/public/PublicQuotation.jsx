import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { FiShoppingCart, FiPlus, FiTrash2, FiCheck, FiSend, FiShoppingBag, FiUser, FiInfo } from 'react-icons/fi';
import publicService from '../../services/public.service';
import SearchableSelect from '../../components/common/SearchableSelect';

const PublicQuotation = () => {
    const { slug } = useParams();
    const [company, setCompany] = useState(null);
    const [products, setProducts] = useState([]); // Productos de la empresa
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    const { register, control, handleSubmit, watch, setValue, formState: { errors } } = useForm({
        defaultValues: {
            nombre_cliente: '',
            rut_cliente: '',
            email_cliente: '',
            telefono_cliente: '',
            comentarios: '',
            items: [{ producto_id: '', cantidad: 1 }]
        }
    });

    const { fields, append, remove } = useFieldArray({
        control,
        name: "items"
    });

    useEffect(() => {
        loadCompanyInfo();
    }, [slug]);

    const loadCompanyInfo = async () => {
        try {
            setLoading(true);
            const data = await publicService.getCompanyInfo(slug);
            if (data.empresa) {
                setCompany(data.empresa);
            }
            if (data.productos) {
                setProducts(data.productos);
            }
        } catch (err) {
            console.error('Error loading company:', err);
            setError('Empresa no encontrada o enlace inválido.');
        } finally {
            setLoading(false);
        }
    };

    const onSubmit = async (data) => {
        setSubmitting(true);
        try {
            // Filtrar items vacíos
            const validItems = data.items.filter(i => i.producto_id && i.cantidad > 0);

            if (validItems.length === 0) {
                alert('Por favor agrega al menos un producto a la cotización.');
                setSubmitting(false);
                return;
            }

            const payload = {
                cliente_nombre: data.nombre_cliente,
                cliente_email: data.email_cliente,
                cliente_telefono: data.telefono_cliente,
                cliente_rut: data.rut_cliente,
                notas: data.comentarios,
                canal_preferencia: data.canal_preferencia,
                detalles: validItems.map(i => ({
                    producto_id: i.producto_id,
                    cantidad: parseInt(i.cantidad)
                }))
            };

            await publicService.createQuotation(slug, payload);
            setSuccess(true);
        } catch (err) {
            console.error('Error submitting quotation:', err);
            alert('Hubo un error al enviar tu solicitud. Intenta nuevamente.');
        } finally {
            setSubmitting(false);
        }
    };



    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    if (error) {
        return (
            <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--background-cream)' }}>
                <div className="card-custom" style={{ textAlign: 'center', padding: '40px', maxWidth: '500px' }}>
                    <FiInfo size={48} color="var(--danger-red)" />
                    <h3 style={{ marginTop: '20px' }}>Enlace Inválido</h3>
                    <p className="text-muted">{error}</p>
                </div>
            </div>
        );
    }

    if (success) {
        return (
            <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--background-cream)' }}>
                <div className="card-custom" style={{ textAlign: 'center', padding: '40px', maxWidth: '600px' }}>
                    <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: '#d1fae5', color: '#059669', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto' }}>
                        <FiCheck size={40} />
                    </div>
                    <h2 style={{ marginTop: '20px', color: 'var(--text-dark)' }}>¡Solicitud Enviada!</h2>
                    <p className="text-muted" style={{ marginBottom: '30px' }}>
                        Gracias por cotizar con <strong>{company?.nombre}</strong>. Hemos recibido tu solicitud y te responderemos a la brevedad al correo <strong>{watch('email_cliente')}</strong>.
                    </p>
                    <button
                        className="btn-custom btn-primary"
                        onClick={() => window.location.reload()}
                    >
                        Nueva Cotización
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div style={{ minHeight: '100vh', backgroundColor: 'var(--background-cream)', padding: '20px 0' }}>
            <div className="container-custom" style={{ maxWidth: '900px' }}>

                {/* Header Empresa */}
                <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                    {company?.logo_url && (
                        <div style={{ marginBottom: '20px' }}>
                            <img
                                src={company.logo_url}
                                alt={`Logo ${company.nombre}`}
                                style={{ maxHeight: '100px', maxWidth: '200px', objectFit: 'contain' }}
                            />
                        </div>
                    )}
                    <h1 style={{ color: 'var(--primary-orange)', fontWeight: 'bold' }}>{company?.nombre || 'Solicitud de Cotización'}</h1>
                    <p className="text-muted">Portal de Autoatención</p>

                    {company?.mensaje_autoatencion && (
                        <div style={{
                            marginTop: '20px',
                            padding: '20px',
                            backgroundColor: 'white',
                            borderRadius: '8px',
                            boxShadow: 'var(--shadow-sm)',
                            borderLeft: '4px solid var(--primary-orange)',
                            textAlign: 'left'
                        }}>
                            <p style={{ margin: 0, whiteSpace: 'pre-line' }}>{company.mensaje_autoatencion}</p>
                        </div>
                    )}
                </div>

                <form onSubmit={handleSubmit(onSubmit)}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>

                        {/* Sección 1: Tus Datos */}
                        <div className="card-custom">
                            <h3 style={{ borderBottom: '1px solid var(--gray-200)', paddingBottom: '15px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <FiUser /> Tus Datos
                            </h3>

                            <div style={{ padding: '15px', marginBottom: '20px', backgroundColor: 'var(--blue-50)', color: 'var(--blue-700)', borderLeft: '4px solid var(--blue-500)', borderRadius: '4px' }}>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <FiInfo size={24} style={{ flexShrink: 0 }} />
                                    <div>
                                        <strong>¡Importante!</strong>
                                        <p style={{ margin: '5px 0 0', fontSize: '14px' }}>
                                            Por favor ingresa un número de teléfono válido. Si seleccionas WhatsApp, te enviaremos la cotización directamente, así que asegúrate de que sea correcto.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                                <div className="form-group-custom">
                                    <label className="form-label-custom">Nombre Completo *</label>
                                    <input
                                        {...register('nombre_cliente', { required: 'Tu nombre es obligatorio' })}
                                        className="form-control-custom"
                                        placeholder="Tu nombre o empresa"
                                    />
                                    {errors.nombre_cliente && <span className="form-error">{errors.nombre_cliente.message}</span>}
                                </div>

                                <div className="form-group-custom">
                                    <label className="form-label-custom">RUT (Sin puntos ni guión) *</label>
                                    <input
                                        {...register('rut_cliente', {
                                            required: 'El RUT es obligatorio',
                                            pattern: { value: /^[0-9]+[0-9kK]{1}$/, message: 'RUT inválido (ej: 123456789)' }
                                        })}
                                        className="form-control-custom"
                                        placeholder="Ej: 123456789"
                                    />
                                    {errors.rut_cliente && <span className="form-error">{errors.rut_cliente.message}</span>}
                                </div>

                                <div className="form-group-custom">
                                    <label className="form-label-custom">Teléfono {watch('canal_preferencia') === 'WHATSAPP' && '*'}</label>
                                    <input
                                        {...register('telefono_cliente', {
                                            required: watch('canal_preferencia') === 'WHATSAPP' ? 'El teléfono es obligatorio para WhatsApp' : false,
                                            pattern: { value: /^\+?[0-9]{8,15}$/, message: 'Teléfono inválido (ej: +56912345678)' }
                                        })}
                                        className="form-control-custom"
                                        placeholder="+56 9 ..."
                                    />
                                    {errors.telefono_cliente && <span className="form-error">{errors.telefono_cliente.message}</span>}
                                </div>
                            </div>

                            <div className="form-group-custom">
                                <label className="form-label-custom">Correo Electrónico *</label>
                                <input
                                    type="email"
                                    {...register('email_cliente', {
                                        required: 'Tu email es obligatorio para enviarte la cotización',
                                        pattern: { value: /^\S+@\S+$/i, message: 'Email inválido' }
                                    })}
                                    className="form-control-custom"
                                    placeholder="ejemplo@correo.com"
                                />
                                {errors.email_cliente && <span className="form-error">{errors.email_cliente.message}</span>}
                            </div>

                            <div className="form-group-custom">
                                <label className="form-label-custom">Prefiero recibir mi cotización por:</label>
                                <div style={{ display: 'flex', gap: '20px', marginTop: '10px' }}>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                        <input
                                            type="radio"
                                            value="EMAIL"
                                            {...register('canal_preferencia')}
                                            defaultChecked
                                        />
                                        Correo Electrónico
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                        <input
                                            type="radio"
                                            value="WHATSAPP"
                                            {...register('canal_preferencia')}
                                        />
                                        WhatsApp
                                    </label>
                                </div>
                            </div>
                        </div>

                        {/* Sección 2: Productos */}
                        <div className="card-custom">
                            <h3 style={{ borderBottom: '1px solid var(--gray-200)', paddingBottom: '15px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <FiShoppingCart /> Productos a Cotizar
                            </h3>

                            {fields.map((field, index) => (
                                <div key={field.id} style={{ display: 'flex', gap: '15px', marginBottom: '15px', alignItems: 'flex-start', padding: '15px', backgroundColor: 'var(--gray-50)', borderRadius: '8px' }}>
                                    <div style={{ flex: 1 }}>
                                        <label className="form-label-custom" style={{ fontSize: '13px' }}>Producto</label>
                                        <Controller
                                            name={`items.${index}.producto_id`}
                                            control={control}
                                            rules={{ required: true }}
                                            render={({ field: { onChange, value } }) => (
                                                <SearchableSelect
                                                    options={products.map(p => ({
                                                        value: p.id,
                                                        label: p.nombre
                                                    }))}
                                                    value={value}
                                                    onChange={onChange}
                                                    placeholder="Selecciona un producto..."
                                                />
                                            )}
                                        />
                                    </div>
                                    <div style={{ width: '100px' }}>
                                        <label className="form-label-custom" style={{ fontSize: '13px' }}>Cant.</label>
                                        <input
                                            type="number"
                                            min="1"
                                            {...register(`items.${index}.cantidad`)}
                                            className="form-control-custom"
                                            style={{ textAlign: 'center' }}
                                        />
                                    </div>
                                    <div style={{ marginTop: '28px' }}>
                                        <button
                                            type="button"
                                            onClick={() => remove(index)}
                                            className="btn-icon"
                                            style={{ color: 'var(--danger-red)', border: 'none', background: 'none' }}
                                            title="Eliminar item"
                                        >
                                            <FiTrash2 size={20} />
                                        </button>
                                    </div>
                                </div>
                            ))}

                            <button
                                type="button"
                                className="btn-custom btn-secondary btn-sm"
                                onClick={() => append({ producto_id: '', cantidad: 1 })}
                            >
                                <FiPlus size={16} /> Agregar otro producto
                            </button>
                        </div>

                        {/* Sección 3: Mensaje */}
                        <div className="card-custom">
                            <div className="form-group-custom">
                                <label className="form-label-custom">Mensaje o Comentarios Adicionales</label>
                                <textarea
                                    {...register('comentarios')}
                                    className="form-control-custom"
                                    rows="3"
                                    placeholder="¿Necesitas algo más específico? Cuéntanos aquí."
                                />
                            </div>

                            <button
                                type="submit"
                                className="btn-custom btn-primary"
                                style={{ width: '100%', padding: '15px', fontSize: '18px', marginTop: '10px' }}
                                disabled={submitting}
                            >
                                {submitting ? 'Enviando...' : (
                                    <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                                        <FiSend /> Solicitar Cotización
                                    </span>
                                )}
                            </button>
                        </div>

                    </div>
                </form>

                {/* Footer CotizApp */}
                <div style={{
                    textAlign: 'center',
                    marginTop: '60px',
                    paddingTop: '30px',
                    borderTop: '1px solid var(--gray-200)',
                    color: 'var(--gray-400)',
                    fontSize: '14px'
                }}>
                    <p style={{ margin: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                        Powered by <span style={{ fontWeight: '600', color: 'var(--primary-orange)' }}>🧾 CotizApp</span>
                    </p>
                </div>
            </div >
        </div >
    );
};

export default PublicQuotation;

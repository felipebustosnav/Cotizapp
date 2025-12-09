import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { FiSave, FiArrowLeft, FiUser, FiMapPin, FiPhone, FiMail } from 'react-icons/fi';
import clientsService from '../../services/clients.service';

const ClientForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const isEditing = !!id;
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const { register, handleSubmit, formState: { errors }, reset, setValue } = useForm({
        defaultValues: {
            nombre: '',
            rut: '',
            email: '',
            telefono: '',
            direccion: ''
        }
    });

    useEffect(() => {
        if (isEditing) {
            loadClient();
        }
    }, [id]);

    const loadClient = async () => {
        try {
            setLoading(true);
            const client = await clientsService.getById(id);
            reset(client);
        } catch (err) {
            console.error('Error loading client:', err);
            setError('Error al cargar los datos del cliente');
        } finally {
            setLoading(false);
        }
    };

    const onSubmit = async (data) => {
        setLoading(true);
        setError('');

        // Formatear RUT antes de enviar
        if (data.rut) {
            data.rut = clientsService.formatRut(data.rut);
        }

        try {
            if (isEditing) {
                await clientsService.update(id, data);
            } else {
                await clientsService.create(data);
            }
            navigate('/clientes');
        } catch (err) {
            console.error('Error saving client:', err);
            // Extraer mensaje de error del backend si existe
            let msg = 'Error al guardar el cliente.';
            if (err.response?.data?.email) msg = 'El correo electrónico ya está registrado.';
            if (err.response?.data?.rut) msg = 'El RUT ya está registrado o es inválido.';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    const handleRutBlur = (e) => {
        const value = e.target.value;
        if (value) {
            const formatted = clientsService.formatRut(value);
            setValue('rut', formatted);
        }
    };

    if (loading && isEditing) {
        return <div className="loading-overlay"><div className="spinner"></div></div>;
    }

    return (
        <div className="container-custom">
            <div className="card-header-custom" style={{ marginTop: '20px', borderBottom: 'none' }}>
                <div>
                    <h2>{isEditing ? 'Editar Cliente' : 'Nuevo Cliente'}</h2>
                    <p className="text-muted">Información de contacto y facturación</p>
                </div>
                <button className="btn-custom btn-secondary" onClick={() => navigate('/clientes')}>
                    <FiArrowLeft size={20} /> Volver
                </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="card-custom" style={{ maxWidth: '800px', margin: '0 auto' }}>
                {error && <div className="alert-custom alert-danger" style={{ marginBottom: '20px' }}>{error}</div>}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>

                    <div className="form-group-custom">
                        <label className="form-label-custom">
                            <FiUser style={{ marginRight: '8px' }} /> Nombre Completo / Razón Social *
                        </label>
                        <input
                            {...register('nombre', { required: 'El nombre es obligatorio' })}
                            className="form-control-custom"
                            placeholder="Ej: Empresa Ltda. o Juan Pérez"
                        />
                        {errors.nombre && <span className="form-error">{errors.nombre.message}</span>}
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div className="form-group-custom">
                            <label className="form-label-custom">RUT</label>
                            <input
                                {...register('rut', {
                                    required: 'El RUT es obligatorio',
                                    validate: value => clientsService.validateRut(value) || 'RUT inválido'
                                })}
                                className="form-control-custom"
                                placeholder="12345678-9"
                                onBlur={handleRutBlur}
                            />
                            {errors.rut && <span className="form-error">{errors.rut.message}</span>}
                        </div>

                        <div className="form-group-custom">
                            <label className="form-label-custom">
                                <FiPhone style={{ marginRight: '8px' }} /> Teléfono
                            </label>
                            <input
                                {...register('telefono')}
                                className="form-control-custom"
                                placeholder="+56 9 1234 5678"
                            />
                        </div>
                    </div>

                    <div className="form-group-custom">
                        <label className="form-label-custom">
                            <FiMail style={{ marginRight: '8px' }} /> Correo Electrónico *
                        </label>
                        <input
                            type="email"
                            {...register('email', {
                                required: 'El email es obligatorio',
                                pattern: {
                                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                    message: 'Email inválido'
                                }
                            })}
                            className="form-control-custom"
                            placeholder="contacto@cliente.com"
                        />
                        {errors.email && <span className="form-error">{errors.email.message}</span>}
                    </div>

                    <div className="form-group-custom">
                        <label className="form-label-custom">
                            <FiMapPin style={{ marginRight: '8px' }} /> Dirección
                        </label>
                        <input
                            {...register('direccion')}
                            className="form-control-custom"
                            placeholder="Av. Principal 123, Ciudad"
                        />
                    </div>

                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '15px', marginTop: '30px', paddingTop: '20px', borderTop: '1px solid var(--gray-200)' }}>
                    <button type="button" className="btn-custom btn-secondary" onClick={() => navigate('/clientes')}>
                        Cancelar
                    </button>
                    <button type="submit" className="btn-custom btn-primary" disabled={loading}>
                        <FiSave size={20} />
                        {loading ? 'Guardando...' : 'Guardar Cliente'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ClientForm;

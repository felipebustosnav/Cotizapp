import React, { useState, useEffect } from 'react';
import { FiPlus, FiEdit2, FiTrash2, FiCheck, FiX, FiAlertCircle } from 'react-icons/fi';
import taxesService from '../../services/taxes.service';

const TaxManagement = () => {
    const [taxes, setTaxes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [editingTax, setEditingTax] = useState(null);
    const [formData, setFormData] = useState({
        nombre: '',
        porcentaje: '',
        activo: true
    });

    useEffect(() => {
        fetchTaxes();
    }, []);

    const fetchTaxes = async () => {
        try {
            setLoading(true);
            const data = await taxesService.getAll();
            // Handle both paginated and non-paginated responses
            const taxesArray = Array.isArray(data) ? data : (data.results || []);
            setTaxes(taxesArray);
        } catch (err) {
            console.error('Error fetching taxes:', err);
            setError('Error al cargar impuestos');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            if (editingTax) {
                await taxesService.update(editingTax.id, formData);
                setSuccess('Impuesto actualizado correctamente');
            } else {
                await taxesService.create(formData);
                setSuccess('Impuesto creado correctamente');
            }

            fetchTaxes();
            handleCancel();
        } catch (err) {
            console.error('Error saving tax:', err);
            setError(err.response?.data?.detail || 'Error al guardar impuesto');
        }
    };

    const handleEdit = (tax) => {
        setEditingTax(tax);
        setFormData({
            nombre: tax.nombre,
            porcentaje: tax.porcentaje,
            activo: tax.activo
        });
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de que deseas eliminar este impuesto?')) {
            return;
        }

        try {
            await taxesService.delete(id);
            setSuccess('Impuesto eliminado correctamente');
            fetchTaxes();
        } catch (err) {
            console.error('Error deleting tax:', err);
            setError('Error al eliminar impuesto');
        }
    };

    const handleToggleActive = async (tax) => {
        try {
            await taxesService.toggleActive(tax.id, !tax.activo);
            setSuccess(`Impuesto ${!tax.activo ? 'activado' : 'desactivado'} correctamente`);
            fetchTaxes();
        } catch (err) {
            console.error('Error toggling tax:', err);
            setError('Error al cambiar estado del impuesto');
        }
    };

    const handleCancel = () => {
        setShowForm(false);
        setEditingTax(null);
        setFormData({ nombre: '', porcentaje: '', activo: true });
    };

    if (loading && taxes.length === 0) {
        return <div className="loading-overlay"><div className="spinner"></div></div>;
    }

    return (
        <div className="container-custom">
            <div className="card-header-custom" style={{ marginTop: '20px', borderBottom: 'none' }}>
                <div>
                    <h2>Gestión de Impuestos</h2>
                    <p className="text-muted">Administra los impuestos predefinidos de tu empresa</p>
                </div>
                <button
                    className="btn-custom btn-primary"
                    onClick={() => setShowForm(true)}
                    disabled={showForm}
                >
                    <FiPlus size={20} /> Nuevo Impuesto
                </button>
            </div>

            {error && (
                <div className="alert-custom alert-danger">
                    <FiAlertCircle size={20} />
                    <span>{error}</span>
                </div>
            )}

            {success && (
                <div className="alert-custom alert-success">
                    <FiCheck size={20} />
                    <span>{success}</span>
                </div>
            )}

            {/* Formulario */}
            {showForm && (
                <div className="card-custom" style={{ marginBottom: '20px' }}>
                    <h3>{editingTax ? 'Editar Impuesto' : 'Nuevo Impuesto'}</h3>
                    <form onSubmit={handleSubmit}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                            <div className="form-group-custom">
                                <label className="form-label-custom">Nombre *</label>
                                <input
                                    type="text"
                                    className="form-control-custom"
                                    value={formData.nombre}
                                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                                    required
                                    placeholder="Ej: IVA, Impuesto Específico"
                                />
                            </div>

                            <div className="form-group-custom">
                                <label className="form-label-custom">Porcentaje (%) *</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    max="100"
                                    className="form-control-custom"
                                    value={formData.porcentaje}
                                    onChange={(e) => setFormData({ ...formData, porcentaje: e.target.value })}
                                    required
                                    placeholder="Ej: 19.00"
                                />
                            </div>
                        </div>

                        <div className="form-group-custom">
                            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={formData.activo}
                                    onChange={(e) => setFormData({ ...formData, activo: e.target.checked })}
                                />
                                <span>Activo</span>
                            </label>
                        </div>

                        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
                            <button type="button" className="btn-custom btn-secondary" onClick={handleCancel}>
                                <FiX size={18} /> Cancelar
                            </button>
                            <button type="submit" className="btn-custom btn-primary">
                                <FiCheck size={18} /> {editingTax ? 'Actualizar' : 'Crear'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Tabla */}
            <div className="card-custom">
                {taxes.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                        <p className="text-muted">No hay impuestos registrados</p>
                    </div>
                ) : (
                    <div className="table-responsive">
                        <table className="table-custom">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Porcentaje</th>
                                    <th>Estado</th>
                                    <th>Última Actualización</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {taxes.map((tax) => (
                                    <tr key={tax.id}>
                                        <td style={{ fontWeight: 'bold' }}>{tax.nombre}</td>
                                        <td>{tax.porcentaje}%</td>
                                        <td>
                                            <span
                                                className={`badge ${tax.activo ? 'badge-success' : 'badge-secondary'}`}
                                                style={{ cursor: 'pointer' }}
                                                onClick={() => handleToggleActive(tax)}
                                            >
                                                {tax.activo ? 'Activo' : 'Inactivo'}
                                            </span>
                                        </td>
                                        <td>
                                            {new Date(tax.fecha_actualizacion).toLocaleDateString('es-CL')}
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '10px' }}>
                                                <button
                                                    type="button"
                                                    className="btn-icon"
                                                    onClick={() => handleEdit(tax)}
                                                    title="Editar"
                                                    style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--primary-orange)' }}
                                                >
                                                    <FiEdit2 size={18} style={{ pointerEvents: 'none' }} />
                                                </button>
                                                <button
                                                    type="button"
                                                    className="btn-icon"
                                                    onClick={() => handleDelete(tax.id)}
                                                    title="Eliminar"
                                                    style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--danger-red)' }}
                                                >
                                                    <FiTrash2 size={18} style={{ pointerEvents: 'none' }} />
                                                </button>
                                            </div>
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

export default TaxManagement;

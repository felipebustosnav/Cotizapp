import React, { useState } from 'react';
import { FiX, FiCheck, FiAlertCircle } from 'react-icons/fi';
import taxesService from '../services/taxes.service';

const TaxQuickCreate = ({ isOpen, onClose, onTaxCreated }) => {
    const [formData, setFormData] = useState({
        nombre: '',
        porcentaje: '',
        activo: true
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const newTax = await taxesService.create(formData);
            onTaxCreated(newTax);
            setFormData({ nombre: '', porcentaje: '', activo: true });
            onClose();
        } catch (err) {
            console.error('Error creating tax:', err);
            setError(err.response?.data?.detail || 'Error al crear impuesto');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0,0,0,0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 9999
            }}
            onClick={onClose}
        >
            <div
                className="card-custom"
                style={{
                    width: '90%',
                    maxWidth: '500px',
                    margin: '20px'
                }}
                onClick={(e) => e.stopPropagation()}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h3>Crear Nuevo Impuesto</h3>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: '5px'
                        }}
                    >
                        <FiX size={24} />
                    </button>
                </div>

                {error && (
                    <div className="alert-custom alert-danger" style={{ marginBottom: '15px' }}>
                        <FiAlertCircle size={20} />
                        <span>{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit}>
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
                        <button type="button" className="btn-custom btn-secondary" onClick={onClose}>
                            Cancelar
                        </button>
                        <button type="submit" className="btn-custom btn-primary" disabled={loading}>
                            <FiCheck size={18} /> {loading ? 'Creando...' : 'Crear Impuesto'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TaxQuickCreate;

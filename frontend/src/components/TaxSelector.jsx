import React, { useState, useEffect } from 'react';
import { FiX, FiChevronDown, FiPlus } from 'react-icons/fi';
import taxesService from '../services/taxes.service';

const TaxSelector = ({ selectedTaxes = [], onChange, onQuickCreate }) => {
    const [availableTaxes, setAvailableTaxes] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchActiveTaxes();
    }, []);

    // Expose refresh function to parent
    useEffect(() => {
        window.refreshTaxSelector = fetchActiveTaxes;
    }, []);

    const fetchActiveTaxes = async () => {
        try {
            setLoading(true);
            const data = await taxesService.getActive();
            setAvailableTaxes(data);
        } catch (err) {
            console.error('Error loading taxes:', err);
        } finally {
            setLoading(false);
        }
    };

    const filteredTaxes = availableTaxes.filter(tax =>
        tax.nombre.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Filter out already selected taxes to prevent duplicates
    const availableOptions = filteredTaxes.filter(
        tax => !selectedTaxes.some(selected => selected.id === tax.id)
    );

    const handleSelectTax = (tax) => {
        onChange([...selectedTaxes, tax]);
        setSearchTerm('');
        setIsOpen(false);
    };

    const handleRemoveTax = (taxId) => {
        onChange(selectedTaxes.filter(t => t.id !== taxId));
    };

    const totalPercentage = selectedTaxes.reduce((sum, tax) => sum + parseFloat(tax.porcentaje || 0), 0);

    return (
        <div className="form-group-custom">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label className="form-label-custom">
                    Impuestos
                    {selectedTaxes.length > 0 && (
                        <span style={{ marginLeft: '10px', color: '#ff6b35', fontWeight: 'bold' }}>
                            (Total: {totalPercentage.toFixed(2)}%)
                        </span>
                    )}
                </label>
                {onQuickCreate && (
                    <button
                        type="button"
                        className="btn-custom btn-sm btn-secondary"
                        onClick={onQuickCreate}
                        style={{ fontSize: '0.85rem', padding: '4px 12px' }}
                    >
                        <FiPlus size={14} /> Crear Impuesto
                    </button>
                )}
            </div>

            {/* Dropdown de búsqueda */}
            <div style={{ position: 'relative' }}>
                <div
                    className="form-control-custom"
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        cursor: 'pointer',
                        backgroundColor: 'white'
                    }}
                    onClick={() => setIsOpen(!isOpen)}
                >
                    <input
                        type="text"
                        placeholder="Buscar o seleccionar impuesto..."
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setIsOpen(true);
                        }}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                            border: 'none',
                            outline: 'none',
                            flex: 1,
                            backgroundColor: 'transparent'
                        }}
                    />
                    <FiChevronDown size={20} color="var(--gray-500)" />
                </div>

                {/* Dropdown menu */}
                {isOpen && (
                    <div
                        style={{
                            position: 'absolute',
                            top: '100%',
                            left: 0,
                            right: 0,
                            backgroundColor: 'white',
                            border: '1px solid var(--gray-300)',
                            borderRadius: '8px',
                            marginTop: '4px',
                            maxHeight: '200px',
                            overflowY: 'auto',
                            zIndex: 1000,
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                        }}
                    >
                        {loading ? (
                            <div style={{ padding: '12px', textAlign: 'center', color: 'var(--gray-500)' }}>
                                Cargando...
                            </div>
                        ) : availableOptions.length === 0 ? (
                            <div style={{ padding: '12px', textAlign: 'center', color: 'var(--gray-500)' }}>
                                {searchTerm ? 'No se encontraron impuestos' : 'Todos los impuestos ya están seleccionados'}
                            </div>
                        ) : (
                            availableOptions.map(tax => (
                                <div
                                    key={tax.id}
                                    onClick={() => handleSelectTax(tax)}
                                    style={{
                                        padding: '10px 12px',
                                        cursor: 'pointer',
                                        borderBottom: '1px solid var(--gray-200)',
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center'
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--gray-100)'}
                                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                                >
                                    <span>{tax.nombre}</span>
                                    <span style={{ color: '#ff6b35', fontWeight: 'bold' }}>
                                        {tax.porcentaje}%
                                    </span>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            {/* Chips de impuestos seleccionados */}
            {selectedTaxes && selectedTaxes.length > 0 && (
                <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '8px',
                    marginTop: '10px',
                    padding: '10px',
                    border: '1px dashed #ccc',
                    borderRadius: '4px'
                }}>
                    {selectedTaxes.map(tax => (
                        <div
                            key={tax.id}
                            style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '6px 12px',
                                backgroundColor: '#ff6b35',
                                color: 'white',
                                borderRadius: '20px',
                                fontSize: '14px',
                                fontWeight: '500'
                            }}
                        >
                            <span>{tax.nombre} ({tax.porcentaje}%)</span>
                            <FiX
                                size={16}
                                style={{ cursor: 'pointer' }}
                                onClick={() => handleRemoveTax(tax.id)}
                            />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default TaxSelector;

import React, { useState, useEffect, useRef } from 'react';
import { FiChevronDown, FiX } from 'react-icons/fi';

const SearchableSelect = ({ options, value, onChange, placeholder = "Seleccionar...", disabled = false }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const wrapperRef = useRef(null);

    // Encontrar la opción seleccionada actualmente
    const selectedOption = options.find(opt => opt.value === value);

    // Sincronizar el término de búsqueda con el valor seleccionado cuando cambia externamente
    useEffect(() => {
        if (selectedOption) {
            setSearchTerm(selectedOption.label);
        } else {
            setSearchTerm('');
        }
    }, [selectedOption]);

    // Cerrar al hacer clic fuera
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
                // Si cerramos y no hay match exacto con el texto, revertir al valor guardado
                if (selectedOption) {
                    setSearchTerm(selectedOption.label);
                } else if (!value) {
                    setSearchTerm('');
                }
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [selectedOption, value]);

    // Filtrar opciones
    const filteredOptions = options.filter(opt =>
        opt.label.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleSelect = (option) => {
        onChange(option.value);
        setSearchTerm(option.label);
        setIsOpen(false);
    };

    const handleClear = (e) => {
        e.stopPropagation();
        onChange('');
        setSearchTerm('');
        setIsOpen(false);
    };

    return (
        <div ref={wrapperRef} style={{ position: 'relative', width: '100%' }}>
            <div
                className="form-control-custom"
                onClick={() => !disabled && setIsOpen(!isOpen)}
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: disabled ? 'default' : 'pointer',
                    backgroundColor: disabled ? 'var(--gray-100)' : 'white',
                    padding: '8px 12px',
                    border: '1px solid var(--gray-300)',
                    borderRadius: '8px'
                }}
            >
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                        setSearchTerm(e.target.value);
                        if (!isOpen) setIsOpen(true);
                        // Si borra todo, limpiar valor
                        if (e.target.value === '') onChange('');
                    }}
                    placeholder={placeholder}
                    disabled={disabled}
                    style={{
                        border: 'none',
                        outline: 'none',
                        width: '100%',
                        backgroundColor: 'transparent',
                        fontSize: '14px',
                        color: 'var(--text-dark)'
                    }}
                />
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    {value && !disabled && (
                        <FiX
                            size={16}
                            style={{ color: 'var(--gray-500)', cursor: 'pointer' }}
                            onClick={handleClear}
                        />
                    )}
                    <FiChevronDown size={16} style={{ color: 'var(--gray-500)' }} />
                </div>
            </div>

            {isOpen && !disabled && (
                <ul style={{
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
                    zIndex: 9999,
                    listStyle: 'none',
                    padding: 0,
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}>
                    {filteredOptions.length > 0 ? (
                        filteredOptions.map((opt) => (
                            <li
                                key={opt.value}
                                onClick={() => handleSelect(opt)}
                                style={{
                                    padding: '10px 12px',
                                    cursor: 'pointer',
                                    borderBottom: '1px solid var(--gray-100)',
                                    backgroundColor: opt.value === value ? 'var(--orange-light)' : 'white',
                                    color: opt.value === value ? 'var(--primary-orange)' : 'var(--text-dark)',
                                    fontSize: '14px'
                                }}
                                onMouseEnter={(e) => e.target.style.backgroundColor = 'var(--gray-50)'}
                                onMouseLeave={(e) => e.target.style.backgroundColor = opt.value === value ? 'var(--orange-light)' : 'white'}
                            >
                                {opt.label}
                            </li>
                        ))
                    ) : (
                        <li style={{ padding: '10px 12px', color: 'var(--gray-500)', fontSize: '14px' }}>
                            No hay resultados
                        </li>
                    )}
                </ul>
            )}
        </div>
    );
};

export default SearchableSelect;

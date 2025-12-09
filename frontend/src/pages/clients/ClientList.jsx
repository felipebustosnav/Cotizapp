import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiPlus, FiSearch, FiEdit2, FiTrash2, FiUsers, FiMail, FiPhone } from 'react-icons/fi';
import clientsService from '../../services/clients.service';

const ClientList = () => {
    const navigate = useNavigate();
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchClients();
    }, []);

    const fetchClients = async () => {
        try {
            setLoading(true);
            const data = await clientsService.getAll();
            setClients(data.results || data);
        } catch (err) {
            console.error('Error fetching clients:', err);
            setError('Error al cargar clientes');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('¿Estás seguro de que deseas eliminar este cliente?')) {
            try {
                await clientsService.delete(id);
                setClients(clients.filter(c => c.id !== id));
            } catch (err) {
                console.error('Error deleting client:', err);
                alert('No se pudo eliminar el cliente. Puede que tenga cotizaciones asociadas.');
            }
        }
    };

    const filteredClients = clients.filter(client =>
        client.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.rut?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="container-custom">
            <div className="card-header-custom" style={{ marginTop: '20px', borderBottom: 'none' }}>
                <div>
                    <h2>Gestión de Clientes</h2>
                    <p className="text-muted">Administra tu base de datos de clientes</p>
                </div>
                <button className="btn-custom btn-primary" onClick={() => navigate('/clientes/nuevo')}>
                    <FiPlus size={20} /> Nuevo Cliente
                </button>
            </div>

            {error && <div className="alert-custom alert-danger">{error}</div>}

            <div className="card-custom">
                <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
                    <div className="header-search" style={{ flex: 1 }}>
                        <FiSearch size={20} />
                        <input
                            type="text"
                            placeholder="Buscar por nombre, email o RUT..."
                            className="header-search-input"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                {filteredClients.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                        <FiUsers size={48} color="var(--gray-400)" />
                        <p className="text-muted" style={{ marginTop: '10px' }}>No se encontraron clientes</p>
                    </div>
                ) : (
                    <div className="table-responsive">
                        <table className="table-custom">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>RUT</th>
                                    <th>Contacto</th>
                                    <th>Dirección</th>
                                    <th>Fecha Registro</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredClients.map((client) => (
                                    <tr key={client.id}>
                                        <td>
                                            <div style={{ fontWeight: '500' }}>{client.nombre?.trim() || <span style={{ color: 'var(--gray-400)', fontStyle: 'italic' }}>(Sin Nombre)</span>}</div>
                                        </td>
                                        <td>{client.rut_formateado || client.rut || '-'}</td>
                                        <td>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                                {client.email && (
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '13px' }}>
                                                        <FiMail size={12} color="var(--gray-600)" /> {client.email}
                                                    </div>
                                                )}
                                                {client.telefono && (
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '13px' }}>
                                                        <FiPhone size={12} color="var(--gray-600)" /> {client.telefono}
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td><small>{client.direccion || '-'}</small></td>
                                        <td>{client.fecha_registro ? new Date(client.fecha_registro).toLocaleDateString('es-CL') : '-'}</td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '10px' }}>
                                                <button
                                                    type="button"
                                                    className="btn-icon"
                                                    onClick={() => navigate(`/clientes/editar/${client.id}`)}
                                                    title="Editar"
                                                    style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--primary-orange)' }}
                                                >
                                                    <FiEdit2 size={18} style={{ pointerEvents: 'none' }} />
                                                </button>
                                                <button
                                                    type="button"
                                                    className="btn-icon"
                                                    onClick={() => handleDelete(client.id)}
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

export default ClientList;

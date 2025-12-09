import React, { useState, useEffect } from 'react';
import { Modal, Form, Alert, Badge, Spinner } from 'react-bootstrap';
import {
    FiPlus,
    FiSearch,
    FiTrash2,
    FiUser,
    FiMail,
    FiShield,
    FiKey,
    FiCalendar,
    FiUserX,
    FiAlertTriangle
} from 'react-icons/fi';
import api from '../../services/api';

const Employees = () => {
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: ''
    });
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [submissionLoading, setSubmissionLoading] = useState(false);

    useEffect(() => {
        fetchEmployees();
    }, []);

    const fetchEmployees = async () => {
        try {
            const response = await api.get('/usuarios/');
            // Manejar paginación de DRF (results) o lista directa
            setEmployees(response.data.results || response.data);
            setLoading(false);
        } catch (err) {
            console.error("Error fetching employees:", err);
            setError("No se pudo cargar la lista de empleados.");
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmissionLoading(true);
        setError(null);
        setSuccess(null);

        try {
            await api.post('/usuarios/', formData);
            setSuccess("Empleado creado exitosamente. Se han enviado las credenciales a su correo.");
            setFormData({ first_name: '', last_name: '', email: '' });
            setShowModal(false);
            fetchEmployees();
        } catch (err) {
            console.error(err);
            let errorMsg = "Error al crear empleado. Verifique los datos.";
            if (err.response && err.response.data) {
                // Si es un objeto con errores de campo (ej: { email: ["Ya existe"] })
                const data = err.response.data;
                if (data.email) errorMsg = `Error en Email: ${data.email[0]}`;
                else if (data.first_name) errorMsg = `Error en Nombre: ${data.first_name[0]}`;
                else if (data.detail) errorMsg = data.detail;
                else {
                    // Unir primer error de cada campo
                    errorMsg = Object.values(data).flat()[0] || errorMsg;
                }
            }
            setError(errorMsg);
        } finally {
            setSubmissionLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm("¿Estás seguro de desactivar este usuario?")) {
            try {
                await api.delete(`/usuarios/${id}/`);
                fetchEmployees();
            } catch (err) {
                alert("Error al desactivar usuario.");
            }
        }
    };

    const handleResetPassword = async (id) => {
        if (window.confirm("¿Estás seguro de resetear la contraseña de este usuario? Se generará una nueva y se enviará por correo.")) {
            try {
                await api.post(`/usuarios/${id}/reset_password/`);
                setSuccess("Contraseña reseteada exitosamente. Correo enviado.");
                setTimeout(() => setSuccess(null), 3000);
            } catch (err) {
                console.error(err);
                setError(err.response?.data?.error || "Error al resetear contraseña.");
            }
        }
    };

    // Filtrado local
    const filteredEmployees = employees.filter(emp =>
        emp.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="container-custom">
            <div className="card-header-custom" style={{ marginTop: '20px', borderBottom: 'none' }}>
                <div>
                    <h2>Gestión de Empleados</h2>
                    <p className="text-muted">Administra el acceso y roles de los miembros de tu equipo</p>
                </div>
                <button className="btn-custom btn-primary" onClick={() => setShowModal(true)}>
                    <FiPlus size={20} /> Nuevo Empleado
                </button>
            </div>

            {success && <Alert variant="success" onClose={() => setSuccess(null)} dismissible>{success}</Alert>}
            {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}

            <div className="card-custom">
                {/* Search Header */}
                <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
                    <div className="header-search" style={{ flex: 1 }}>
                        <FiSearch size={20} />
                        <input
                            type="text"
                            placeholder="Buscar por nombre o email..."
                            className="header-search-input"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                {filteredEmployees.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                        <FiUser size={48} color="var(--gray-400)" />
                        <p className="text-muted" style={{ marginTop: '10px' }}>No se encontraron empleados</p>
                    </div>
                ) : (
                    <div className="table-responsive">
                        <table className="table-custom">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Email</th>
                                    <th>Rol</th>
                                    <th>Estado</th>
                                    <th>Fecha Registro</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredEmployees.map(emp => (
                                    <tr key={emp.id}>
                                        <td>
                                            <div style={{ fontWeight: '500' }}>{emp.first_name} {emp.last_name}</div>
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '13px' }}>
                                                <FiMail size={12} color="var(--gray-600)" /> {emp.email}
                                            </div>
                                        </td>
                                        <td>
                                            <Badge bg={emp.rol === 'ADMIN' ? 'info' : 'secondary'} style={{ fontWeight: 500 }}>
                                                {emp.rol === 'ADMIN' && <FiShield className="me-1" />}
                                                {emp.rol}
                                            </Badge>
                                        </td>
                                        <td>
                                            <Badge bg={emp.activo ? 'success' : 'danger'}>
                                                {emp.activo ? 'Activo' : 'Inactivo'}
                                            </Badge>
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                <FiCalendar size={12} color="var(--gray-400)" />
                                                {emp.fecha_creacion ? new Date(emp.fecha_creacion).toLocaleDateString() : '-'}
                                            </div>
                                        </td>
                                        <td>
                                            {emp.rol !== 'ADMIN' && (
                                                <div style={{ display: 'flex', gap: '10px' }}>
                                                    <button
                                                        className="btn-icon"
                                                        onClick={() => handleResetPassword(emp.id)}
                                                        disabled={!emp.activo}
                                                        title="Resetear Contraseña"
                                                        style={{ color: 'var(--warning-yellow)', border: 'none', background: 'none' }}
                                                    >
                                                        <FiKey size={18} />
                                                    </button>

                                                    <button
                                                        className="btn-icon"
                                                        onClick={() => handleDelete(emp.id)}
                                                        disabled={!emp.activo}
                                                        title="Desactivar Usuario"
                                                        style={{ color: 'var(--danger-red)', border: 'none', background: 'none' }}
                                                    >
                                                        <FiUserX size={18} />
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <Modal show={showModal} onHide={() => setShowModal(false)} centered>
                <Modal.Header closeButton style={{ borderBottom: 'none', padding: '20px 24px' }}>
                    <Modal.Title style={{ fontWeight: 600 }}>Nuevo Empleado</Modal.Title>
                </Modal.Header>
                <Form onSubmit={handleSubmit}>
                    <Modal.Body style={{ padding: '0 24px 20px' }}>
                        <Alert variant="info" className="small d-flex align-items-center">
                            <FiAlertTriangle className="me-2" size={16} />
                            <div>
                                El sistema generará una <strong>contraseña segura</strong> y la enviará al correo del empleado.
                            </div>
                        </Alert>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Nombre</Form.Label>
                            <Form.Control
                                type="text"
                                name="first_name"
                                required
                                value={formData.first_name}
                                onChange={handleInputChange}
                                className="form-control-custom"
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Apellido</Form.Label>
                            <Form.Control
                                type="text"
                                name="last_name"
                                required
                                value={formData.last_name}
                                onChange={handleInputChange}
                                className="form-control-custom"
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Correo Electrónico</Form.Label>
                            <Form.Control
                                type="email"
                                name="email"
                                required
                                value={formData.email}
                                onChange={handleInputChange}
                                className="form-control-custom"
                            />
                        </Form.Group>
                    </Modal.Body>
                    <Modal.Footer style={{ borderTop: 'none', padding: '0 24px 24px' }}>
                        <button type="button" className="btn-custom btn-secondary" onClick={() => setShowModal(false)}>
                            Cancelar
                        </button>
                        <button type="submit" className="btn-custom btn-primary" disabled={submissionLoading}>
                            {submissionLoading ? <Spinner size="sm" animation="border" /> : 'Crear Empleado'}
                        </button>
                    </Modal.Footer>
                </Form>
            </Modal>
        </div>
    );
};

export default Employees;

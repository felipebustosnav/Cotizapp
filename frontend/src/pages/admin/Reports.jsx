import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Spinner, Alert } from 'react-bootstrap';
import {
    BarChart, Bar, Line, ComposedChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import api from '../../services/api';
import './Reports.css'; // We'll create this minimal CSS

const Reports = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const response = await api.get('/reportes/');
            setData(response.data);
            setLoading(false);
        } catch (err) {
            console.error("Error cargando reportes:", err);
            setError("No se pudieron cargar los datos del reporte.");
            setLoading(false);
        }
    };

    const handleDownloadPDF = async () => {
        try {
            const response = await api.get('/reportes/download_pdf/', { responseType: 'blob' });
            // Crear URL del blob y descargar
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const dateStr = new Date().toISOString().split('T')[0].replace(/-/g, '');
            link.setAttribute('download', `Reporte_Ejecutivo_${dateStr}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Error al descargar PDF:", err);
            // Intentar leer el error si es un JSON blob
            if (err.response && err.response.data instanceof Blob) {
                const text = await err.response.data.text();
                try {
                    const errorJson = JSON.parse(text);
                    console.error("Error details:", errorJson);
                    alert(`Error: ${errorJson.error || 'Error al descargar el reporte'}`);
                } catch (e) {
                    alert("Error al descargar el reporte.");
                }
            } else {
                alert("Error al conectar con el servidor para descargar el PDF.");
            }
        }
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
                <Spinner animation="border" variant="primary" />
            </div>
        );
    }

    if (error) {
        return <Alert variant="danger">{error}</Alert>;
    }

    if (!data) return null;

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

    return (
        <div className="container-fluid p-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="text-primary fw-bold">Reportes de Análisis</h2>
                <Button variant="outline-danger" onClick={handleDownloadPDF}>
                    <i className="bi bi-file-earmark-pdf me-2"></i>Descargar PDF
                </Button>
            </div>
            {data.automatizacion && (
                <>
                    <h4 className="text-secondary fw-bold mb-3 mt-4">Análisis mensajería instantánea</h4>
                    <Row className="mb-4">
                        <Col md={3}>
                            <Card className="shadow-sm border-0 h-100" style={{ borderLeft: '4px solid #8b5cf6' }}>
                                <Card.Body>
                                    <h6 className="text-muted text-uppercase small fw-bold">Ingresos Recuperados</h6>
                                    <h3 className="fw-bold fs-4 text-dark">
                                        ${(data.automatizacion.ingresos_recuperados || 0).toLocaleString('es-CL', { maximumFractionDigits: 0 })}
                                    </h3>
                                    <small className="text-success">
                                        <i className="bi bi-graph-up-arrow me-1"></i>
                                        Ventas cerradas vía bot
                                    </small>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col md={3}>
                            <Card className="shadow-sm border-0 h-100" style={{ borderLeft: '4px solid #ec4899' }}>
                                <Card.Body>
                                    <h6 className="text-muted text-uppercase small fw-bold">Tasa de Éxito</h6>
                                    <h3 className="fw-bold fs-4 text-dark">{data.automatizacion.tasa_conversion}%</h3>
                                    <div className="d-flex justify-content-between small text-muted mt-1">
                                        <span><i className="bi bi-check-circle text-success"></i> {data.automatizacion.ofertas_aceptadas} Aceptadas</span>
                                        <span><i className="bi bi-x-circle text-danger"></i> {data.automatizacion.ofertas_rechazadas} Rechazadas</span>
                                    </div>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col md={3}>
                            <Card className="shadow-sm border-0 h-100" style={{ borderLeft: '4px solid #f59e0b' }}>
                                <Card.Body>
                                    <h6 className="text-muted text-uppercase small fw-bold">Volumen Total</h6>
                                    <h3 className="fw-bold fs-4 text-dark">{data.automatizacion.total_ofertas}</h3>
                                    <small className="text-muted">
                                        Ofertas enviadas
                                    </small>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col md={3}>
                            <Card className="shadow-sm border-0 h-100" style={{ borderLeft: '4px solid #10b981' }}>
                                <Card.Body>
                                    <h6 className="text-muted text-uppercase small fw-bold">Promedio Descuento</h6>
                                    <h3 className="fw-bold fs-4 text-dark">
                                        ${(data.automatizacion.promedio_descuento || 0).toLocaleString('es-CL', { maximumFractionDigits: 0 })}
                                    </h3>
                                    <small className="text-muted">
                                        Dinero ahorrado/cliente
                                    </small>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Row>
                        <Col lg={6} className="mb-4">
                            <Card className="shadow-sm border-0 h-100">
                                <Card.Header className="bg-white border-0 py-3">
                                    <h5 className="mb-0 fw-bold">Efectividad por % de Descuento</h5>
                                </Card.Header>
                                <Card.Body>
                                    <div style={{ width: '100%', height: '300px' }}>
                                        <ResponsiveContainer>
                                            <BarChart
                                                data={data.automatizacion.eficiencia_por_descuento}
                                                margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                                            >
                                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                                <XAxis dataKey="porcentaje" label={{ value: '% Descuento', position: 'insideBottom', offset: -10 }} />
                                                <YAxis label={{ value: 'Tasa Éxito (%)', angle: -90, position: 'insideLeft' }} />
                                                <Tooltip formatter={(value, name) => [name === 'tasa' ? `${value}%` : value, name === 'tasa' ? 'Tasa Éxito' : name]} />
                                                <Legend verticalAlign="top" />
                                                <Bar dataKey="tasa" name="Tasa Éxito (%)" fill="#8884d8" radius={[4, 4, 0, 0]}>
                                                    {
                                                        data.automatizacion.eficiencia_por_descuento.map((entry, index) => (
                                                            <Cell key={`cell-${index}`} fill={entry.tasa > 50 ? '#22c55e' : '#8884d8'} />
                                                        ))
                                                    }
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                    <p className="text-center text-muted small mt-2">
                                        Muestra qué porcentaje de descuento logra mayor conversión.
                                    </p>
                                </Card.Body>
                            </Card>
                        </Col>

                        <Col lg={6} className="mb-4">
                            <Card className="shadow-sm border-0 h-100">
                                <Card.Header className="bg-white border-0 py-3">
                                    <h5 className="mb-0 fw-bold">Estado de Ofertas</h5>
                                </Card.Header>
                                <Card.Body>
                                    <div style={{ width: '100%', height: '300px' }}>
                                        <ResponsiveContainer>
                                            <PieChart>
                                                <Pie
                                                    data={data.automatizacion.estado_ofertas}
                                                    cx="50%"
                                                    cy="50%"
                                                    innerRadius={60}
                                                    outerRadius={100}
                                                    paddingAngle={5}
                                                    dataKey="cantidad"
                                                    nameKey="nombre"
                                                >
                                                    {data.automatizacion.estado_ofertas.map((entry, index) => {
                                                        let color = '#999';
                                                        if (entry.nombre === 'ACEPTADA') color = '#22c55e'; // Green
                                                        if (entry.nombre === 'RECHAZADA') color = '#ef4444'; // Red
                                                        if (entry.nombre === 'VENCIDA') color = '#f59e0b';   // Amber
                                                        if (entry.nombre === 'ACTIVA') color = '#3b82f6';    // Blue
                                                        if (entry.nombre === 'PENDIENTE') color = '#64748b'; // Slate

                                                        return <Cell key={`cell-${index}`} fill={color} />;
                                                    })}
                                                </Pie>
                                                <Tooltip />
                                                <Legend layout="vertical" verticalAlign="middle" align="right" />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </div>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </>
            )}

            <h4 className="text-secondary fw-bold mb-3 mt-4">Análisis de cotizaciones</h4>
            {/* Resumen Cards */}
            <Row className="mb-4">
                <Col md={4}>
                    <Card className="shadow-sm border-0 h-100 bg-primary text-white">
                        <Card.Body>
                            <h6 className="opacity-75">Total Cotizaciones</h6>
                            <h3 className="fw-bold display-6">{data.resumen.total_cotizaciones}</h3>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={4}>
                    <Card className="shadow-sm border-0 h-100 bg-success text-white">
                        <Card.Body>
                            <h6 className="opacity-75">Tasa de Aprobación</h6>
                            <h3 className="fw-bold display-6">{data.resumen.tasa_aprobacion}%</h3>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={4}>
                    <Card className="shadow-sm border-0 h-100 bg-info text-white">
                        <Card.Body>
                            <h6 className="opacity-75">Monto Total Aprobado</h6>
                            <h3 className="fw-bold display-6">${data.resumen.monto_total_aprobado.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</h3>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <Row>
                {/* Gráfico de Ventas Mensuales */}
                <Col lg={8} className="mb-4">
                    <Card className="shadow-sm border-0 h-100">
                        <Card.Header className="bg-white border-0 py-3">
                            <h5 className="mb-0 fw-bold">Ventas Aprobadas por Mes</h5>
                        </Card.Header>
                        <Card.Body style={{ height: '400px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart
                                    data={data.ventas_mensuales}
                                    margin={{ top: 20, right: 30, left: 40, bottom: 5 }} // Increased margin here too just in case
                                >
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="mes" />
                                    <YAxis yAxisId="left" orientation="left" stroke="#8884d8" label={{ value: 'Monto ($)', angle: -90, position: 'insideLeft' }} />
                                    <YAxis yAxisId="right" orientation="right" stroke="#ff7300" label={{ value: 'Cantidad', angle: 90, position: 'insideRight' }} />
                                    <Tooltip formatter={(value) => value.toLocaleString('es-CL')} />
                                    <Legend />
                                    <Bar yAxisId="left" dataKey="total" name="Monto ($)" fill="#8884d8" barSize={30} radius={[4, 4, 0, 0]} />
                                    <Line yAxisId="right" type="monotone" dataKey="cantidad" name="Cantidad" stroke="#ff7300" strokeWidth={3} dot={{ r: 5 }} />
                                </ComposedChart>
                            </ResponsiveContainer>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default Reports;

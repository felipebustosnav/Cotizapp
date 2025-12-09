import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiPlus, FiSearch, FiEdit2, FiTrash2, FiPackage } from 'react-icons/fi';
import productsService from '../../services/products.service';
import { useAuth } from '../../context/AuthContext';

const ProductList = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            setLoading(true);
            const data = await productsService.getAll();
            setProducts(data.results || data);
        } catch (err) {
            console.error('Error fetching products:', err);
            setError('Error al cargar productos');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('¿Estás seguro de que deseas eliminar este producto?')) {
            try {
                await productsService.delete(id);
                setProducts(products.filter(p => p.id !== id));
            } catch (err) {
                console.error('Error deleting product:', err);
                alert('No se pudo eliminar el producto. Puede que esté en uso en alguna cotización.');
            }
        }
    };

    const filteredProducts = products.filter(product =>
        product.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.marca?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.sku?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(amount);
    };

    if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

    return (
        <div className="container-custom">
            <div className="card-header-custom" style={{ marginTop: '20px', borderBottom: 'none' }}>
                <div>
                    <h2>Gestión de Productos</h2>
                    <p className="text-muted">Administra tu catálogo de productos y servicios</p>
                </div>
                <button className="btn-custom btn-primary" onClick={() => navigate('/productos/nuevo')}>
                    <FiPlus size={20} /> Nuevo Producto
                </button>
            </div>

            {error && <div className="alert-custom alert-danger">{error}</div>}

            <div className="card-custom">
                <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
                    <div className="header-search" style={{ flex: 1 }}>
                        <FiSearch size={20} />
                        <input
                            type="text"
                            placeholder="Buscar por nombre, SKU o marca..."
                            className="header-search-input"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                {filteredProducts.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                        <FiPackage size={48} color="var(--gray-400)" />
                        <p className="text-muted" style={{ marginTop: '10px' }}>No se encontraron productos</p>
                    </div>
                ) : (
                    <div className="table-responsive">
                        <table className="table-custom">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Marca / Sku</th>
                                    <th>Tipo</th>
                                    <th>Precio Neto</th>
                                    <th>Impuesto</th>
                                    <th>Precio Final</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredProducts.map((product) => (
                                    <tr key={product.id}>
                                        <td>
                                            <div style={{ fontWeight: '500' }}>{product.nombre}</div>
                                            {product.descripcion && <small className="text-muted">{product.descripcion.substring(0, 30)}...</small>}
                                        </td>
                                        <td>
                                            <div>{product.marca || '-'}</div>
                                            <small className="text-muted">{product.sku || '-'}</small>
                                        </td>
                                        <td><span className="badge-custom badge-secondary">{product.tipo}</span></td>
                                        <td>{formatCurrency(product.precio)}</td>
                                        <td>{product.impuesto}%</td>
                                        <td style={{ fontWeight: 'bold' }}>
                                            {formatCurrency(productsService.calculateTotal(product.precio, product.impuesto))}
                                        </td>
                                        <td>
                                            <span className={`badge-custom ${product.activo ? 'badge-success' : 'badge-danger'}`}>
                                                {product.activo ? 'Activo' : 'Inactivo'}
                                            </span>
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '10px' }}>
                                                <button
                                                    className="btn-icon"
                                                    onClick={() => navigate(`/productos/editar/${product.id}`)}
                                                    title="Editar"
                                                    style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--primary-orange)' }}
                                                >
                                                    <FiEdit2 size={18} />
                                                </button>
                                                <button
                                                    className="btn-icon"
                                                    onClick={() => handleDelete(product.id)}
                                                    title="Eliminar"
                                                    style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--danger-red)' }}
                                                >
                                                    <FiTrash2 size={18} />
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

export default ProductList;

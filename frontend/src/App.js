import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
// Force Rebuild
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/layout/Layout';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register'; // Importar Register
import Dashboard from './pages/dashboard/Dashboard';

import ProductList from './pages/products/ProductList';
import ProductForm from './pages/products/ProductForm';
import ClientList from './pages/clients/ClientList';
import ClientForm from './pages/clients/ClientForm';
import QuotationList from './pages/quotations/QuotationList';
import QuotationForm from './pages/quotations/QuotationForm';
import TaxManagement from './pages/taxes/TaxManagement';
import SelfServiceLink from './pages/admin/SelfServiceLink';
import Settings from './pages/admin/Settings';
import Reports from './pages/admin/Reports';
import PublicQuotationReview from './pages/public/PublicQuotationReview';
import PublicQuotation from './pages/public/PublicQuotation';
import Employees from './pages/admin/Employees';
import RequestsPanel from './pages/admin/RequestsPanel';
import MyRequests from './pages/requests/MyRequests';
import ForcePasswordChange from './pages/auth/ForcePasswordChange';

// Importar estilos
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/variables.css';
import './styles/components.css';

function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <BrowserRouter>
          <Routes>
            {/* Ruta pública de login */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Ruta pública de autoatención (para clientes - solicitar) */}
            <Route path="/autoatencion/:slug" element={<PublicQuotation />} />

            {/* Ruta pública de revisión (para clientes - aceptar/rechazar) */}
            <Route path="/cotizacion/:uuid" element={<PublicQuotationReview />} />

            {/* Ruta de Cambio Contraseña Forzado */}
            <Route
              path="/change-password"
              element={
                <ProtectedRoute allowPasswordChange={true}>
                  <ForcePasswordChange />
                </ProtectedRoute>
              }
            />


            {/* Rutas protegidas (Admin) */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />

              {/* Rutas de Productos */}
              <Route path="productos" element={<ProductList />} />
              <Route path="productos/nuevo" element={<ProductForm />} />
              <Route path="productos/editar/:id" element={<ProductForm />} />

              {/* Rutas de Clientes */}
              <Route path="clientes" element={<ClientList />} />
              <Route path="clientes/nuevo" element={<ClientForm />} />
              <Route path="clientes/editar/:id" element={<ClientForm />} />

              {/* Rutas de Cotizaciones */}
              <Route path="cotizaciones" element={<QuotationList />} />
              <Route path="cotizaciones/nuevo" element={<QuotationForm />} />
              <Route path="cotizaciones/editar/:id" element={<QuotationForm />} />

              {/* Ruta de Impuestos */}
              <Route path="impuestos" element={<TaxManagement />} />

              <Route path="autoatencion" element={<SelfServiceLink />} />
              <Route path="reportes" element={<Reports />} />
              <Route path="empleados" element={<Employees />} />
              <Route path="solicitudes" element={<RequestsPanel />} />
              <Route path="mis-solicitudes" element={<MyRequests />} />
              <Route path="configuracion" element={<Settings />} />
            </Route>

            {/* Ruta por defecto */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;

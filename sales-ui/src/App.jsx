import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import DashboardPage from './pages/DashboardPage';
import POSPage from './pages/POSPage';
import UsersPage from './pages/UsersPage';
import ProductPage from './pages/ProductPage';
import CustomerPage from './pages/CustomerPage';
import SupplierPage from './pages/SupplierPage';
import ExpirationControlPage from './pages/ExpirationControlPage';
import SalesHistoryPage from './pages/SalesHistoryPage';
import ReportsPage from './pages/ReportsPage';
import MarketingPage from './pages/MarketingPage';
import ReservationPage from './pages/ReservationPage';
import TableManagementPage from './pages/TableManagementPage';
import FloorPlanSettingsPage from './pages/FloorPlanSettingsPage';
import KDSPage from './pages/KDSPage';
import OpenCashRegisterPage from './pages/OpenCashRegisterPage';
import UnauthorizedPage from './pages/UnauthorizedPage';
import GlobalDashboardPage from './pages/superadmin/GlobalDashboardPage';
import StoresManagementPage from './pages/superadmin/StoresManagementPage';
// A página de Login original não é mais necessária

// --- NOSSO COMPONENTE DE ROTA PROTEGIDA (FASE 2) ---
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Carregando...</div>; // Ou um componente de Spinner
  }

  if (!isAuthenticated) {
    // NÃO está logado. Redireciona para o HUB CENTRAL
    const redirectPath = window.location.pathname + window.location.search;
    // Garante que o redirect seja prefixado com /sales/
    const safeRedirect = redirectPath.startsWith('/sales') ? redirectPath : `/sales${redirectPath}`;
    
    window.location.href = `http://localhost/login?redirect=${safeRedirect}`;
    return null; // Retorna nulo enquanto redireciona
  }

  return children; // Está logado, renderiza a página
}
// --- FIM DO COMPONENTE ---

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* A Rota de Login foi REMOVIDA */}
          <Route path="/unauthorized" element={<UnauthorizedPage />} />

          {/* Adicionamos o prefixo /sales/ a todas as rotas */}
          <Route 
            path="/sales/dashboard" 
            element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/pos" 
            element={<ProtectedRoute><POSPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/users" 
            element={<ProtectedRoute><UsersPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/products" 
            element={<ProtectedRoute><ProductPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/customers" 
            element={<ProtectedRoute><CustomerPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/suppliers" 
            element={<ProtectedRoute><SupplierPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/expiration" 
            element={<ProtectedRoute><ExpirationControlPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/history" 
            element={<ProtectedRoute><SalesHistoryPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/reports" 
            element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/marketing" 
            element={<ProtectedRoute><MarketingPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/reservations" 
            element={<ProtectedRoute><ReservationPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/tables" 
            element={<ProtectedRoute><TableManagementPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/floor-plan" 
            element={<ProtectedRoute><FloorPlanSettingsPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/kds" 
            element={<ProtectedRoute><KDSPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/open-cash-register" 
            element={<ProtectedRoute><OpenCashRegisterPage /></ProtectedRoute>} 
          />
          
          {/* Rotas de Super Admin */}
          <Route 
            path="/sales/super/dashboard" 
            element={<ProtectedRoute><GlobalDashboardPage /></ProtectedRoute>} 
          />
          <Route 
            path="/sales/super/stores" 
            element={<ProtectedRoute><StoresManagementPage /></ProtectedRoute>} 
          />

          {/* Rota Raiz - Redireciona para o dashboard de vendas */}
          <Route path="/" element={<Navigate to="/sales/dashboard" replace />} />
          <Route path="/sales" element={<Navigate to="/sales/dashboard" replace />} />

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
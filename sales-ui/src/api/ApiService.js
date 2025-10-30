// client/src/api/ApiService.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/sales', // <-- CORRIGIDO (Caminho do Gateway)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercetor de REQUISIÇÃO: Adiciona o token a cada chamada
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Intercetor de RESPOSTA: Lida com erros
ApiService.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

ApiService.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Redireciona para a página de login do Hub Central
      window.location.href = '/login'; // O Gateway vai rotear para o Auth-UI
    }
    return Promise.reject(error);
  }
);

// Agrupando todos os métodos da API em um único objeto
const ApiService = {
  // Funções genéricas
  get: (url, config) => apiClient.get(url, config),
  post: (url, data, config) => apiClient.post(url, data, config),
  put: (url, data, config) => apiClient.put(url, data, config),
  patch: (url, data, config) => apiClient.patch(url, data, config),
  delete: (url, config) => apiClient.delete(url, config),

  // Autenticação e Usuário
  login: (email, password) => {
    sessionStorage.removeItem('logout-message'); // Ainda pode ser útil limpar isso no login
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return ApiService.post('/login/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  getCurrentUser: () => ApiService.get('/users/me'),

  // Walls
  getWalls: () => ApiService.get('/walls/'),
  createWall: (wallData) => ApiService.post('/walls/', wallData),
  updateWall: (wallId, wallData) => ApiService.put(`/walls/${wallId}`, wallData),
  deleteWall: (wallId) => ApiService.delete(`/walls/${wallId}`),
  updateWallsLayout: (layoutData) => ApiService.put('/walls/layout', layoutData),

  // Caixa
  getCashRegisterStatus: () => ApiService.get('/cash-registers/status'),
  openCashRegister: (data) => ApiService.post('/cash-registers/open', data),

  // Produtos
  getProducts: (params) => ApiService.get('/products/', { params }),
  lookupProduct: (barcodeOrName) => ApiService.get(`/products/lookup?q=${barcodeOrName}`),

  // Vendas (Sales) - para finalizar o pagamento
  createSale: (saleData) => ApiService.post('/sales/', saleData),

  // Comandas (Orders) - para a venda persistente no POS
  processPartialPayment: (orderId, paymentData) => ApiService.post(`/orders/${orderId}/pay`, paymentData),

  createOrder: (orderData) => ApiService.post('/orders/', orderData),
  getActivePosOrder: () => ApiService.get('/orders/pos/active'),
  addItemToOrder: (orderId, itemData) => ApiService.post(`/orders/${orderId}/items`, itemData),
  cancelOrder: (orderId) => ApiService.patch(`/orders/${orderId}/cancel`),
  closeOrder: (orderId) => ApiService.patch(`/orders/${orderId}/close`),

  // Clientes
  getCustomers: (params) => ApiService.get('/customers/', { params }),
  createCustomer: (customerData) => ApiService.post('/customers/', customerData),
  // Adicione a função que faltava para buscar histórico do cliente
  getCustomerSalesHistory: (customerId) => ApiService.get(`/customers/${customerId}/sales`),


  // Outros...
  getStores: () => ApiService.get('/stores'),
  getGlobalDashboardSummary: () => ApiService.get('/super-admin/dashboard'),
  getDashboardSummary: () => ApiService.get('/reports/dashboard'),

  getTopSellingProducts: (limit = 10) => {
    return ApiService.get(`/reports/top-selling-products?limit=${limit}`);
  },
  getSalesEvolution: (startDate, endDate) => {
    return ApiService.get(`/reports/sales-evolution?start_date=${startDate}&end_date=${endDate}`);
  },
  getSalesByPeriodPdf: (startDate, endDate) => {
    return ApiService.get(`/reports/pdf/sales-by-period?start_date=${startDate}&end_date=${endDate}`, {
      responseType: 'blob',
    });
  },
   // Adicione as funções de usuário que faltavam (exemplo)
  createUser: (userData) => ApiService.post('/users/', userData),
  updateUser: (userId, userData) => ApiService.put(`/users/${userId}`, userData),
  deleteUser: (userId) => ApiService.delete(`/users/${userId}`), // Assumindo que a rota existe

  // Adicione as funções de fornecedor que faltavam (exemplo)
  createSupplier: (supplierData) => ApiService.post('/suppliers/', supplierData),
  updateSupplier: (supplierId, supplierData) => ApiService.put(`/suppliers/${supplierId}`, supplierData),
  deleteSupplier: (supplierId) => ApiService.delete(`/suppliers/${supplierId}`), // Assumindo que a rota existe
};

export default ApiService;
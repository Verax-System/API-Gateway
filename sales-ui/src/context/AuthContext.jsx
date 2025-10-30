import React, { createContext, useContext, useState, useEffect } from 'react';
import ApiService from '../api/ApiService';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Esta função é chamada quando o AuthProvider é montado
    const loadUserFromToken = async () => {
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;

          if (decodedToken.exp > currentTime) {
            // Token é válido e não expirado
            ApiService.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            
            // CORREÇÃO: Buscamos o usuário no /users/me do sales-api
            const response = await ApiService.get('/users/me'); //
            setUser(response.data);
            setIsAuthenticated(true);
          } else {
            // Token expirado
            logout();
          }
        } catch (error) {
          console.error("Falha ao carregar usuário do token", error);
          if (error.response && error.response.status === 404) {
            // O token é válido, mas o usuário não foi sincronizado
            console.error("Usuário não sincronizado. Redirecionando para logout.");
          }
          logout(); // Token inválido ou usuário não encontrado
        }
      }
      setIsLoading(false);
    };

    loadUserFromToken();
  }, []);

  // Funções de login e registro foram REMOVIDAS

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('token');
    delete ApiService.defaults.headers.common['Authorization'];
    // Redireciona para o Hub Central ao deslogar
    window.location.href = 'http://localhost/login';
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading, logout }}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
};
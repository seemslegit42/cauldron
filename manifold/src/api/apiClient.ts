import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Default API configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:80';

// Create axios instance with default config
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for adding auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling common errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      // Redirect to login or refresh token
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    
    // Handle server errors
    if (error.response && error.response.status >= 500) {
      console.error('Server error:', error.response.data);
      // Could dispatch to error tracking service
    }
    
    return Promise.reject(error);
  }
);

// Generic API client class
class ApiClient {
  // GET request
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await axiosInstance.get(url, config);
    return response.data;
  }
  
  // POST request
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await axiosInstance.post(url, data, config);
    return response.data;
  }
  
  // PUT request
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await axiosInstance.put(url, data, config);
    return response.data;
  }
  
  // PATCH request
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await axiosInstance.patch(url, data, config);
    return response.data;
  }
  
  // DELETE request
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await axiosInstance.delete(url, config);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export module-specific API clients
export const operationsApi = {
  getSalesOrders: () => apiClient.get('/api/operations/sales-orders'),
  createSalesOrder: (data: any) => apiClient.post('/api/operations/sales-orders', data),
  // Add more operations-specific endpoints
};

export const intelligenceApi = {
  getDashboards: () => apiClient.get('/api/intelligence/dashboards'),
  getForecasts: () => apiClient.get('/api/intelligence/forecasts'),
  // Add more intelligence-specific endpoints
};

export const securityApi = {
  getAlerts: () => apiClient.get('/api/security/alerts'),
  getSecurityStatus: () => apiClient.get('/api/security/status'),
  // Add more security-specific endpoints
};

export const knowledgeApi = {
  searchKnowledge: (query: string) => apiClient.get(`/api/knowledge/search?q=${encodeURIComponent(query)}`),
  getDocument: (id: string) => apiClient.get(`/api/knowledge/documents/${id}`),
  // Add more knowledge-specific endpoints
};

export const devopsApi = {
  getDeployments: () => apiClient.get('/api/devops/deployments'),
  getPipelines: () => apiClient.get('/api/devops/pipelines'),
  // Add more devops-specific endpoints
};

export default apiClient;
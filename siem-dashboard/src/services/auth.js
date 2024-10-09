import axios from 'axios';

const API_URL = 'http://localhost:8000/api'; // Adjust this to your backend URL

const isBrowser = typeof window !== 'undefined';

export async function login(username, password) {
  try {
    const response = await axios.post(`${API_URL}/auth/login/`, {
      username,
      password,
    });
    
    if (response.data.access && response.data.refresh) {
      localStorage.setItem('token', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      return response.data;
    } else {
      throw new Error('Login failed: Missing tokens');
    }
  } catch (error) {
    console.error('Login error:', error.response ? error.response.data : error.message);
    throw error;
  }
}

export async function signup(userData) {
  try {
    const response = await axios.post(`${API_URL}/auth/signup/`, userData);
    console.log('Signup response:', response.data);  // Add this for debugging
    return response.data;
  } catch (error) {
    console.error('Signup error:', error.response ? error.response.data : error.message);
    throw error;
  }
}

export async function logout() {
  try {
    await axios.post(`${API_URL}/auth/logout/`, {}, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    if (isBrowser) {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    }
  } catch (error) {
    console.error('Logout error:', error);
    // Still remove tokens even if the request fails
    if (isBrowser) {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    }
  }
}

export const manualLogout = () => {
  if (isBrowser) {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    // Redirect to login page
    window.location.href = '/login';
  }
};

export function getToken() {
    if (!isBrowser) return null;
    return localStorage.getItem('token');
}

export function isAuthenticated() {
    if (!isBrowser) return false;
    return !!getToken();
}

export async function refreshToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
      refresh: refreshToken
    });
    
    localStorage.setItem('token', response.data.access);
    return response.data.access;
  } catch (error) {
    console.error('Token refresh error:', error);
    logout(); // Force logout if refresh fails
    throw error;
  }
}


import { showToast } from './utils.js';

/**
 * ApiService - Handles all API communication with the server
 * Provides methods for making HTTP requests with consistent error handling and user feedback
 */
class ApiService {
  /**
   * Makes a POST request to the specified URL with optional data
   * @param {string} url - The URL to make the request to
   * @param {Object|FormData|null} [data=null] - The data to send with the request
   * @param {Object} [options={}] - Additional options for the request
   * @param {boolean} [options.showSuccess=true] - Whether to show success toast
   * @param {boolean} [options.showError=true] - Whether to show error toast
   * @param {string} [options.successMessage] - Custom success message
   * @param {string} [options.errorMessage] - Custom error message
   * @returns {Promise<Object|string>} The parsed JSON response or text if not JSON
   */
  static async post(url, data = null, options = {}) {
    const {
      showSuccess = true,
      showError = true,
      successMessage = 'Operation completed successfully',
      errorMessage = 'An error occurred',
      ...fetchOptions
    } = options;

    try {
      const formData = new FormData();
      formData.append('csrfmiddlewaretoken', window.CSRF_TOKEN);
      
      // Handle different data types
      if (data instanceof FormData) {
        // If it's already FormData, append all entries
        for (const [key, value] of data.entries()) {
          formData.append(key, value);
        }
      } else if (data && typeof data === 'object') {
        // If it's a plain object, append each key-value pair
        for (const [key, value] of Object.entries(data)) {
          formData.append(key, value);
        }
      } else if (data !== null) {
        formData.append('data', data);
      }

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        ...fetchOptions
      });

      const contentType = response.headers.get('content-type');
      const isJson = contentType && contentType.includes('application/json');
      
      if (!response.ok) {
        const errorData = isJson ? await response.json() : await response.text();
        const error = new Error(errorData.message || errorData || 'Request failed');
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      const result = isJson ? await response.json() : await response.text();
      
      if (showSuccess && successMessage) {
        showToast(successMessage, 'success');
      }
      
      return result;
      
    } catch (error) {
      console.error('API Error:', error);
      
      if (showError) {
        const message = error.message || errorMessage;
        showToast(message, 'error');
      }
      
      throw error;
    }
  }

  /**
   * Makes a request to a URL with an ID (e.g., /api/endpoint/123/)
   * @param {string} baseUrl - The base URL (without the ID)
   * @param {string|number} id - The ID to append to the URL
   * @param {Object} [options] - Options for the request
   * @returns {Promise<Object|string>} The parsed response
   */
  static async idMethod(baseUrl, id, options = {}) {
    const url = `${baseUrl.replace(/\/$/, '')}/${id}/`;
    return this.post(url, null, options);
  }

  /**
   * Makes a GET request to the specified URL
   * @param {string} url - The URL to make the request to
   * @param {Object} [options] - Additional options for the request
   * @returns {Promise<Object|string>} The parsed response
   */
  static async get(url, options = {}) {
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'same-origin',
      ...options
    });

    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');
    
    if (!response.ok) {
      const errorData = isJson ? await response.json() : await response.text();
      const error = new Error(errorData.message || 'Request failed');
      error.status = response.status;
      error.data = errorData;
      throw error;
    }
    
    return isJson ? response.json() : response.text();
  }

  /**
   * Makes a DELETE request to the specified URL
   * @param {string} url - The URL to make the request to
   * @param {Object} [options] - Additional options for the request
   * @returns {Promise<Object|string>} The parsed response
   */
  static async delete(url, options = {}) {
    const response = await fetch(url, {
      method: 'DELETE',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': window.CSRF_TOKEN,
        ...options.headers
      },
      ...options
    });

    if (response.status === 204) return null; // No content
    
    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');
    
    if (!response.ok) {
      const errorData = isJson ? await response.json() : await response.text();
      const error = new Error(errorData.message || 'Delete failed');
      error.status = response.status;
      error.data = errorData;
      throw error;
    }
    
    return isJson ? response.json() : response.text();
  }
}

export default ApiService;

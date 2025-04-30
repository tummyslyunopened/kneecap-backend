class ApiService {
  static async post(url, data = null) {
    try {
      const formData = new FormData();
      formData.append('csrfmiddlewaretoken', window.CSRF_TOKEN);
      if (data !== null) {
        formData.append('data', data);
      }

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      let resultText = await response.text();
      return resultText;
    } catch (error) {
      throw error;
    }
  }

  static async idMethod(url, id) {
    const fullUrl = `${url}/${id}/`;
    try {
      const formData = new FormData();
      formData.append('csrfmiddlewaretoken', window.CSRF_TOKEN);

      const response = await fetch(fullUrl, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      const result = await response.text();
      return result;
    } catch (error) {
      throw error;
    }
  }
}

export default ApiService;

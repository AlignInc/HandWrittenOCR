import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 120000, // 120 seconds for OCR processing
    headers: {
        'Content-Type': 'application/json',
    },
});

// Create new batch with images
export const createBatch = async (files, formType = 'GCCF_10K') => {
    const formData = new FormData();
    files.forEach((file) => {
        formData.append('images', file);
    });

    const response = await api.post(`/api/batches?form_type=${formType}`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

// Get batch status and results
export const getBatch = async (batchId) => {
    const response = await api.get(`/api/batches/${batchId}`);
    return response.data;
};

// Update batch data
export const updateBatch = async (batchId, data) => {
    const response = await api.put(`/api/batches/${batchId}`, { data });
    return response.data;
};

// Export batch
export const exportBatch = async (batchId, format = 'csv') => {
    const response = await api.get(`/api/batches/${batchId}/export?format=${format}`, {
        responseType: 'blob',
    });
    return response.data;
};

export const batchApi = {
    createBatch,
    getBatch,
    updateBatch,
    exportBatch
};

export default api;

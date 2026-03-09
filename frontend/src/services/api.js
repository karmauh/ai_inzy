import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const scale = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const uploadCSV = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Wysłanie pliku CSV do backendu
    const response = await scale.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const analyzeData = async (data, modelType = 'isolation_forest', contamination = 0.05, tickerInfo = null, language = 'pl') => {
    const response = await scale.post('/analyze', {
        data,
        model_type: modelType,
        contamination,
        ticker_info: tickerInfo,
        language
    });
    return response.data;
};

export const fetchMarketData = async (symbol) => {
    const response = await scale.get(`/market/data/${symbol}`);
    return response.data;
};

export default scale;

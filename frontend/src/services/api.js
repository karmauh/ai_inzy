import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const scale = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

const downloadFile = async (response, filename) => {
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

export const exportCSV = async (data) => {
    const response = await scale.post('/export/csv', data, {
        responseType: 'blob'
    });
    downloadFile(response, 'stock_data.csv');
};

export const exportPDF = async (data, assessment, tickerInfo, language) => {
    const response = await scale.post('/export/pdf', {
        data,
        assessment,
        ticker_info: tickerInfo,
        language
    }, {
        responseType: 'blob'
    });
    downloadFile(response, 'analysis_report.pdf');
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

export const evaluateModelsAPI = async (data, fraction = 0.05, models = ['isolation_forest', 'lof', 'ocsvm', 'autoencoder']) => {
    const response = await scale.post('/evaluation/evaluate', {
        data,
        fraction,
        models
    });
    return response.data;
};

export default scale;

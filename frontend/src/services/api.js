import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

const downloadFile = (response, filename) => {
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
};

export const exportCSV = async (data, filename = 'stock_data.csv') => {
    const response = await client.post('/export/csv', data, {
        responseType: 'blob'
    });
    downloadFile(response, filename);
};

export const exportPDF = async (data, assessment, tickerInfo, language) => {
    const response = await client.post('/export/pdf', {
        data,
        assessment,
        ticker_info: tickerInfo,
        language
    }, {
        responseType: 'blob'
    });
    downloadFile(response, `analysis_report_${language}.pdf`);
};

export const analyzeData = async (data, modelType = 'isolation_forest', contamination = 0.05, tickerInfo = null, language = 'pl', mode = 'batch') => {
    const response = await client.post('/analyze', {
        data,
        model_type: modelType,
        contamination,
        mode,
        ticker_info: tickerInfo,
        language
    });
    return response.data;
};

export const generateAssessment = async (results, tickerInfo = null, language = 'pl') => {
    const response = await client.post('/assessment', {
        results,
        ticker_info: tickerInfo,
        language
    });
    return response.data;
};

export const fetchMarketData = async (symbol) => {
    const response = await client.get(`/market/data/${encodeURIComponent(symbol)}`);
    return response.data;
};

export const evaluateModelsAPI = async (data, fraction = 0.05, models = ['isolation_forest', 'lof', 'ocsvm', 'autoencoder'], mode = 'batch') => {
    const response = await client.post('/evaluation/evaluate', {
        data,
        fraction,
        models,
        mode
    });
    return response.data;
};

export default client;

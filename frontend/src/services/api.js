import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const scale = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Eksport danych do CSV
export const exportCSV = async (data) => {
    const response = await axios.post(`${API_URL}/export/csv`, data, {
        responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'stock_data.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link); // Clean up the DOM
};

// Eksport raportu do PDF
export const exportPDF = async (data, assessment, tickerInfo, language) => {
    const response = await axios.post(`${API_URL}/export/pdf`, {
        data,
        assessment,
        ticker_info: tickerInfo,
        language
    }, {
        responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'analysis_report.pdf');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link); // Clean up the DOM
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

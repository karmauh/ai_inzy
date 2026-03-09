import React, { useState } from 'react';

const FileUpload = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setError(null);
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file first.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // Dynamiczny import usługi API
            const { uploadCSV } = await import('../services/api');
            const result = await uploadCSV(file);
            onUploadSuccess(result);
        } catch (err) {
            console.error("Upload failed", err);
            setError("Upload failed. Please check the file and try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 bg-slate-800 rounded-lg shadow-lg max-w-md mx-auto">
            <h2 className="text-xl font-bold mb-4 text-blue-400">Upload Stock Data</h2>
            
            <div className="mb-4">
                <input 
                    type="file" 
                    accept=".csv"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-400
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-full file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-600 file:text-white
                        hover:file:bg-blue-700
                    "
                />
            </div>

            {error && (
                <div className="mb-4 text-red-400 text-sm">
                    {error}
                </div>
            )}

            <button
                onClick={handleUpload}
                disabled={!file || loading}
                className={`w-full py-2 px-4 rounded font-bold text-white transition-colors
                    ${!file || loading 
                        ? 'bg-gray-600 cursor-not-allowed' 
                        : 'bg-blue-600 hover:bg-blue-700'
                    }
                `}
            >
                {loading ? 'Processing...' : 'Upload & Process'}
            </button>
        </div>
    );
};

export default FileUpload;

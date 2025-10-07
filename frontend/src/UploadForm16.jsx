import React, { useState } from 'react';
import axios from 'axios';

export default function UploadForm16() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post('http://localhost:8000/upload/form16', formData);
      setResult(res.data);
    } catch (error) {
      console.error('Upload error:', error);
      setResult({ error: 'Upload failed' });
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Upload Form 16</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} accept="image/*" />
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? 'Processing...' : 'Upload Form16'}
      </button>
      {result && (
        <div>
          <h3>Results:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
          {result.tax_summary && (
            <div>
              <p><strong>Recommended Regime:</strong> {result.tax_summary.recommended_regime}</p>
              <p><strong>Potential Savings:</strong> ₹{result.tax_summary.savings}</p>
              <p><strong>Suggestion:</strong> {result.suggestion}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

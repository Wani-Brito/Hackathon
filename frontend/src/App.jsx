import { useState } from 'react';
import axios from 'axios';
import { Upload, Loader2, RefreshCcw } from 'lucide-react';

const API_URL = "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const processImage = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/process-image`, formData);
      setResult(response.data);
    } catch (err) {
      setError("Erro ao processar imagem. Verifique se o backend está rodando.");
    } finally {
      setLoading(false);
    }
  };

  const uniqueDetections = result?.detections
    ? Object.values(
        result.detections.reduce((acc, item) => {
          const key = item.tag;
          if (!acc[key] || item.confidence > acc[key].confidence) {
            acc[key] = item;
          }
          return acc;
        }, {})
      )
    : [];

  return (
    <div className="p-8 max-w-4xl mx-auto font-sans text-gray-900">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold mb-2">TAGVision P&ID</h1>
        <p className="text-gray-500">Análise inteligente de plantas técnicas</p>
      </header>

      {!result && !loading && (
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center bg-gray-50">
          <Upload className="mx-auto mb-4 text-purple-600" size={48} />
          <input type="file" onChange={handleFileChange} className="mb-4 block mx-auto" />
          {preview && <img src={preview} alt="Preview" className="max-h-64 mx-auto mb-4 rounded shadow" />}
          <button onClick={processImage} disabled={!file} className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition">
            Processar Planta
          </button>
        </div>
      )}

      {loading && (
        <div className="text-center py-20">
          <Loader2 className="animate-spin mx-auto mb-4 text-purple-600" size={48} />
          <p className="text-lg text-gray-600">Analisando planta...</p>
        </div>
      )}

      {error && <div className="text-red-500 text-center p-4 bg-red-50 rounded-lg">{error}</div>}

      {result && (
        <div>
          <h2 className="text-2xl font-semibold mb-6">Resultados da Análise</h2>
          <img src={`${API_URL}${result.processed_image_url}`} alt="Processada" className="mb-8 rounded-lg shadow-xl w-full" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {uniqueDetections.length > 0 ? uniqueDetections.map((d) => (
              <div key={d.tag} className="border border-gray-200 p-4 rounded-xl bg-white shadow-sm">
                <p className="font-bold text-lg mb-1">{d.tag} <span className={`text-xs px-2 py-0.5 rounded-full ${d.status === 'Identificado' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>{d.status}</span></p>
                <p className="text-sm text-gray-600">Tipo: {d.tipo} | Classe: {d.classe}</p>
                <p className="text-sm text-gray-600">Confiança: {(d.confidence * 100).toFixed(0)}%</p>
              </div>
            )) : <p className="text-gray-500 italic">Nenhum equipamento cadastrado foi identificado.</p>}
          </div>

          <div className="flex justify-center">
            <button onClick={() => {setResult(null); setFile(null); setPreview(null);}} className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 px-6 py-2 rounded-lg transition">
              <RefreshCcw size={16} /> Nova análise
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CamisetaImage from './CamisetaImage';

const CamisetasGaleria = () => {
  const [camisetas, setCamisetas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCamisetas = async () => {
      try {
        console.log('Iniciando busca de camisetas...');
        const response = await axios.get('http://localhost:5000/listar-camisetas');
        console.log('Resposta do servidor:', response.data);
        
        if (response.data && Array.isArray(response.data)) {
          setCamisetas(response.data);
        } else {
          setError('Formato de dados inválido');
          console.error('Dados inválidos:', response.data);
        }
      } catch (err) {
        console.error('Erro ao carregar camisetas:', err);
        setError(`Erro ao carregar camisetas: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchCamisetas();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-white">Carregando camisetas...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64 flex-col">
        <div className="text-red-500 mb-2">{error}</div>
        <button 
          onClick={() => window.location.reload()} 
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  if (!camisetas || camisetas.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-400">Nenhuma camiseta encontrada no sistema</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 p-4">
      {camisetas.map((camiseta) => (
        <div key={camiseta.id || Math.random()} className="bg-gray-800 p-4 rounded-lg">
          <CamisetaImage camiseta={camiseta} />
          <div className="mt-2 text-center">
            <h3 className="text-sm font-medium text-white">{camiseta.nome}</h3>
            <p className="text-sm text-gray-400">R$ {camiseta.preco}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CamisetasGaleria;

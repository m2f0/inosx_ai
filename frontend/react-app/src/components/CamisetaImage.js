import React, { useState, useEffect } from 'react';
import { FaImage } from 'react-icons/fa';

const CamisetaImage = ({ camiseta }) => {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const imagePath = `http://localhost:5000/static/camisetas/${camiseta.imagem}`;

  useEffect(() => {
    console.log('Tentando carregar imagem:', imagePath);
  }, [imagePath]);

  return (
    <div className="relative aspect-square w-full overflow-hidden rounded-lg bg-gray-700">
      {isLoading && !imageError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-pulse text-gray-400">
            <FaImage size={24} />
          </div>
        </div>
      )}
      
      {!imageError && (
        <img
          src={imagePath}
          alt={camiseta.nome}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            isLoading ? 'opacity-0' : 'opacity-100'
          }`}
          onError={(e) => {
            console.error('Erro ao carregar imagem:', imagePath);
            setImageError(true);
            setIsLoading(false);
          }}
          onLoad={() => {
            console.log('Imagem carregada com sucesso:', imagePath);
            setIsLoading(false);
          }}
        />
      )}

      {imageError && (
        <div className="absolute inset-0 flex flex-col items-center justify-center p-4">
          <FaImage className="text-gray-500 mb-2" size={32} />
          <p className="text-sm text-gray-400 text-center">
            Imagem não disponível
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {camiseta.imagem}
          </p>
        </div>
      )}
    </div>
  );
};

export default CamisetaImage;

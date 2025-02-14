import React, { useState } from 'react';
import { FaImage } from 'react-icons/fa';

const CamisetaImage = ({ camiseta }) => {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const handleImageError = (e) => {
    console.warn('Imagem não encontrada:', camiseta.imagem);
    setImageError(true);
    setIsLoading(false);
  };

  const handleImageLoad = () => {
    setIsLoading(false);
  };

  return (
    <div className="relative w-full h-48">
      {isLoading && (
        <div className="absolute inset-0 bg-gray-700 rounded-lg animate-pulse" />
      )}
      
      {imageError ? (
        <div className="w-full h-48 bg-gray-700 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <FaImage className="mx-auto text-4xl text-gray-500 mb-2" />
            <p className="text-sm text-gray-400">{camiseta.nome}</p>
          </div>
        </div>
      ) : (
        <img
          src={`http://localhost:5000/camisetas/${camiseta.imagem}`}
          alt={camiseta.nome}
          className={`w-full h-48 object-cover rounded-lg ${
            isLoading ? 'opacity-0' : 'opacity-100'
          } transition-opacity duration-300`}
          onError={handleImageError}
          onLoad={handleImageLoad}
        />
      )}
    </div>
  );
};

export default CamisetaImage;

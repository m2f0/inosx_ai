import React, { useState } from 'react';
import { FaImage, FaShoppingCart } from 'react-icons/fa';

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

  const handleCheckout = () => {
    // Criar URL com parâmetros do produto
    const checkoutUrl = `/checkout?` + new URLSearchParams({
      produto: camiseta.nome,
      imagem: camiseta.imagem,
      preco: camiseta.preco || '39.90', // Preço padrão se não especificado
      id: camiseta.id || Date.now()
    }).toString();

    // Abrir em nova aba
    window.open(checkoutUrl, '_blank');
  };

  return (
    <div className="relative w-full h-48 group cursor-pointer" onClick={handleCheckout}>
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
        <>
          <img
            src={`http://localhost:5000/camisetas/${camiseta.imagem}`}
            alt={camiseta.nome}
            className={`w-full h-48 object-cover rounded-lg ${
              isLoading ? 'opacity-0' : 'opacity-100'
            } transition-opacity duration-300 group-hover:opacity-80`}
            onError={handleImageError}
            onLoad={handleImageLoad}
          />
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-black bg-opacity-50 rounded-lg">
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
              <FaShoppingCart />
              <span>Comprar</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default CamisetaImage;

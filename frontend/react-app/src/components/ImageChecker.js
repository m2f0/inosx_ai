import React, { useEffect } from 'react';

const ImageChecker = () => {
  useEffect(() => {
    const imagesToCheck = [
      '/camisetas/camiseta-basica-preta.jpg',
      '/camisetas/camiseta-basica-branca.jpg',
      '/camisetas/camiseta-premium-azul.jpg'
    ];

    imagesToCheck.forEach(imagePath => {
      const img = new Image();
      img.onload = () => {
        console.log('✅ Imagem existe:', imagePath);
      };
      img.onerror = () => {
        console.error('❌ Imagem não encontrada:', imagePath);
      };
      img.src = imagePath;
    });
  }, []);

  return null;
};

export default ImageChecker;
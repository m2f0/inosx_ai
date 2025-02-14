import React, { useState, useEffect } from 'react';

const CamisetaItem = ({ camiseta }) => {
    const [imageError, setImageError] = useState(false);
    const [imageStatus, setImageStatus] = useState('loading');

    const handleImageError = (e) => {
        console.error('Erro ao carregar imagem:', {
            src: e.target.src,
            error: e.error
        });
        setImageError(true);
        setImageStatus('error');
    };

    const handleImageLoad = () => {
        setImageStatus('loaded');
    };

    return (
        <div className="camiseta-item">
            {!imageError ? (
                <img
                    src={`http://localhost:5000/camisetas/${camiseta.imagem}`}
                    alt={camiseta.nome}
                    className="camiseta-image"
                    onError={handleImageError}
                    onLoad={handleImageLoad}
                />
            ) : (
                <div className="camiseta-image-fallback">
                    <p>Imagem não disponível</p>
                    <small>Status: {imageStatus}</small>
                    <small>URL: {camiseta.imagem}</small>
                </div>
            )}
            <h3 className="camiseta-nome">{camiseta.nome}</h3>
        </div>
    );
};

export default CamisetaItem;

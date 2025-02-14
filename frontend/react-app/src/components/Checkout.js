import React, { useState, useEffect } from 'react';
import { FaArrowLeft, FaShoppingCart } from 'react-icons/fa';

const Checkout = () => {
  const [produto, setProduto] = useState(null);
  const [quantidade, setQuantidade] = useState(1);

  useEffect(() => {
    // Pegar parâmetros da URL
    const params = new URLSearchParams(window.location.search);
    setProduto({
      nome: params.get('produto'),
      imagem: params.get('imagem'),
      preco: parseFloat(params.get('preco')),
      id: params.get('id')
    });
  }, []);

  const calcularTotal = () => {
    if (!produto) return 0;
    return (produto.preco * quantidade).toFixed(2);
  };

  const handleComprar = () => {
    // Aqui você implementaria a lógica de compra
    alert('Compra finalizada com sucesso!');
  };

  if (!produto) return <div>Carregando...</div>;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <button 
          onClick={() => window.close()} 
          className="flex items-center space-x-2 text-gray-400 hover:text-white mb-8"
        >
          <FaArrowLeft />
          <span>Voltar</span>
        </button>

        <div className="bg-gray-800 rounded-lg p-6">
          <h1 className="text-2xl font-bold mb-8">Checkout</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <img
                src={`http://localhost:5000/camisetas/${produto.imagem}`}
                alt={produto.nome}
                className="w-full rounded-lg"
              />
            </div>

            <div className="space-y-6">
              <h2 className="text-xl font-semibold">{produto.nome}</h2>
              
              <div className="text-lg">
                <span className="text-gray-400">Preço: </span>
                <span className="text-green-400">R$ {produto.preco.toFixed(2)}</span>
              </div>

              <div className="space-y-2">
                <label className="block text-gray-400">Quantidade</label>
                <input
                  type="number"
                  min="1"
                  value={quantidade}
                  onChange={(e) => setQuantidade(Math.max(1, parseInt(e.target.value)))}
                  className="bg-gray-700 rounded px-3 py-2 w-24"
                />
              </div>

              <div className="text-xl font-bold">
                <span className="text-gray-400">Total: </span>
                <span className="text-green-400">R$ {calcularTotal()}</span>
              </div>

              <button
                onClick={handleComprar}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg flex items-center justify-center space-x-2"
              >
                <FaShoppingCart />
                <span>Finalizar Compra</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
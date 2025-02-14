from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import logging
import os.path
import shutil
from pathlib import Path

# Configuração de logging mais detalhada
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Definir o caminho absoluto para o diretório de camisetas
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
CAMISETAS_DIR = os.path.join(BACKEND_DIR, "camisetas")

# Log do caminho para debug
logger.debug(f"Backend directory: {BACKEND_DIR}")
logger.debug(f"Camisetas directory: {CAMISETAS_DIR}")

# Carregar variáveis do .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração do OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
    raise ValueError("OPENAI_API_KEY não encontrada")

client = openai.Client(api_key=api_key)

SYSTEM_PROMPT = """
Você é um assistente virtual especializado em atendimento ao cliente.
Mantenha suas respostas concisas e diretas.
"""

DEMO_PROMPT = """
Você é um assistente virtual da StyleTech Camisetas, uma empresa especializada em camisetas personalizadas.
Mantenha suas respostas focadas no contexto de uma loja de camisetas, incluindo:
- Tipos de camisetas (básica, premium, gola V, etc)
- Processos de personalização
- Prazos de entrega (5-7 dias úteis)
- Preços base (camisetas básicas R$39,90, premium R$59,90)
- Descontos para pedidos em quantidade
- Processo de pedido e personalização

Mantenha um tom profissional mas amigável, sempre focando nas soluções da StyleTech Camisetas.
"""

# Função para inicializar o diretório de camisetas com imagens de exemplo
def init_camisetas_dir():
    # Criar diretório se não existir
    if not os.path.exists(CAMISETAS_DIR):
        os.makedirs(CAMISETAS_DIR)
        logger.info(f"Diretório de camisetas criado: {CAMISETAS_DIR}")
    
    # Lista de camisetas padrão (você precisará fornecer estas imagens)
    camisetas_padrao = [
        {
            'nome': 'Camiseta Básica Preta',
            'arquivo': 'camiseta-basica-preta.jpg'
        },
        {
            'nome': 'Camiseta Básica Branca',
            'arquivo': 'camiseta-basica-branca.jpg'
        },
        {
            'nome': 'Camiseta Premium Azul',
            'arquivo': 'camiseta-premium-azul.jpg'
        }
    ]
    
    return camisetas_padrao

# Chamar a função de inicialização ao iniciar o app
camisetas_padrao = init_camisetas_dir()

@app.route('/camisetas/<path:filename>')
def serve_camiseta(filename):
    try:
        # Remover qualquer prefixo 'camisetas/' do filename
        filename = filename.replace('camisetas/', '')
        file_path = os.path.join(CAMISETAS_DIR, filename)
        
        logger.debug(f"Requisição de imagem recebida para: {filename}")
        logger.debug(f"Caminho completo do arquivo: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return jsonify({"error": "Arquivo não encontrado"}), 404
        
        # Determinar o mimetype baseado na extensão do arquivo
        extension = os.path.splitext(filename)[1].lower()
        mimetype = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }.get(extension, 'application/octet-stream')
        
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=False,
            etag=True,
            conditional=True,
            last_modified=os.path.getmtime(file_path)
        )
    except Exception as e:
        logger.error(f"Erro ao servir imagem {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/listar-camisetas')
def listar_camisetas():
    try:
        logger.debug(f"Verificando diretório: {CAMISETAS_DIR}")
        
        if not os.path.exists(CAMISETAS_DIR):
            logger.warning(f"Diretório de camisetas não encontrado: {CAMISETAS_DIR}")
            return jsonify([])

        camisetas = []
        arquivos = os.listdir(CAMISETAS_DIR)
        
        # Se não houver arquivos, retornar lista das camisetas padrão
        if not arquivos:
            return jsonify([
                {
                    'nome': camiseta['nome'],
                    'imagem': camiseta['arquivo'],
                    'id': idx + 1
                }
                for idx, camiseta in enumerate(camisetas_padrao)
            ])

        # Se houver arquivos, listar as camisetas existentes
        for arquivo in arquivos:
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                caminho_completo = os.path.join(CAMISETAS_DIR, arquivo)
                if os.path.isfile(caminho_completo):
                    camisetas.append({
                        'nome': os.path.splitext(arquivo)[0].replace('-', ' ').title(),
                        'imagem': arquivo,
                        'id': len(camisetas) + 1
                    })
        
        return jsonify(camisetas)
    except Exception as e:
        logger.error(f"Erro ao listar camisetas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/perguntar', methods=['POST'])
def perguntar():
    try:
        data = request.get_json()
        pergunta = data.get('pergunta', '').lower()
        modo_demo = data.get('modoDemo', False)

        if not pergunta or not pergunta.strip():
            return jsonify({'error': 'Pergunta não pode ser vazia'}), 400

        # Palavras-chave que devem acionar a galeria de imagens
        palavras_chave = [
            'produtos', 'modelos', 'camisetas', 'mostrar', 'catálogo', 
            'disponíveis', 'mostra', 'ver', 'quais', 'galeria'
        ]

        # Se estiver no modo demo e a pergunta contiver alguma das palavras-chave
        if modo_demo and any(palavra in pergunta for palavra in palavras_chave):
            camisetas = []
            for arquivo in os.listdir(CAMISETAS_DIR):
                if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    camisetas.append({
                        'nome': os.path.splitext(arquivo)[0].replace('-', ' ').title(),
                        'imagem': arquivo  # Remover o prefixo 'camisetas/'
                    })

            contexto_produtos = {
                'camisetas': camisetas,
                'mostrar_galeria': True
            }
        else:
            contexto_produtos = {'mostrar_galeria': False}

        # Seleciona o prompt baseado no modo
        prompt = DEMO_PROMPT if modo_demo else SYSTEM_PROMPT

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": pergunta}
            ],
            temperature=0.7
        )

        resposta_completa = response.choices[0].message.content
        
        # Sugestões específicas para o modo demo
        sugestoes = [
            "Quais são os tipos de camiseta?",
            "Como personalizo minha camiseta?",
            "Qual o prazo de entrega?"
        ] if modo_demo else [
            "Como posso ajudar?",
            "Conte-me mais",
            "Preciso de mais informações"
        ]

        logger.debug(f"Modo Demo: {modo_demo}")
        logger.debug(f"Pergunta: {pergunta}")
        logger.debug(f"Mostrar galeria: {contexto_produtos['mostrar_galeria']}")
        logger.debug(f"Número de camisetas: {len(contexto_produtos.get('camisetas', []))}")

        return jsonify({
            'resposta': resposta_completa,
            'sugestoes': sugestoes,
            **contexto_produtos
        })

    except Exception as e:
        logger.error(f"Erro não esperado: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

@app.route('/debug/camisetas')
def debug_camisetas():
    try:
        files = os.listdir(CAMISETAS_DIR)
        return jsonify({
            'directory': CAMISETAS_DIR,
            'files': files,
            'exists': os.path.exists(CAMISETAS_DIR),
            'is_dir': os.path.isdir(CAMISETAS_DIR)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Verificar configurações críticas antes de iniciar
    logger.info("Iniciando servidor...")
    logger.info(f"OpenAI API Key presente: {bool(api_key)}")
    
    app.run(debug=True)

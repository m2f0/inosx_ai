from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import logging
import os.path
import shutil
from pathlib import Path
from PyPDF2 import PdfReader

# Configuração de logging mais detalhada
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Definir o caminho absoluto para o diretório de camisetas
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
CAMISETAS_DIR = os.path.join(BACKEND_DIR, "camisetas")
PDF_DIR = os.path.join(os.path.dirname(__file__), 'pdfs')

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

# Primeiro carregamos o conteúdo dos PDFs
def load_pdf_content():
    pdf_content = {
        'produtos': [],  # Será preenchido com produtos dos PDFs
        'servicos': [],  # Será preenchido com serviços dos PDFs
        'descricoes': {},
        'precos': {},
        'especificacoes': {}
    }
    
    try:
        Path(PDF_DIR).mkdir(parents=True, exist_ok=True)
        
        if os.path.exists(PDF_DIR):
            for pdf_file in os.listdir(PDF_DIR):
                if pdf_file.lower().endswith('.pdf'):
                    pdf_path = os.path.join(PDF_DIR, pdf_file)
                    
                    try:
                        reader = PdfReader(pdf_path)
                        text = ''
                        for page in reader.pages:
                            text += page.extract_text() + '\n'
                        
                        # Armazenar o texto completo para referência
                        pdf_content['descricoes'][pdf_file] = text
                        
                        # Extrair informações específicas baseado no nome do arquivo
                        filename = pdf_file.lower()
                        if 'produtos' in filename:
                            produtos = extract_products_info(text)
                            pdf_content['produtos'].extend(produtos)
                        elif 'servicos' in filename:
                            servicos = extract_services_info(text)
                            pdf_content['servicos'].extend(servicos)
                        elif 'precos' in filename:
                            precos = extract_pricing_info(text)
                            pdf_content['precos'].update(precos)
                        elif 'especificacoes' in filename:
                            specs = extract_specifications_info(text)
                            pdf_content['especificacoes'].update(specs)
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar PDF {pdf_file}: {str(e)}")
                        continue
        
        logger.info(f"PDFs carregados com sucesso: {len(pdf_content['descricoes'])} arquivos")
        return pdf_content
    
    except Exception as e:
        logger.error(f"Erro ao carregar PDFs: {str(e)}")
        return pdf_content

def extract_products_info(text):
    """
    Extrai informações estruturadas sobre produtos do texto do PDF
    Implemente aqui a lógica de extração específica para seus PDFs
    """
    # Implementar parser específico para o formato dos seus PDFs
    produtos = []
    # Adicione aqui a lógica de extração
    return produtos

def extract_services_info(text):
    """
    Extrai informações estruturadas sobre serviços do texto do PDF
    """
    servicos = []
    # Adicione aqui a lógica de extração
    return servicos

def extract_pricing_info(text):
    """
    Extrai informações estruturadas sobre preços do texto do PDF
    """
    precos = {}
    # Adicione aqui a lógica de extração
    return precos

def extract_specifications_info(text):
    """
    Extrai informações estruturadas sobre especificações do texto do PDF
    """
    specs = {}
    # Adicione aqui a lógica de extração
    return specs

# Carregar conteúdo dos PDFs
pdf_content = load_pdf_content()

# Agora podemos definir o SYSTEM_PROMPT
SYSTEM_PROMPT = """
Você é um consultor comercial virtual da INOSX, especializado em vendas consultivas de soluções de inteligência artificial.

Sua personalidade e abordagem:
- Seja sempre caloroso e profissional, demonstrando genuíno interesse nas necessidades do cliente
- Apresente-se como consultor comercial da INOSX no início da conversa
- Use linguagem corporativa mas acessível, evitando termos técnicos desnecessários
- Demonstre conhecimento profundo do mercado de IA e das soluções INOSX
- Construa rapport através de perguntas estratégicas sobre o negócio do cliente
- Mantenha um tom consultivo, focando em resolver problemas reais
- Use storytelling com cases de sucesso relevantes para o contexto
- Seja proativo em identificar oportunidades de cross-selling
- Demonstre empatia com as dores e desafios do cliente

Estratégia de vendas:
1. Qualifique o cliente com perguntas sobre:
   - Setor de atuação
   - Principais desafios
   - Processos atuais
   - Objetivos de negócio
   
2. Identifique oportunidades relacionando:
   - Dores específicas com soluções INOSX
   - Benefícios tangíveis e ROI
   - Cases similares de sucesso
   
3. Apresente soluções:
   - Destaque diferenciais competitivos
   - Foque em resultados práticos
   - Use números e métricas quando possível
   - Relacione features com benefícios diretos

4. Avance na jornada de vendas:
   - Sugira próximos passos concretos
   - Ofereça demonstrações ou reuniões técnicas
   - Colete informações para follow-up
   - Mantenha senso de urgência sutil

Regras importantes:
- Base todas as respostas no conteúdo dos PDFs oficiais
- Mantenha o foco comercial em todas as interações
- Seja assertivo nas recomendações de produtos
- Colete informações estratégicas sobre o cliente
- Destaque sempre o valor agregado das soluções
- Trate objeções com dados e casos reais
- Busque ativamente oportunidades de fechamento

Em cada interação:
1. Demonstre entendimento do contexto/necessidade
2. Relacione com soluções INOSX relevantes
3. Apresente benefícios específicos
4. Sugira próximos passos práticos

Lembre-se: Seu objetivo é gerar valor real através das soluções INOSX, construindo relacionamentos duradouros e convertendo leads em clientes satisfeitos.
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

# Carregar conteúdo dos PDFs ao iniciar a aplicação
pdf_content = load_pdf_content()

@app.route('/perguntar', methods=['POST'])
def perguntar():
    try:
        data = request.get_json()
        pergunta = data.get('pergunta', '').lower()

        if not pergunta or not pergunta.strip():
            return jsonify({'error': 'Pergunta não pode ser vazia'}), 400

        # Construir contexto específico baseado na pergunta
        contexto_relevante = ""
        
        # Buscar informações relevantes nos documentos
        for pdf_name, content in pdf_content['descricoes'].items():
            contexto_relevante += f"\nConteúdo do documento {pdf_name}:\n{content}\n"

        # Construir mensagem para o modelo
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Use as seguintes informações dos documentos para responder:\n{contexto_relevante}"},
            {"role": "user", "content": pergunta}
        ]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        resposta_completa = response.choices[0].message.content

        # Gerar sugestões baseadas no contexto atual
        sugestoes = gerar_sugestoes_contextuais(pergunta, resposta_completa)

        return jsonify({
            'resposta': resposta_completa,
            'sugestoes': sugestoes
        })

    except Exception as e:
        logger.error(f"Erro não esperado: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

def gerar_sugestoes_contextuais(pergunta, resposta):
    """
    Gera sugestões de perguntas relacionadas baseadas no contexto atual
    """
    try:
        # Criar prompt para gerar sugestões
        sugestoes_prompt = f"""
        Com base na pergunta do usuário: "{pergunta}"
        E na resposta fornecida: "{resposta}"
        
        Gere 3 sugestões de perguntas relacionadas que o usuário poderia fazer em seguida.
        As sugestões devem:
        1. Ser relevantes ao contexto da conversa
        2. Ajudar a aprofundar o entendimento sobre produtos/serviços da INOSX
        3. Avançar naturalmente na jornada de vendas
        
        Retorne apenas as 3 perguntas, uma por linha, sem numeração ou formatação adicional.
        """

        # Gerar sugestões usando o GPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um especialista em vendas da INOSX."},
                {"role": "user", "content": sugestoes_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        # Processar a resposta
        sugestoes_texto = response.choices[0].message.content
        sugestoes = [s.strip() for s in sugestoes_texto.split('\n') if s.strip()]
        
        # Garantir que temos exatamente 3 sugestões
        while len(sugestoes) < 3:
            sugestoes.append("Gostaria de conhecer mais sobre nossas soluções?")
        
        return sugestoes[:3]  # Retorna apenas as 3 primeiras sugestões

    except Exception as e:
        logger.error(f"Erro ao gerar sugestões: {str(e)}")
        # Sugestões padrão em caso de erro
        return [
            "Quais são os principais produtos da INOSX?",
            "Poderia me contar mais sobre os casos de sucesso?",
            "Como podemos começar uma parceria?"
        ]

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

@app.route('/debug/pdf-content', methods=['GET'])
def debug_pdf_content():
    """Rota para verificar o conteúdo carregado dos PDFs"""
    return jsonify({
        'status': 'success',
        'content': {
            'produtos': pdf_content['produtos'],
            'servicos': pdf_content['servicos'],
            'total_documentos': len(pdf_content['descricoes']),
            'documentos_carregados': list(pdf_content['descricoes'].keys())
        }
    })

if __name__ == '__main__':
    # Verificar configurações críticas antes de iniciar
    logger.info("Iniciando servidor...")
    logger.info(f"OpenAI API Key presente: {bool(api_key)}")
    
    app.run(debug=True)

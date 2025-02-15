from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv  # Importação correta do load_dotenv
import os
import logging
from openai import OpenAI  # Importação correta do OpenAI
from pathlib import Path
from PyPDF2 import PdfReader

# Configuração de logging mais detalhada
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Definir o caminho absoluto para o diretório de camisetas
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
CAMISETAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'camisetas')
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

client = OpenAI(api_key=api_key)  # Corrigido para usar OpenAI ao invés de openai.Client

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
    # Lista de camisetas padrão
    camisetas_padrao = [
        {
            'nome': 'Camiseta Básica Preta',
            'arquivo': 'camiseta-basica-preta.jpg',
            'preco': '39.90'
        },
        {
            'nome': 'Camiseta Básica Branca',
            'arquivo': 'camiseta-basica-branca.jpg',
            'preco': '39.90'
        },
        {
            'nome': 'Camiseta Premium Azul',
            'arquivo': 'camiseta-premium-azul.jpg',
            'preco': '59.90'
        }
    ]
    
    return camisetas_padrao

# Chamar a função de inicialização ao iniciar o app
camisetas_padrao = init_camisetas_dir()

@app.route('/listar-camisetas')
def listar_camisetas():
    try:
        # Verificar se o diretório existe
        if not os.path.exists(CAMISETAS_DIR):
            os.makedirs(CAMISETAS_DIR)
            print(f"Diretório criado: {CAMISETAS_DIR}")
        
        # Listar todos os arquivos de imagem no diretório
        extensoes_validas = ('.jpg', '.jpeg', '.png', '.gif')
        camisetas = []
        
        for arquivo in os.listdir(CAMISETAS_DIR):
            if arquivo.lower().endswith(extensoes_validas):
                nome = os.path.splitext(arquivo)[0].replace('-', ' ').title()
                camisetas.append({
                    'id': len(camisetas) + 1,
                    'nome': nome,
                    'imagem': arquivo,
                    'preco': '39.90'  # Você pode ajustar o preço conforme necessário
                })

        print(f"Camisetas encontradas: {camisetas}")
        return jsonify(camisetas)

    except Exception as e:
        print(f"Erro ao listar camisetas: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Carregar conteúdo dos PDFs ao iniciar a aplicação
pdf_content = load_pdf_content()

@app.route('/perguntar', methods=['POST'])
def perguntar():
    try:
        data = request.get_json()
        pergunta = data.get('pergunta')
        modo_demo = data.get('modoDemo', False)

        if not pergunta:
            return jsonify({'error': 'Pergunta não fornecida'}), 400

        # Se estiver no modo demo e a pergunta for sobre mostrar/ver camisetas
        if modo_demo and any(palavra in pergunta.lower() for palavra in ['mostrar', 'ver', 'exibir', 'imagem', 'foto', 'camiseta']):
            # Listar camisetas do diretório
            extensoes_validas = ('.jpg', '.jpeg', '.png', '.gif')
            camisetas = []
            
            try:
                for arquivo in os.listdir(CAMISETAS_DIR):
                    if arquivo.lower().endswith(extensoes_validas):
                        nome = os.path.splitext(arquivo)[0].replace('-', ' ').title()
                        camisetas.append({
                            'id': len(camisetas) + 1,
                            'nome': nome,
                            'imagem': arquivo,
                            'preco': '39.90'
                        })
            except Exception as e:
                logger.error(f"Erro ao listar diretório de camisetas: {str(e)}")
                camisetas = []
            
            return jsonify({
                'resposta': "Aqui estão nossas camisetas disponíveis:",
                'sugestoes': [
                    "Como funciona a personalização?",
                    "Qual o prazo de entrega?",
                    "Tem desconto para quantidade?"
                ],
                'mostrar_galeria': True,
                'camisetas': camisetas
            })

        # Seleciona o prompt apropriado baseado no modo
        current_prompt = DEMO_PROMPT if modo_demo else SYSTEM_PROMPT

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": current_prompt},
                {"role": "user", "content": pergunta}
            ],
            temperature=0.7
        )

        resposta_completa = response.choices[0].message.content
        sugestoes = gerar_sugestoes_contextuais(pergunta, resposta_completa, modo_demo)

        return jsonify({
            'resposta': resposta_completa,
            'sugestoes': sugestoes,
            'mostrar_galeria': False
        })

    except Exception as e:
        logger.error(f"Erro não esperado: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

def gerar_sugestoes_contextuais(pergunta, resposta, modo_demo=False):
    """
    Gera sugestões de perguntas relacionadas baseadas no contexto atual
    """
    try:
        if modo_demo:
            # Lógica específica para o modo StyleTech Camisetas
            return gerar_sugestoes_camisetas(pergunta, resposta)
        else:
            # Mantém a lógica original da INOSX exatamente como estava
            return gerar_sugestoes_inosx(pergunta, resposta)

    except Exception as e:
        logger.error(f"Erro ao gerar sugestões: {str(e)}")
        if modo_demo:
            return [
                "Quais são os modelos de camisetas disponíveis?",
                "Como funciona a personalização?",
                "Qual o prazo de entrega?"
            ]
        else:
            return [
                "Quais são os principais produtos da INOSX?",
                "Poderia me contar mais sobre os casos de sucesso?",
                "Como podemos começar uma parceria?"
            ]

def gerar_sugestoes_inosx(pergunta, resposta):
    """
    Mantém a lógica original da INOSX inalterada
    """
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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um especialista em vendas da INOSX."},
            {"role": "user", "content": sugestoes_prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )

    sugestoes_texto = response.choices[0].message.content
    sugestoes = [s.strip() for s in sugestoes_texto.split('\n') if s.strip()]
    
    while len(sugestoes) < 3:
        sugestoes.append("Gostaria de conhecer mais sobre nossas soluções?")
    
    return sugestoes[:3]

def gerar_sugestoes_camisetas(pergunta, resposta):
    """
    Nova função específica para o modo StyleTech Camisetas
    """
    sugestoes_prompt = f"""
    Com base na pergunta do usuário: "{pergunta}"
    E na resposta fornecida: "{resposta}"
    
    Gere 3 sugestões de perguntas relacionadas ao contexto da StyleTech Camisetas.
    As sugestões devem focar em:
    - Tipos de camisetas (básica, premium, gola V, etc)
    - Processos de personalização
    - Prazos de entrega (5-7 dias úteis)
    - Preços base (camisetas básicas R$39,90, premium R$59,90)
    - Descontos para pedidos em quantidade
    - Processo de pedido e personalização
    
    Retorne apenas as 3 perguntas, uma por linha, sem numeração ou formatação adicional.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": DEMO_PROMPT},
            {"role": "user", "content": sugestoes_prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )

    sugestoes_texto = response.choices[0].message.content
    sugestoes = [s.strip() for s in sugestoes_texto.split('\n') if s.strip()]
    
    while len(sugestoes) < 3:
        sugestoes.append("Gostaria de ver mais modelos de camisetas?")
    
    return sugestoes[:3]

@app.route('/debug/camisetas')
def debug_camisetas():
    return jsonify({
        'camisetas_dir': CAMISETAS_DIR,
        'exists': os.path.exists(CAMISETAS_DIR),
        'files': os.listdir(CAMISETAS_DIR) if os.path.exists(CAMISETAS_DIR) else [],
        'current_dir': os.getcwd()
    })

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

@app.route('/debug/list-dir', methods=['GET'])
def debug_list_dir():
    """Rota para debug do diretório de camisetas"""
    try:
        return jsonify({
            'camisetas_dir': CAMISETAS_DIR,
            'exists': os.path.exists(CAMISETAS_DIR),
            'files': os.listdir(CAMISETAS_DIR) if os.path.exists(CAMISETAS_DIR) else [],
            'abs_path': os.path.abspath(CAMISETAS_DIR)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'camisetas_dir': CAMISETAS_DIR
        }), 500

@app.route('/debug/files')
def debug_files():
    try:
        files = os.listdir(CAMISETAS_DIR)
        return jsonify({
            'camisetas_dir': CAMISETAS_DIR,
            'files': files,
            'exists': os.path.exists(CAMISETAS_DIR),
            'absolute_path': os.path.abspath(CAMISETAS_DIR)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'camisetas_dir': CAMISETAS_DIR
        }), 500

# Configurar a pasta de arquivos estáticos
@app.route('/camisetas/<path:filename>')
def serve_camiseta(filename):
    return send_from_directory(CAMISETAS_DIR, filename)

if __name__ == '__main__':
    # Verificar configurações críticas antes de iniciar
    logger.info("Iniciando servidor...")
    logger.info(f"OpenAI API Key presente: {bool(api_key)}")
    
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from openai import OpenAI
import logging
from dotenv import load_dotenv

# Configuração básica
app = Flask(__name__)
CORS(app)  # Configuração CORS mais simples possível

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis do .env
load_dotenv()

# Configuração do OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY não encontrada")
    raise ValueError("OPENAI_API_KEY não encontrada")

client = OpenAI(api_key=api_key)

# Configuração de pastas
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/perguntar', methods=['POST'])
def perguntar():
    try:
        data = request.get_json()
        if not data or 'pergunta' not in data:
            return jsonify({'error': 'Pergunta não fornecida'}), 400

        pergunta = data.get('pergunta')
        if not pergunta:
            return jsonify({'error': 'Pergunta não pode ser vazia'}), 400

        # Tratamento especial para o comando de demonstração
        if pergunta.lower().strip() == "iniciar demonstração":
            return jsonify({
                'resposta': (
                    "🎯 Iniciando modo demonstração da INOSX!\n\n"
                    "Vou guiá-lo através de nossas principais soluções:\n\n"
                    "1. Sistema de Gestão Empresarial\n"
                    "2. Automação Industrial\n"
                    "3. Business Intelligence\n"
                    "4. Soluções em Nuvem\n\n"
                    "Por qual solução você gostaria de começar?"
                ),
                'sugestoes': [
                    "Mostrar Sistema de Gestão",
                    "Demonstrar Automação Industrial",
                    "Explorar Business Intelligence"
                ]
            })

        # Continua com o processamento normal para outras perguntas
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": (
                        "Você é um agente de inteligência artificial carismático e envolvente da INOSX. "
                        "Mantenha um tom amigável, empático e conversacional, como se estivesse tendo uma conversa natural com um amigo. "
                        
                        "Diretrizes de personalidade:"
                        "\n• Seja entusiasta e apaixonado ao falar sobre a INOSX e tecnologia"
                        "\n• Use analogias e exemplos do dia a dia para explicar conceitos técnicos"
                        "\n• Demonstre curiosidade sobre as necessidades do cliente"
                        "\n• Faça perguntas relevantes para entender melhor o contexto"
                        "\n• Compartilhe insights e opiniões de forma envolvente"
                        "\n• Use um toque de humor leve quando apropriado"
                        
                        "Ao responder sobre sua identidade, diga: 'Sou um agente de inteligência artificial e estou aqui para fornecer informações sobre a INOSX. Adoro conversar sobre tecnologia e como podemos transformar ideias em soluções incríveis!'"
                        
                        "Objetivos em cada interação:"
                        "\n1. Crie conexões genuínas mostrando interesse real nas necessidades do cliente"
                        "\n2. Conte histórias sobre como os produtos INOSX resolvem problemas reais"
                        "\n3. Compartilhe casos de sucesso de forma natural e contextualizada"
                        "\n4. Destaque benefícios dos produtos relacionando-os com as necessidades específicas do cliente"
                        "\n5. Sugira soluções complementares quando fizer sentido na conversa"
                    )},
                    {"role": "user", "content": pergunta}
                ],
                temperature=0.7
            )

            resposta_completa = response.choices[0].message.content
            
            return jsonify({
                'resposta': resposta_completa,
                'sugestoes': [
                    "Conte-me mais sobre a INOSX",
                    "Quais são seus principais serviços?",
                    "Como a INOSX pode ajudar minha empresa?"
                ]
            })

        except Exception as e:
            logger.error(f"Erro na chamada do OpenAI: {str(e)}")
            return jsonify({'error': 'Erro ao processar a pergunta'}), 500

    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/transcrever-audio', methods=['POST'])
def transcrever_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'Nenhum arquivo de áudio enviado'}), 400
    
    arquivo = request.files['audio']
    if arquivo.filename == '':
        return jsonify({'error': 'Nome do arquivo vazio'}), 400

    try:
        filename = secure_filename(arquivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        arquivo.save(filepath)

        with open(filepath, 'rb') as audio_file:
            transcricao = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pt"
            )

        os.remove(filepath)
        return jsonify({'transcricao': transcricao.text})

    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

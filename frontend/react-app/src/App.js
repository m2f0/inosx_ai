import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { 
  FaRobot, 
  FaPaperPlane, 
  FaQuestion, 
  FaLightbulb, 
  FaInfoCircle, 
  FaTools, 
  FaCode, 
  FaCog, 
  FaVolumeUp, 
  FaVolumeMute, 
  FaMicrophone, 
  FaStop 
} from "react-icons/fa";

// Configuração do Axios
axios.defaults.baseURL = 'http://localhost:5000';
axios.defaults.headers.post['Content-Type'] = 'application/json';

function App() {
  const [pergunta, setPergunta] = useState("");
  const [respostas, setRespostas] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [modoDemo, setModoDemo] = useState(false); // Novo estado
  const [audioBlob, setAudioBlob] = useState(null);
  const chatContainerRef = useRef(null);
  const speechSynthesis = window.speechSynthesis;
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  // Função para limpar o texto de tags HTML
  const stripHtml = (html) => {
    const tmp = document.createElement("DIV");
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || "";
  };

  // Função para ler o texto
  const speak = (texto) => {
    if (isSpeaking) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const textoLimpo = stripHtml(texto);
    const utterance = new SpeechSynthesisUtterance(textoLimpo);
    
    utterance.onend = () => {
      setIsSpeaking(false);
    };

    setIsSpeaking(true);
    speechSynthesis.speak(utterance);
  };

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      setTimeout(() => {
        chatContainerRef.current.scrollTo({
          top: chatContainerRef.current.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [respostas, isLoading]);

  const enviarPergunta = async (perguntaEnviada = pergunta) => {
    if (!perguntaEnviada.trim()) return;

    // Verifica se está ativando o modo demo
    if (perguntaEnviada.toLowerCase().trim() === 'modo de demonstração' || 
        perguntaEnviada.toLowerCase().trim() === 'iniciar demonstração') {
      setModoDemo(true);
    }

    const novaMensagem = { tipo: "user", texto: perguntaEnviada };
    setRespostas(prev => [...prev, novaMensagem]);
    setPergunta("");
    setIsLoading(true);

    try {
      const res = await axios.post("http://localhost:5000/perguntar", { 
        pergunta: perguntaEnviada 
      });
      
      const novaResposta = { 
        tipo: "bot", 
        texto: formatarResposta(res.data.resposta),
        sugestoes: res.data.sugestoes
      };
      
      setRespostas(prev => [...prev, novaResposta]);
    } catch (error) {
      console.error("Erro ao obter resposta", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      enviarPergunta();
    }
  };

  const formatarResposta = (texto) => {
    return texto
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/- (.*?)\n/g, '<li class="mb-2">$1</li>')
      .replace(/\n/g, '<br>');
  };

  const getButtonIcon = (index) => {
    const icons = [
      <FaLightbulb className="mr-2" />,
      <FaInfoCircle className="mr-2" />,
      <FaQuestion className="mr-2" />,
      <FaTools className="mr-2" />,
      <FaCode className="mr-2" />,
      <FaCog className="mr-2" />
    ];
    return icons[index % icons.length];
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        await handleAudioSubmission(audioBlob);
        
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Erro ao iniciar gravação:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleAudioSubmission = async (blob) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', blob, 'audio.wav');

      const response = await axios.post('/transcrever-audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });

      if (response.data.transcricao) {
        await enviarPergunta(response.data.transcricao);
      }
    } catch (error) {
      console.error("Erro ao enviar áudio:", error);
      setRespostas(prev => [...prev, {
        tipo: "bot",
        texto: "Desculpe, ocorreu um erro ao processar o áudio. Por favor, tente novamente.",
        sugestoes: []
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white flex-col">
      {/* Cabeçalho */}
      <div className="p-4 bg-gray-800 flex justify-between items-center">
        <h2 className="text-lg">INOSX AI</h2>
        {modoDemo && (
          <div className="flex items-center">
            <span className="mr-2">👕</span>
            <span className="text-sm">Modo Demo: StyleTech Camisetas</span>
            <button 
              onClick={() => {
                setModoDemo(false);
                setRespostas([]);
              }}
              className="ml-4 text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded"
            >
              Sair do Demo
            </button>
          </div>
        )}
      </div>

      <div 
        ref={chatContainerRef}
        className="flex-1 p-4 overflow-y-auto space-y-4"
        style={{
          scrollBehavior: 'smooth',
          maxHeight: 'calc(100vh - 140px)'
        }}
      >
        {respostas.map((msg, msgIndex) => (
          <div key={msgIndex} className="space-y-2">
            <div
              className={`p-4 rounded-lg max-w-2xl ${
                msg.tipo === "user"
                  ? "bg-blue-600 ml-auto text-white"
                  : "bg-gray-700 text-gray-300 border-l-4 border-blue-400"
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-grow">
                  {msg.tipo === "bot" ? (
                    <div dangerouslySetInnerHTML={{ __html: `<ul class="list-disc pl-5">${msg.texto}</ul>` }} />
                  ) : (
                    msg.texto
                  )}
                </div>
                {msg.tipo === "bot" && (
                  <button
                    onClick={() => speak(msg.texto)}
                    className={`ml-2 p-2 rounded-full hover:bg-gray-600 transition-colors ${
                      isSpeaking ? 'text-blue-400' : 'text-gray-400'
                    }`}
                  >
                    {isSpeaking ? <FaVolumeMute size={20} /> : <FaVolumeUp size={20} />}
                  </button>
                )}
              </div>
            </div>
            
            {msg.tipo === "bot" && msg.sugestoes && msg.sugestoes.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {msg.sugestoes.map((sugestao, sugestaoIndex) => (
                  <button
                    key={`${msgIndex}-${sugestaoIndex}`}
                    onClick={() => enviarPergunta(sugestao)}
                    className={`
                      px-4 py-2 rounded-full
                      text-sm font-medium
                      flex items-center gap-2
                      transition-colors
                      ${sugestaoIndex % 3 === 0 ? 'bg-blue-600 hover:bg-blue-700' : 
                        sugestaoIndex % 3 === 1 ? 'bg-purple-600 hover:bg-purple-700' : 
                        'bg-teal-600 hover:bg-teal-700'}
                    `}
                  >
                    {getButtonIcon(sugestaoIndex)}
                    <span>{sugestao}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Pensando...</span>
          </div>
        )}
      </div>

      <div className="p-4 bg-gray-800">
        <div className="max-w-4xl mx-auto flex items-center gap-2">
          <input
            type="text"
            value={pergunta}
            className="flex-1 p-2 rounded bg-gray-700 text-white"
            placeholder="Digite sua mensagem..."
            onChange={(e) => setPergunta(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={isLoading || isRecording}
          />
            
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`ml-2 p-2 rounded transition-colors ${
              isRecording 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-gray-600 hover:bg-gray-700'
            }`}
            disabled={isLoading}
          >
            {isRecording ? <FaStop /> : <FaMicrophone />}
          </button>

          <button 
            onClick={() => enviarPergunta()}
            className={`ml-2 p-2 rounded transition-colors ${
              isLoading 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
            disabled={isLoading || isRecording}
          >
            <FaPaperPlane />
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { FaRobot, FaPaperPlane, FaQuestion, FaLightbulb, FaInfoCircle, FaTools, FaCode, FaCog, FaVolumeUp, FaVolumeMute, FaMicrophone, FaStop } from "react-icons/fa";

function App() {
  const [pergunta, setPergunta] = useState("");
  const [respostas, setRespostas] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
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
    // Se já estiver falando, para a fala atual
    if (isSpeaking) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    // Limpa o texto de tags HTML
    const textoLimpo = stripHtml(texto);
    
    const utterance = new SpeechSynthesisUtterance(textoLimpo);
    utterance.lang = 'pt-BR';
    utterance.rate = 1.5; // Velocidade aumentada
    utterance.pitch = 1.2; // Tom mais agudo

    // Seleciona uma voz feminina em português
    const voices = speechSynthesis.getVoices();
    
    // Lista de nomes de vozes femininas conhecidas em português
    const femaleVoiceNames = [
      'Microsoft Maria',
      'Google português do Brasil',
      'Luciana',
      'Helena',
      'Francisca',
      'pt-BR-Standard-Female',
      'Brazilian Portuguese Female'
    ];

    // Tenta encontrar uma das vozes femininas
    const femaleVoice = voices.find(voice => 
      voice.lang.includes('pt') && 
      femaleVoiceNames.some(name => 
        voice.name.toLowerCase().includes(name.toLowerCase())
      )
    );

    // Se encontrou uma voz feminina, usa ela
    if (femaleVoice) {
      utterance.voice = femaleVoice;
    } else {
      // Se não encontrou, tenta qualquer voz em português
      const ptVoice = voices.find(voice => voice.lang.includes('pt'));
      if (ptVoice) {
        utterance.voice = ptVoice;
      }
    }

    // Para debug - mostra as vozes disponíveis no console
    console.log('Vozes disponíveis:', voices.map(v => `${v.name} (${v.lang})`));
    console.log('Voz selecionada:', utterance.voice?.name);

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
        sugestoes: res.data.sugestoes // Armazenando as sugestões junto com a resposta
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
    // Array de ícones que serão alternados
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

  // useEffect para garantir que as vozes sejam carregadas
  useEffect(() => {
    const loadVoices = () => {
      const voices = speechSynthesis.getVoices();
      console.log('Vozes carregadas:', voices.map(v => `${v.name} (${v.lang})`));
    };

    loadVoices();
    
    speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      speechSynthesis.onvoiceschanged = null;
    };
  }, []);

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
        
        // Parar todos os tracks do stream
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
      // Criar FormData com o arquivo de áudio
      const formData = new FormData();
      formData.append('audio', blob, 'audio.wav');

      // Enviar para o backend
      const response = await axios.post('http://localhost:5000/transcrever-audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Se recebeu a transcrição com sucesso, envia como pergunta
      if (response.data.transcricao) {
        await enviarPergunta(response.data.transcricao);
      }
    } catch (error) {
      console.error("Erro ao enviar áudio:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white flex-col">
      {/* Cabeçalho */}
      <div className="p-4 bg-gray-800 flex justify-center">
        <h2 className="text-lg">INOSX AI</h2>
      </div>

      {/* Área do Chat */}
      <div 
        ref={chatContainerRef}
        className="flex-1 p-4 overflow-y-auto space-y-4"
        style={{
          scrollBehavior: 'smooth',
          maxHeight: 'calc(100vh - 140px)' // Altura total - header - input
        }}
      >
        {respostas.map((msg, index) => (
          <div key={index} className="space-y-2">
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
            
            {/* Botões de sugestão dinâmicos */}
            {msg.tipo === "bot" && msg.sugestoes && msg.sugestoes.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {msg.sugestoes.map((sugestao, idx) => (
                  <button
                    key={idx}
                    onClick={() => enviarPergunta(sugestao)}
                    className={`
                      border-2 
                      ${idx % 3 === 0 ? 'border-blue-500 text-blue-500 hover:bg-blue-50' : 
                        idx % 3 === 1 ? 'border-purple-500 text-purple-500 hover:bg-purple-50' : 
                        'border-teal-500 text-teal-500 hover:bg-teal-50'}
                      bg-transparent 
                      text-sm 
                      px-4 
                      py-1.5 
                      rounded-full 
                      transition-colors
                      font-medium
                      flex
                      items-center
                      justify-center
                    `}
                    disabled={isLoading}
                  >
                    {getButtonIcon(idx)}
                    <span>{sugestao}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        
        {/* Indicador de Loading */}
        {isLoading && (
          <div className="flex items-center space-x-2 p-4 rounded-lg max-w-2xl bg-gray-700 text-gray-300 border-l-4 border-blue-400">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-sm text-gray-400">INOSX está pensando...</span>
          </div>
        )}
        
        <div className="h-4" />
      </div>

      {/* Input de Pergunta */}
      <div className="p-4 bg-gray-800 flex">
        <input
          type="text"
          className="flex-1 p-2 bg-gray-700 rounded text-white"
          placeholder="Digite sua pergunta..."
          value={pergunta}
          onChange={(e) => setPergunta(e.target.value)}
          onKeyDown={handleKeyPress} // 🔹 Captura o "Enter"
          disabled={isLoading || isRecording}
        />
        
        {/* Botão de Gravação */}
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

        {/* Botão de Envio */}
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
  );
}

export default App;

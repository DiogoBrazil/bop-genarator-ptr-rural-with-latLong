import streamlit as st
from openai import OpenAI
from datetime import datetime
import streamlit.components.v1 as components

# Configurar cliente OpenAI usando secrets do Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def obter_localizacao():
    """Função para obter localização em tempo real com alta precisão"""
    html_code = """
    <div style="padding: 15px; border: 2px solid #0066cc; border-radius: 10px; margin: 15px 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);">
        <h4 style="margin-top: 0; color: #0066cc;">📍 Obter Localização de Alta Precisão</h4>
        
        <div style="margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
            <button onclick="getHighPrecisionLocation()" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.37);
                flex: 1 1 auto; /* Responsividade */
                min-width: 180px; /* Largura mínima */
                text-align: center;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                🎯 Localização de Alta Precisão
            </button>
            
            <button onclick="getQuickLocation()" style="
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 4px 15px 0 rgba(76, 175, 80, 0.37);
                flex: 1 1 auto; /* Responsividade */
                min-width: 180px; /* Largura mínima */
                text-align: center;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                ⚡ Localização Rápida
            </button>
            
            <button onclick="clearLocation()" style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 4px 15px 0 rgba(245, 87, 108, 0.37);
                flex: 1 1 auto; /* Responsividade */
                min-width: 120px; /* Largura mínima para botão menor */
                text-align: center;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                🗑️ Limpar
            </button>
        </div>
        
        <div id="status" style="margin-top: 15px; font-weight: bold; font-size: 14px;"></div>
        <div id="coordinates" style="margin-top: 15px; display: none;"></div>
        
    </div>

    <script>
    let currentCoords = null;
    let watchId = null;
    let bestAccuracy = Infinity;
    let attempts = 0;
    let maxAttempts = 10;
    
    function getHighPrecisionLocation() {
        const status = document.getElementById("status");
        const coordinates = document.getElementById("coordinates");
        
        if (!navigator.geolocation) {
            status.innerHTML = "❌ Geolocalização não é suportada por este navegador.";
            status.style.color = "#dc3545";
            return;
        }
        
        bestAccuracy = Infinity;
        attempts = 0;
        currentCoords = null;
        
        status.innerHTML = "🎯 Iniciando localização de alta precisão... Aguarde até 60 segundos.";
        status.style.color = "#007bff";
        coordinates.style.display = "none";
        
        watchId = navigator.geolocation.watchPosition(
            function(position) {
                attempts++;
                const accuracy = position.coords.accuracy;
                
                status.innerHTML = `🔄 Tentativa ${attempts}/${maxAttempts} - Precisão: ±${Math.round(accuracy)}m`;
                
                if (accuracy < bestAccuracy && (accuracy < 10 || attempts >= maxAttempts)) {
                    bestAccuracy = accuracy;
                    processPosition(position, true);
                    if (watchId) navigator.geolocation.clearWatch(watchId); // Adicionado if para segurança
                    watchId = null;
                } else if (attempts >= maxAttempts) {
                    processPosition(position, true);
                    if (watchId) navigator.geolocation.clearWatch(watchId); // Adicionado if para segurança
                    watchId = null;
                }
            },
            handleLocationError,
            {
                enableHighAccuracy: true,
                timeout: 60000,
                maximumAge: 0
            }
        );
        
        setTimeout(() => {
            if (watchId) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
                if (currentCoords) { // Se já processou uma posição antes do timeout
                    status.innerHTML = `✅ Localização obtida! (Melhor esforço após timeout)`;
                } else {
                    status.innerHTML = "⏰ Tempo limite. Tente em área mais aberta ou use localização rápida.";
                    status.style.color = "#ff9800";
                }
            }
        }, 60000);
    }
    
    function getQuickLocation() {
        const status = document.getElementById("status");
        
        if (!navigator.geolocation) {
            status.innerHTML = "❌ Geolocalização não é suportada por este navegador.";
            status.style.color = "#dc3545";
            return;
        }
        
        status.innerHTML = "⚡ Obtendo localização rápida...";
        status.style.color = "#28a745";
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                processPosition(position, false);
            },
            handleLocationError,
            {
                enableHighAccuracy: true, // Mantido true para melhor "rápida" possível
                timeout: 15000, // Aumentado um pouco o timeout para rápida
                maximumAge: 60000 // Aceitar posições armazenadas em cache por até 1 minuto
            }
        );
    }
    
    function processPosition(position, isHighPrecision) {
        const status = document.getElementById("status");
        const coordinates = document.getElementById("coordinates");
        
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        const accuracy = position.coords.accuracy;
        const timestamp = new Date(position.timestamp);
        
        currentCoords = {
            lat: lat.toFixed(8),
            lng: lng.toFixed(8),
            formatted: `${lat.toFixed(8)}, ${lng.toFixed(8)}`,
            accuracy: accuracy
        };
        
        let precisionLevel = "";
        let precisionColor = "";
        
        if (accuracy <= 5) {
            precisionLevel = "🎯 EXCELENTE";
            precisionColor = "#28a745";
        } else if (accuracy <= 10) {
            precisionLevel = "✅ MUITO BOA";
            precisionColor = "#28a745";
        } else if (accuracy <= 50) {
            precisionLevel = "👍 BOA";
            precisionColor = "#ffc107";
        } else if (accuracy <= 100) {
            precisionLevel = "⚠️ REGULAR";
            precisionColor = "#ff9800";
        } else {
            precisionLevel = "❌ BAIXA";
            precisionColor = "#dc3545";
        }
        
        // A mensagem de status agora inclui o nível de precisão.
        status.innerHTML = `✅ Localização obtida! Nível: ${precisionLevel} (±${Math.round(accuracy)}m)`;
        status.style.color = precisionColor;
        
        coordinates.innerHTML = `
            <div style="
                background: rgba(255,255,255,0.95); 
                padding: 20px; 
                border-radius: 12px; 
                border-left: 5px solid ${precisionColor};
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                margin-top: 15px;
            ">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div>
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">📍 LATITUDE</div>
                        <div style="font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; color: #333;">${lat.toFixed(8)}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">📍 LONGITUDE</div>
                        <div style="font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; color: #333;">${lng.toFixed(8)}</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <button onclick="copyCoords()" style="
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        border: none;
                        padding: 12px 16px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
                        transition: all 0.3s;
                    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        📋 Copiar Coordenadas
                    </button>
                    
                    <button onclick="openMaps()" style="
                        background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
                        color: white;
                        border: none;
                        padding: 12px 16px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                        box-shadow: 0 4px 12px rgba(111, 66, 193, 0.3);
                        transition: all 0.3s;
                    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        🗺️ Ver no Mapa
                    </button>
                </div>
            </div>
        `;
        
        coordinates.style.display = "block";
        
        sessionStorage.setItem('gps_coords', currentCoords.formatted);
        sessionStorage.setItem('gps_accuracy', accuracy.toString());
        sessionStorage.setItem('gps_timestamp', timestamp.toISOString());
    }
    
    function handleLocationError(error) {
        const status = document.getElementById("status");
        const coordinates = document.getElementById("coordinates"); // Certifique-se de que coordinates é manipulado
        
        let errorMsg = "";
        let suggestions = "";
        
        switch(error.code) {
            case error.PERMISSION_DENIED:
                errorMsg = "❌ Acesso à localização negado.";
                suggestions = "💡 Permita acesso nas configurações do navegador.";
                break;
            case error.POSITION_UNAVAILABLE:
                errorMsg = "❌ Localização não disponível.";
                suggestions = "💡 Verifique se GPS está ativo e tente ao ar livre.";
                break;
            case error.TIMEOUT:
                errorMsg = "❌ Tempo limite excedido.";
                suggestions = "💡 Tente localização rápida ou mova para área aberta.";
                break;
            default:
                errorMsg = "❌ Erro desconhecido ao obter localização.";
                suggestions = "💡 Recarregue a página e tente novamente.";
                break;
        }
        
        status.innerHTML = errorMsg + "<br><span style='font-size: 12px; color: #777;'>" + suggestions + "</span>";
        status.style.color = "#dc3545";
        if (coordinates) { // Adicionado para segurança
            coordinates.style.display = "none";
        }
    }
    
    function copyCoords() {
        if (currentCoords && currentCoords.formatted) {
            navigator.clipboard.writeText(currentCoords.formatted).then(function() {
                const button = event.target; // Assume event is available
                const originalText = button.innerHTML;
                button.innerHTML = "✅ Copiado!";
                button.style.background = "linear-gradient(135deg, #17a2b8 0%, #138496 100%)";
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.style.background = "linear-gradient(135deg, #28a745 0%, #20c997 100%)"; // Restore original background
                }, 2000);
                
            }).catch(function(err) {
                console.error('Erro ao copiar para clipboard: ', err);
                // Fallback para prompt se a API de clipboard falhar (ex: em HTTP ou sem permissão)
                prompt('Não foi possível copiar automaticamente. Copie manualmente:', currentCoords.formatted);
            });
        } else {
            // Informar ao usuário que não há coordenadas para copiar
            const status = document.getElementById("status");
            if(status) { // Adicionado para segurança
                const originalStatusText = status.innerHTML;
                const originalStatusColor = status.style.color;
                status.innerHTML = "📋 Nenhuma coordenada para copiar. Obtenha a localização primeiro.";
                status.style.color = "#ff9800"; // Laranja para aviso
                setTimeout(() => {
                    status.innerHTML = originalStatusText;
                    status.style.color = originalStatusColor;
                }, 3000);
            }
        }
    }
    
    function openMaps() {
        if (currentCoords && currentCoords.lat && currentCoords.lng) {
            const mapsUrl = `https://www.google.com/maps?q=${currentCoords.lat},${currentCoords.lng}`;
            window.open(mapsUrl, '_blank');
        } else {
            // Informar ao usuário que não há coordenadas para abrir no mapa
             const status = document.getElementById("status");
            if(status) { // Adicionado para segurança
                const originalStatusText = status.innerHTML;
                const originalStatusColor = status.style.color;
                status.innerHTML = "🗺️ Nenhuma coordenada para ver no mapa. Obtenha a localização primeiro.";
                status.style.color = "#ff9800"; // Laranja para aviso
                setTimeout(() => {
                    status.innerHTML = originalStatusText;
                    status.style.color = originalStatusColor;
                }, 3000);
            }
        }
    }
    
    function clearLocation() {
        if (watchId) {
            navigator.geolocation.clearWatch(watchId);
            watchId = null;
        }
        const statusDiv = document.getElementById("status");
        const coordinatesDiv = document.getElementById("coordinates");

        if (statusDiv) statusDiv.innerHTML = "🗑️ Localização limpa.";
        if (coordinatesDiv) coordinatesDiv.style.display = "none";
        
        currentCoords = null;
        bestAccuracy = Infinity;
        attempts = 0;
        
        sessionStorage.removeItem('gps_coords');
        sessionStorage.removeItem('gps_accuracy');
        sessionStorage.removeItem('gps_timestamp');

        // Limpar a mensagem após um tempo
        setTimeout(() => {
            if (statusDiv && statusDiv.innerHTML === "🗑️ Localização limpa.") {
                statusDiv.innerHTML = "";
            }
        }, 2000);
    }
    </script>
    """
    
    components.html(html_code, height=320) # Ajustei a altura ligeiramente, pode precisar de mais testes

def criar_botao_preencher_coords(campo_nome):
    """Criar botão para preencher coordenadas automaticamente"""
    button_html = f"""
    <button 
        onclick="preencherCampo_{campo_nome}()" 
        style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 5px;
            width: 100%;
            box-shadow: 0 2px 10px rgba(79, 172, 254, 0.3);
        "
        onmouseover="this.style.transform='scale(1.02)'"
        onmouseout="this.style.transform='scale(1)'"
    >
        📍 Usar Localização Capturada
    </button>
    
    <script>
        function preencherCampo_{campo_nome}() {{
            const coords = sessionStorage.getItem('gps_coords');
            if (coords) {{
                // Lógica para encontrar o campo de input específico.
                // Esta lógica pode precisar ser mais robusta dependendo da estrutura do seu app Streamlit.
                // O seletor abaixo tenta encontrar um input com um placeholder específico.
                // Se você tiver IDs ou classes mais confiáveis, use-os.
                let targetInput = null;
                const inputs = Array.from(document.querySelectorAll('input[type="text"], textarea'));

                // Tenta encontrar o input associado ao st.text_input ou st.text_area
                // A heurística abaixo busca pelo input que visualmente está próximo ou
                // tem um label correspondente ao campo_nome.
                // Esta é uma parte difícil de generalizar sem IDs fixos.
                // Uma abordagem mais simples, se os campos são sempre na mesma ordem:
                // const porteiraInput = inputs.find(inp => inp.placeholder && inp.placeholder.includes("porteira"));
                // const sedeInput = inputs.find(inp => inp.placeholder && inp.placeholder.includes("sede"));

                let placeholderQuery = "";
                if ('{campo_nome}' === 'porteira') {{
                    placeholderQuery = "porteira";
                }} else if ('{campo_nome}' === 'sede') {{
                    placeholderQuery = "sede";
                }}

                // Tenta encontrar por placeholder se definido
                if (placeholderQuery) {{
                    targetInput = inputs.find(input => input.placeholder && input.placeholder.toLowerCase().includes(placeholderQuery));
                }}

                // Fallback se não encontrar por placeholder específico (pega o primeiro campo de coordenadas visível)
                if (!targetInput) {{
                     targetInput = inputs.find(input => input.placeholder && input.placeholder.toLowerCase().includes("lat, long") && input.offsetParent !== null);
                }}
                
                if (targetInput) {{
                    targetInput.value = coords;
                    // Simular input para Streamlit reconhecer a mudança
                    const event = new Event('input', {{ bubbles: true }});
                    targetInput.dispatchEvent(event);
                    // Alguns apps Streamlit reagem melhor a 'change' ou precisam de um blur/focus
                    const changeEvent = new Event('change', {{ bubbles: true }});
                    targetInput.dispatchEvent(changeEvent);
                    targetInput.focus(); // Para feedback visual
                    
                    // Feedback ao usuário
                    const feedbackSpan = document.createElement('span');
                    feedbackSpan.textContent = ' ✅ Preenchido!';
                    feedbackSpan.style.color = 'green';
                    feedbackSpan.style.fontSize = '12px';
                    event.target.parentNode.insertBefore(feedbackSpan, event.target.nextSibling);
                    setTimeout(() => feedbackSpan.remove(), 2000);

                }} else {{
                    alert('⚠️ Campo de destino não encontrado. Cole manualmente: ' + coords);
                }}
            }} else {{
                alert('❌ Nenhuma localização capturada. Use o widget de localização primeiro.');
            }}
        }}
    </script>
    """
    
    components.html(button_html, height=55)


def criar_botao_copiar(texto):
    """Criar botão customizado para copiar texto"""
    texto_escapado = texto.replace('`', '\\`').replace('"', '\\"').replace("'", "\\'")
    
    button_html = f"""
    <div style="margin: 10px 0;">
        <button 
            id="customCopyButton"
            onclick="copyToClipboard_{texto_escapado[:10].replace(' ','_')}()" 
            style="
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(238, 90, 36, 0.4);
            "
            onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(238, 90, 36, 0.6)'"
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(238, 90, 36, 0.4)'"
        >
            📋 Copiar Texto Completo
        </button>
    </div>
    
    <script>
        function copyToClipboard_{texto_escapado[:10].replace(' ','_')}() {{
            const textToCopy = `{texto_escapado}`;
            const button = document.getElementById("customCopyButton");
            const originalButtonText = button.innerHTML;

            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(textToCopy).then(function() {{
                    button.innerHTML = '✅ Texto Copiado!';
                    button.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'; // Verde sucesso
                    setTimeout(function() {{
                        button.innerHTML = originalButtonText;
                        button.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)'; // Restaura cor original
                    }}, 2000);
                }}, function(err) {{
                    console.error('Erro ao copiar para clipboard: ', err);
                    // Fallback para método execCommand
                    fallbackCopyTextToClipboard(textToCopy, button, originalButtonText);
                }});
            }} else {{
                // Fallback para navegadores sem navigator.clipboard
                fallbackCopyTextToClipboard(textToCopy, button, originalButtonText);
            }}
        }}

        function fallbackCopyTextToClipboard(text, button, originalButtonText) {{
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";  // Prevenir scroll
            textArea.style.top = "-9999px";    // Mover para fora da tela
            textArea.style.left = "-9999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {{
                const successful = document.execCommand('copy');
                if (successful) {{
                    button.innerHTML = '✅ Texto Copiado! (fallback)';
                    button.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                }} else {{
                    button.innerHTML = '❌ Falha ao Copiar (fallback)';
                    button.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)'; // Vermelho erro
                    prompt("Falha ao copiar. Por favor, copie manualmente:", text);
                }}
            }} catch (err) {{
                console.error('Erro no fallback execCommand: ', err);
                button.innerHTML = '❌ Falha Crítica ao Copiar';
                button.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
                prompt("Falha crítica ao copiar. Por favor, copie manualmente:", text);
            }}
            document.body.removeChild(textArea);
            setTimeout(function() {{
                button.innerHTML = originalButtonText;
                button.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)';
            }}, 3000);
        }}
    </script>
    """
    
    components.html(button_html, height=80)


def refinar_texto_com_openai(texto):
    """Função para refinar o texto usando OpenAI GPT"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em correção gramatical, coesão e coerência de textos oficiais da Polícia Militar. Corrija apenas erros gramaticais, melhore a coesão e coerência do texto, mantendo o formato original e o tom formal. Não altere informações factuais ou dados específicos."
                },
                {
                    "role": "user",
                    "content": f"Por favor, corrija este relatório policial mantendo todas as informações originais, apenas melhorando a gramática, coesão e coerência:\n\n{texto}"
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao conectar com OpenAI: {str(e)}")
        return texto

def gerar_historico(dados):
    """Função para gerar o histórico baseado no template"""
    
    template = f"""Em atendimento à Ordem de Serviço, vinculada ao Programa de Segurança Rural no Vale do Jamari, foi realizada uma visita técnica em {dados['data']}, com início às {dados['hora_inicio']} e término às {dados['hora_fim']}. A diligência ocorreu na propriedade rural denominada {dados['tipo_propriedade']} "{dados['nome_propriedade']}", situada em {dados['endereco']}, na Zona Rural do município de {dados['municipio']}/{dados['uf']}. Procedeu-se ao levantamento das coordenadas geográficas, sendo a porteira de acesso principal localizada em {dados['lat_long_porteira']}, e a sede/residência principal em {dados['lat_long_sede']}. A área total da propriedade compreende {dados['area']} {dados['unidade_area']}. O proprietário, Sr. "{dados['nome_proprietario']}", inscrito no CPF/CNPJ sob o nº "{dados['cpf_cnpj']}", com contato telefônico principal "{dados['telefone']}", esteve presente durante a visita. A principal atividade econômica desenvolvida no local é "{dados['atividade_principal']}"."""
    
    if dados['veiculos']:
        template += f" Foram identificados os seguintes veículos automotores na propriedade: {dados['veiculos']}."
    
    if dados['marca_gado']:
        template += f" O rebanho possui marca/sinal/ferro registrado como \"{dados['marca_gado']}\"."
    
    template += f""" A visita teve como objetivo central o cadastro e georreferenciamento da propriedade no sistema do Programa de Segurança Rural, o que foi efetivado. Consequentemente, foi afixada a placa de identificação do programa, de nº "{dados['numero_placa']}", entregue via mídia digital. Adicionalmente, foram repassadas ao proprietário orientações concernentes ao programa mencionado, a fim de sanar as dúvidas existentes. A presente visita cumpriu os objetivos estabelecidos pela referida Ordem de Serviço, sendo as informações coletadas e registradas com base nas declarações do proprietário e na verificação in loco."""
    
    return template

def main():
    st.set_page_config(
        page_title="Gerador de Histórico Policial - Segurança Rural",
        page_icon="🚔",
        layout="wide"
    )
    
    st.title("🚔 Gerador de Histórico Policial")
    st.subheader("Programa de Segurança Rural - Vale do Jamari")
    
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("⚠️ API Key da OpenAI não configurada! Configure no arquivo .streamlit/secrets.toml")
        st.stop()
    
    with st.sidebar:
        st.header("📋 Instruções")
        st.write("1. **📍 Localização**: Use os botões '🎯 Alta Precisão' ou '⚡ Rápida' para obter coordenadas GPS.")
        st.write("2. Preencha todos os campos obrigatórios.")
        st.write("3. Campos opcionais: veículos e marca de gado.")
        st.write("4. Clique em '🚀 Gerar Histórico'.")
        st.write("5. O texto será refinado automaticamente pela IA.")
        st.write("6. Use o botão '📋 Copiar Texto Completo' ou '💾 Baixar como TXT'.")
        
        st.header("🔧 Dicas de Precisão GPS")
        st.write("📱 **No celular**: Permita acesso à localização quando solicitado pelo navegador.")
        st.write("🌍 **GPS**: Funciona melhor ao ar livre com visão clara do céu.")
        st.write("⏰ **Paciência**: A 'Alta Precisão' pode levar até 60 segundos.")
        st.write("📍 **Posição**: Mantenha o dispositivo relativamente parado durante a captura para melhor precisão.")
        st.write("🔒 **HTTPS**: A geolocalização do navegador geralmente requer conexão segura (HTTPS).")
    
    with st.form("formulario_historico"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("📅 Dados da Visita")
            data = st.date_input("Data da visita")
            hora_inicio = st.time_input("Hora de início")
            hora_fim = st.time_input("Hora de término")
            
            st.header("🏠 Dados da Propriedade")
            tipo_propriedade = st.selectbox("Tipo de propriedade", ["Sítio", "Fazenda", "Chácara", "Estância"])
            nome_propriedade = st.text_input("Nome da propriedade", placeholder="Ex: São José")
            endereco = st.text_area("Endereço completo", placeholder="Inclua referências se houver")
            municipio = st.text_input("Município")
            uf = st.selectbox("UF", ["RO", "AC", "AM", "RR", "PA", "TO", "MT", "MS", "GO", "DF"])
            
        with col2:
            st.header("📍 Coordenadas GPS")
            obter_localizacao()
            
            lat_long_porteira = st.text_input("Coordenadas da porteira (Lat, Long)", key="lat_long_porteira_input", placeholder="Ex: -9.897289, -63.017788")
            # Se quiser o botão de preenchimento:
            # criar_botao_preencher_coords("porteira") 
            
            lat_long_sede = st.text_input("Coordenadas da sede (Lat, Long)", key="lat_long_sede_input", placeholder="Ex: -9.897500, -63.017900")
            # Se quiser o botão de preenchimento:
            # criar_botao_preencher_coords("sede")
            
            st.header("📏 Área e Proprietário")
            area = st.number_input("Área da propriedade", min_value=0.01, step=0.1, format="%.2f")
            unidade_area = st.selectbox("Unidade", ["hectares", "alqueires"])
            nome_proprietario = st.text_input("Nome do proprietário")
            cpf_cnpj = st.text_input("CPF/CNPJ", placeholder="000.000.000-00 ou 00.000.000/0000-00")
            telefone = st.text_input("Telefone", placeholder="(69) 99999-9999")
        
        st.header("💼 Atividade Econômica")
        atividade_principal = st.text_input("Atividade principal", placeholder="Ex: Criação de bovinos")
        
        st.header("🚗 Veículos (Opcional)")
        veiculos = st.text_area("Descrição dos veículos", 
                               placeholder="Ex: uma caminhonete marca Ford, modelo Ranger, placa ABC-1234, cor Prata; um trator marca Massey Ferguson, modelo 265, sem placa, cor Vermelha")
        
        st.header("🐄 Rebanho")
        marca_gado = st.text_input("Marca/sinal/ferro registrado (Opcional)", 
                                  placeholder="Ex: JB na paleta esquerda")
        
        st.header("🏷️ Placa de Identificação")
        numero_placa = st.text_input("Número da placa", placeholder="Ex: PSR-001")
        
        submitted = st.form_submit_button("🚀 Gerar Histórico", use_container_width=True)
    
    if submitted:
        campos_obrigatorios = {
            "Data da visita": data,
            "Hora de início": hora_inicio,
            "Hora de término": hora_fim,
            "Nome da propriedade": nome_propriedade,
            "Endereço completo": endereco,
            "Município": municipio,
            "Coordenadas da porteira": lat_long_porteira,
            "Coordenadas da sede": lat_long_sede,
            "Área da propriedade": area, # A validação de > 0 é feita abaixo
            "Nome do proprietário": nome_proprietario,
            "CPF/CNPJ": cpf_cnpj,
            "Telefone": telefone,
            "Atividade principal": atividade_principal,
            "Número da placa": numero_placa
        }
        
        campos_vazios = [nome for nome, valor in campos_obrigatorios.items() if not valor and nome != "Área da propriedade"] # area é validada separadamente
        if not campos_obrigatorios["Área da propriedade"]: # Adiciona área se estiver vazia (None)
             campos_vazios.append("Área da propriedade")

        if campos_vazios:
            st.error(f"❌ Por favor, preencha todos os campos obrigatórios: {', '.join(campos_vazios)}!")
        elif area <= 0: # area é um float aqui
             st.error("❌ A área da propriedade deve ser maior que zero.")
        else:
            dados = {
                'data': data.strftime("%d/%m/%Y"),
                'hora_inicio': hora_inicio.strftime("%H:%M"),
                'hora_fim': hora_fim.strftime("%H:%M"),
                'tipo_propriedade': tipo_propriedade,
                'nome_propriedade': nome_propriedade,
                'endereco': endereco,
                'municipio': municipio,
                'uf': uf,
                'lat_long_porteira': lat_long_porteira,
                'lat_long_sede': lat_long_sede,
                'area': f"{area:.2f}", 
                'unidade_area': unidade_area,
                'nome_proprietario': nome_proprietario,
                'cpf_cnpj': cpf_cnpj,
                'telefone': telefone,
                'atividade_principal': atividade_principal,
                'veiculos': veiculos,
                'marca_gado': marca_gado,
                'numero_placa': numero_placa
            }
           
            with st.spinner("🔄 Gerando histórico..."):
                historico_bruto = gerar_historico(dados)
           
            with st.spinner("✨ Refinando texto com IA..."):
                historico_refinado = refinar_texto_com_openai(historico_bruto)
           
            st.success("✅ Histórico gerado com sucesso!")
           
            st.header("📄 Histórico Final")
            st.text_area("Texto gerado:", value=historico_refinado, height=400, key="historico_final_text_area_display", disabled=True) # Chave única
                       
            col_copy, col_download = st.columns(2)
           
            with col_copy:
                criar_botao_copiar(historico_refinado)
           
            with col_download:
                st.download_button(
                    label="💾 Baixar como TXT",
                    data=historico_refinado,
                    file_name=f"historico_policial_{data.strftime('%Y%m%d')}_{nome_propriedade.replace(' ','_') if nome_propriedade else 'desconhecido'}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

if __name__ == "__main__":
   main()
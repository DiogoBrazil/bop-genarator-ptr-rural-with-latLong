import streamlit as st
from openai import OpenAI
from datetime import datetime
# import re # Not needed if using strptime for validation
import streamlit.components.v1 as components

# Configurar cliente OpenAI usando secrets do Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def validar_formato_hora_strptime(hora_str: str) -> bool:
    """Valida se a string da hora está no formato HH:MM e se os valores são válidos."""
    if not isinstance(hora_str, str) or len(hora_str) != 5:
        return False
    try:
        datetime.strptime(hora_str, "%H:%M")
        return True
    except ValueError:
        return False

def masked_time_input(label: str, key: str) -> str:
    """
    Cria um campo de input de texto com máscara para HH:MM usando HTML/JS.
    O valor é retornado para o Python via Streamlit.setComponentValue.
    The 'key' parameter is used for st.session_state and to generate unique HTML IDs.
    """
    input_id = f"masked_time_input_{key}"
    initial_html_value = st.session_state.get(key, "")

    html_component = f"""
    <label for="{input_id}" style="display: block; margin-bottom: 5px; font-size: 14px; color: #31333F;">{label}</label>
    <input type="text" id="{input_id}" value="{initial_html_value}" maxlength="5" placeholder="HH:MM"
           style="width: 70px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
    <script>
    (function() {{ // IIFE para escopo
        const input = document.getElementById('{input_id}');
        
        function formatAndSetValue(element) {{
            let value = element.value;
            let originalCursorPos = element.selectionStart;

            let digits = value.replace(/[^0-9]/g, "");
            digits = digits.substring(0, 4);
            
            let formattedValue = "";

            if (digits.length > 0) {{
                let hh_str = digits.substring(0, 2);
                if (hh_str.length === 2) {{
                    let hh_num = parseInt(hh_str, 10);
                    if (hh_num > 23) {{
                        hh_str = "23"; 
                        digits = hh_str + digits.substring(2); 
                    }}
                }}
                formattedValue = hh_str;
            }}
            
            if (digits.length > 2) {{
                let mm_str = digits.substring(2, 4);
                 if (mm_str.length === 2) {{
                    let mm_num = parseInt(mm_str, 10);
                    if (mm_num > 59) {{
                        mm_str = "59";
                    }}
                }}
                formattedValue += ":" + mm_str;
            }}
            
            element.value = formattedValue;

            // Lógica de cursor (simplificada)
            if (originalCursorPos === 2 && value.length === 2 && formattedValue.length === 3 && formattedValue.charAt(2) === ':') {{
                 element.setSelectionRange(3, 3);
            }} else if (originalCursorPos === 3 && value.length === 3 && formattedValue.length === 2 && value.charAt(2) === ':'){{
                 element.setSelectionRange(2,2);
            }} else {{
                if (formattedValue.length === 5 || originalCursorPos > formattedValue.length) {{
                    element.setSelectionRange(formattedValue.length, formattedValue.length);
                }} else {{
                    element.setSelectionRange(originalCursorPos, originalCursorPos);
                }}
            }}

            if (window.Streamlit) {{
                window.Streamlit.setComponentValue(formattedValue);
            }}
        }}

        input.addEventListener('input', function(event) {{
            if (event.isComposing) {{
                return;
            }}
            formatAndSetValue(this);
        }});

        let initSent = false;
        const sendInitialValue = () => {{
            // Verifica se Streamlit e setComponentValue estão disponíveis
            if(window.Streamlit && typeof window.Streamlit.setComponentValue === 'function' && !initSent) {{
                formatAndSetValue(input); 
                initSent = true;
            }} else if (!initSent) {{ // Se não estiver pronto, tenta novamente
                setTimeout(sendInitialValue, 100); 
            }}
        }};
        
        // Tenta enviar o valor inicial. Adiciona listener se Streamlit não estiver pronto.
        if (window.Streamlit && typeof window.Streamlit.setComponentValue === 'function') {{
            sendInitialValue();
        }} else {{
            window.addEventListener('streamlit:component_ready', sendInitialValue, {{ once: true }});
            setTimeout(sendInitialValue, 200); // Fallback de tempo
        }}
    }})();
    </script>
    """
    # Removido o argumento 'key' da chamada components.html
    component_value = components.html(html_component, height=75) 
    
    if component_value is not None:
        st.session_state[key] = component_value
        return component_value
    return st.session_state.get(key, "")


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
                    if (watchId) navigator.geolocation.clearWatch(watchId);
                    watchId = null;
                } else if (attempts >= maxAttempts) {
                    processPosition(position, true);
                    if (watchId) navigator.geolocation.clearWatch(watchId);
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
                if (currentCoords) { 
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
                enableHighAccuracy: true, 
                timeout: 15000, 
                maximumAge: 60000 
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
                    <button id="gpsCopyCoordsButton" onclick="copyCoords()" style="
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
        const coordinates = document.getElementById("coordinates"); 
        
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
        if (coordinates) { 
            coordinates.style.display = "none";
        }
    }
    
    function copyCoords() {
        if (!currentCoords || !currentCoords.formatted) {
            const status = document.getElementById("status");
            if (status) {
                const originalStatusText = status.innerHTML;
                const originalStatusColor = status.style.color;
                status.innerHTML = "📋 Nenhuma coordenada para copiar. Obtenha a localização primeiro.";
                status.style.color = "#ff9800";
                setTimeout(() => {
                    if (status.innerHTML === "📋 Nenhuma coordenada para copiar. Obtenha a localização primeiro.") {
                        status.innerHTML = originalStatusText;
                        status.style.color = originalStatusColor;
                    }
                }, 3000);
            }
            return;
        }

        const textToCopy = currentCoords.formatted;
        const copyButton = document.getElementById("gpsCopyCoordsButton");
        
        let originalButtonText = "📋 Copiar Coordenadas";
        let originalButtonStyleBackground = "linear-gradient(135deg, #28a745 0%, #20c997 100%)"; 

        if (copyButton) {
            originalButtonText = copyButton.innerHTML;
            originalButtonStyleBackground = copyButton.style.background || originalButtonStyleBackground;
        }

        function showSuccessFeedback() {
            if (copyButton) {
                copyButton.innerHTML = "✅ Copiado!";
                copyButton.style.background = "linear-gradient(135deg, #17a2b8 0%, #138496 100%)"; 
                setTimeout(() => {
                    copyButton.innerHTML = originalButtonText;
                    copyButton.style.background = originalButtonStyleBackground;
                }, 2000);
            } else { 
                const statusDiv = document.getElementById("status");
                if (statusDiv) {
                    const prevStatus = statusDiv.innerHTML;
                    const prevColor = statusDiv.style.color;
                    statusDiv.innerHTML = "✅ Coordenadas copiadas!";
                    statusDiv.style.color = "#17a2b8"; 
                    setTimeout(() => {
                        statusDiv.innerHTML = prevStatus;
                        statusDiv.style.color = prevColor;
                    }, 2000);
                }
            }
        }

        function showFailureFeedback(usePrompt = true) {
            if (copyButton) {
                copyButton.innerHTML = "❌ Falha ao copiar";
                copyButton.style.background = "linear-gradient(135deg, #dc3545 0%, #c82333 100%)"; 
                setTimeout(() => {
                    copyButton.innerHTML = originalButtonText;
                    copyButton.style.background = originalButtonStyleBackground;
                }, 3000);
            }
            if (usePrompt) {
                prompt('Não foi possível copiar automaticamente. Copie manualmente:', textToCopy);
            }
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(textToCopy).then(
                () => { 
                    showSuccessFeedback();
                },
                (err) => { 
                    console.warn('navigator.clipboard.writeText falhou, tentando fallback execCommand: ', err);
                    fallbackCopy();
                }
            );
        } else {
            console.warn('navigator.clipboard não disponível, usando fallback execCommand.');
            fallbackCopy();
        }

        function fallbackCopy() {
            const textArea = document.createElement("textarea");
            textArea.value = textToCopy;
            textArea.style.position = "fixed"; 
            textArea.style.top = "-9999px";
            textArea.style.left = "-9999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    showSuccessFeedback();
                } else {
                    console.error('Fallback execCommand falhou em copiar.');
                    showFailureFeedback(true); 
                }
            } catch (err) {
                console.error('Erro crítico no fallback execCommand: ', err);
                showFailureFeedback(true); 
            }
            document.body.removeChild(textArea);
        }
    }
    
    function openMaps() {
        if (currentCoords && currentCoords.lat && currentCoords.lng) {
            const mapsUrl = `https://www.google.com/maps?q=${currentCoords.lat},${currentCoords.lng}`;
            window.open(mapsUrl, '_blank');
        } else {
             const status = document.getElementById("status");
            if(status) { 
                const originalStatusText = status.innerHTML;
                const originalStatusColor = status.style.color;
                status.innerHTML = "🗺️ Nenhuma coordenada para ver no mapa. Obtenha a localização primeiro.";
                status.style.color = "#ff9800"; 
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

        setTimeout(() => {
            if (statusDiv && statusDiv.innerHTML === "🗑️ Localização limpa.") {
                statusDiv.innerHTML = "";
            }
        }, 2000);
    }
    </script>
    """
    
    components.html(html_code, height=450) 

def criar_botao_preencher_coords(campo_nome):
    # Esta função não está sendo chamada no main, mas mantida caso seja útil no futuro.
    func_name = f"preencherCampo_{campo_nome.replace('-', '_').replace(' ', '_')}"
    button_html = f"""
    <button 
        onclick="{func_name}()" 
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
        if (typeof {func_name} !== 'function') {{ 
            function {func_name}() {{
                const coords = sessionStorage.getItem('gps_coords');
                const currentButton = document.currentScript.previousElementSibling; 

                if (coords) {{
                    let targetInput = null;
                    const inputs = Array.from(document.querySelectorAll('input[type="text"], textarea'));
                    for (let input of inputs) {{
                        if (input.placeholder && input.placeholder.toLowerCase().includes("{campo_nome.lower()}")) {{
                            targetInput = input;
                            break;
                        }}
                        if (!targetInput && input.placeholder && input.placeholder.toLowerCase().includes("ex: -9.897")) {{
                            targetInput = input;
                        }}
                    }}

                    if (targetInput) {{
                        targetInput.value = coords;
                        const inputEvent = new Event('input', {{ bubbles: true }});
                        targetInput.dispatchEvent(inputEvent);
                        const changeEvent = new Event('change', {{ bubbles: true }});
                        targetInput.dispatchEvent(changeEvent);
                        targetInput.focus();
                        
                        const feedbackSpan = document.createElement('span');
                        feedbackSpan.textContent = ' ✅ Preenchido!';
                        feedbackSpan.style.color = 'green';
                        feedbackSpan.style.fontSize = '10px';
                        feedbackSpan.style.marginLeft = '5px';
                        if(currentButton && currentButton.parentNode) {{
                           currentButton.parentNode.insertBefore(feedbackSpan, currentButton.nextSibling);
                        }}
                        setTimeout(() => feedbackSpan.remove(), 2500);

                    }} else {{
                        alert('⚠️ Campo de texto para "' + '{campo_nome}' + '" não encontrado. Cole manualmente: ' + coords);
                    }}
                }} else {{
                    alert('❌ Nenhuma localização capturada. Use o widget de localização primeiro.');
                }}
            }}
        }}
    </script>
    """
    
    components.html(button_html, height=55)


def criar_botao_copiar(texto):
    texto_escapado = texto.replace('`', '\\`').replace('"', '\\"').replace("'", "\\'")
    unique_id_suffix = ''.join(filter(str.isalnum, texto_escapado[:20])) 

    button_html = f"""
    <div style="margin: 10px 0;">
        <button 
            id="customCopyButton_{unique_id_suffix}"
            onclick="copyToClipboard_{unique_id_suffix}()" 
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
    if (typeof copyToClipboard_{unique_id_suffix} !== 'function') {{
        function copyToClipboard_{unique_id_suffix}() {{
            const textToCopy = `{texto_escapado}`;
            const button = document.getElementById("customCopyButton_{unique_id_suffix}");
            const originalButtonText = button.innerHTML;
            const originalButtonStyleBackground = button.style.background;

            function showSuccessOnButton() {{
                button.innerHTML = '✅ Texto Copiado!';
                button.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'; 
                setTimeout(function() {{
                    button.innerHTML = originalButtonText;
                    button.style.background = originalButtonStyleBackground;
                }}, 2000);
            }}

            function showFailureOnButton(usePrompt = true) {{
                button.innerHTML = '❌ Falha ao Copiar';
                button.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)'; 
                setTimeout(function() {{
                    button.innerHTML = originalButtonText;
                    button.style.background = originalButtonStyleBackground;
                }}, 3000);
                if (usePrompt) {{
                    prompt("Falha ao copiar. Por favor, copie manualmente:", textToCopy);
                }}
            }}

            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(textToCopy).then(
                    showSuccessOnButton,
                    function(err) {{ 
                        console.warn('navigator.clipboard.writeText falhou, tentando fallback: ', err);
                        fallbackCopyToClipboardInternal();
                    }}
                );
            }} else {{ 
                console.warn('navigator.clipboard não disponível, usando fallback.');
                fallbackCopyToClipboardInternal();
            }}

            function fallbackCopyToClipboardInternal() {{
                const textArea = document.createElement("textarea");
                textArea.value = textToCopy;
                textArea.style.position = "fixed";  
                textArea.style.top = "-9999px";    
                textArea.style.left = "-9999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {{
                    const successful = document.execCommand('copy');
                    if (successful) {{
                        showSuccessOnButton();
                    }} else {{
                        console.error('Fallback execCommand falhou em copiar.');
                        showFailureOnButton(true);
                    }}
                }} catch (err) {{
                    console.error('Erro crítico no fallback execCommand: ', err);
                    showFailureOnButton(true);
                }}
                document.body.removeChild(textArea);
            }}
        }}
    }}
    </script>
    """
    
    components.html(button_html, height=80)


def refinar_texto_com_openai(texto):
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
        st.write("3. Para as horas, use o formato HH:MM (ex: 08:30, 14:00).")
        st.write("4. Campos opcionais: veículos e marca de gado.")
        st.write("5. Clique em '🚀 Gerar Histórico'.")
        st.write("6. O texto será refinado automaticamente pela IA.")
        st.write("7. Use o botão '📋 Copiar Texto Completo' ou '💾 Baixar como TXT'.")
        
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
            data_visita = st.date_input("Data da visita", key="data_visita_input")
            
            # Usando os novos componentes de input de hora mascarados
            # As chaves "comp_hora_inicio" e "comp_hora_fim" são usadas internamente pelo componente
            # e para st.session_state.
            hora_inicio_str = masked_time_input("Hora de início", key="comp_hora_inicio")
            hora_fim_str = masked_time_input("Hora de término", key="comp_hora_fim")
            
            st.header("🏠 Dados da Propriedade")
            tipo_propriedade = st.selectbox("Tipo de propriedade", ["Sítio", "Fazenda", "Chácara", "Estância"], key="tipo_prop_sel")
            nome_propriedade = st.text_input("Nome da propriedade", placeholder="Ex: São José", key="nome_prop_text")
            endereco = st.text_area("Endereço completo", placeholder="Inclua referências se houver", key="endereco_text_area")
            municipio = st.text_input("Município", key="municipio_text")
            uf = st.selectbox("UF", ["RO", "AC", "AM", "RR", "PA", "TO", "MT", "MS", "GO", "DF"], key="uf_sel")
            
        with col2:
            st.header("📍 Coordenadas GPS")
            obter_localizacao()
            
            lat_long_porteira = st.text_input("Coordenadas da porteira (Lat, Long)", key="lat_long_porteira_input", placeholder="Ex: -9.897289, -63.017788")
            lat_long_sede = st.text_input("Coordenadas da sede (Lat, Long)", key="lat_long_sede_input", placeholder="Ex: -9.897500, -63.017900")
            
            st.header("📏 Área e Proprietário")
            area = st.number_input("Área da propriedade", min_value=0.01, step=0.1, format="%.2f", key="area_num_input")
            unidade_area = st.selectbox("Unidade", ["hectares", "alqueires"], key="unidade_area_sel")
            nome_proprietario = st.text_input("Nome do proprietário", key="nome_proprietario_text")
            cpf_cnpj = st.text_input("CPF/CNPJ", placeholder="000.000.000-00 ou 00.000.000/0000-00", key="cpf_cnpj_text")
            telefone = st.text_input("Telefone", placeholder="(69) 99999-9999", key="telefone_text")
        
        st.header("💼 Atividade Econômica")
        atividade_principal = st.text_input("Atividade principal", placeholder="Ex: Criação de bovinos", key="atividade_text")
        
        st.header("🚗 Veículos (Opcional)")
        veiculos = st.text_area("Descrição dos veículos", 
                               placeholder="Ex: uma caminhonete marca Ford, modelo Ranger, placa ABC-1234, cor Prata; um trator marca Massey Ferguson, modelo 265, sem placa, cor Vermelha", key="veiculos_text_area")
        
        st.header("🐄 Rebanho")
        marca_gado = st.text_input("Marca/sinal/ferro registrado (Opcional)", 
                                  placeholder="Ex: JB na paleta esquerda", key="marca_gado_text")
        
        st.header("🏷️ Placa de Identificação")
        numero_placa = st.text_input("Número da placa", placeholder="Ex: PSR-001", key="numero_placa_text")
        
        # Este é o botão de submit do formulário Streamlit
        submitted = st.form_submit_button("🚀 Gerar Histórico", use_container_width=True)
    
    if submitted:
        # Recupera os valores dos componentes mascarados usando as mesmas chaves
        # Eles já devem estar atualizados em st.session_state pela lógica do componente
        hora_inicio_val_final = st.session_state.get("comp_hora_inicio", "")
        hora_fim_val_final = st.session_state.get("comp_hora_fim", "")

        campos_obrigatorios_dict = {
            "Data da visita": data_visita,
            "Hora de início": hora_inicio_val_final, 
            "Hora de término": hora_fim_val_final,   
            "Nome da propriedade": nome_propriedade,
            "Endereço completo": endereco,
            "Município": municipio,
            "Coordenadas da porteira": lat_long_porteira,
            "Coordenadas da sede": lat_long_sede,
            "Área da propriedade": area, 
            "Nome do proprietário": nome_proprietario,
            "CPF/CNPJ": cpf_cnpj,
            "Telefone": telefone,
            "Atividade principal": atividade_principal,
            "Número da placa": numero_placa
        }
        
        campos_vazios_nomes = []
        for nome, valor in campos_obrigatorios_dict.items():
            if isinstance(valor, str) and not valor.strip(): # Para strings como hora_inicio_str, nome_propriedade, etc.
                campos_vazios_nomes.append(nome)
            elif valor is None and nome not in ["Veículos", "Marca/sinal/ferro registrado"]: # Campos que podem ser None
                 if nome == "Área da propriedade" and (area is None or area <=0) : # area é float, não pode ser None e deve ser >0
                     if nome not in campos_vazios_nomes: campos_vazios_nomes.append(nome + " (deve ser > 0)")
                 elif nome != "Área da propriedade": # Para outros campos None que são obrigatórios
                     campos_vazios_nomes.append(nome)
        
        # Verificação específica para área, caso não tenha sido pega acima
        if area is None or area <= 0:
            if "Área da propriedade" not in [c.split(" (")[0] for c in campos_vazios_nomes]:
                 campos_vazios_nomes.append("Área da propriedade (deve ser > 0)")


        erros_formato_hora = []
        if hora_inicio_val_final and not validar_formato_hora_strptime(hora_inicio_val_final):
            erros_formato_hora.append("Hora de início")
        if hora_fim_val_final and not validar_formato_hora_strptime(hora_fim_val_final):
            erros_formato_hora.append("Hora de término")

        if campos_vazios_nomes:
            unique_campos_vazios = sorted(list(set(campos_vazios_nomes)))
            st.error(f"❌ Por favor, preencha todos os campos obrigatórios: {', '.join(unique_campos_vazios)}!")
        elif erros_formato_hora:
            st.error(f"❌ Formato de hora inválido para: {', '.join(erros_formato_hora)}. Use o formato HH:MM e valores válidos (ex: 08:30).")
        else:
            dados = {
                'data': data_visita.strftime("%d/%m/%Y"),
                'hora_inicio': hora_inicio_val_final, 
                'hora_fim': hora_fim_val_final,     
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
            st.text_area("Texto gerado:", value=historico_refinado, height=400, key="historico_final_text_area_display_unique", disabled=True) 
                       
            col_copy, col_download = st.columns(2)
           
            with col_copy:
                criar_botao_copiar(historico_refinado)
           
            with col_download:
                st.download_button(
                    label="💾 Baixar como TXT",
                    data=historico_refinado,
                    file_name=f"historico_policial_{data_visita.strftime('%Y%m%d')}_{nome_propriedade.replace(' ','_') if nome_propriedade else 'desconhecido'}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

if __name__ == "__main__":
   main()
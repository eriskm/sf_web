/**
 * Robot AIS Floating Widget Module
 * Made for Sukabumi Flasher Local Store Integration
 * Owner: AIS Technologies
 */
(function() {
    // 1. Inject FontAwesome if not already loaded
    if (!document.querySelector('link[href*="font-awesome"]') && !document.querySelector('link[href*="all.min.css"]')) {
        const fa = document.createElement('link');
        fa.rel = 'stylesheet';
        fa.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(fa);
    }

    // 2. Inject Google Fonts (Outfit & Inter) if not loaded
    if (!document.querySelector('link[href*="fonts.googleapis.com"]')) {
        const fonts = document.createElement('link');
        fonts.rel = 'stylesheet';
        fonts.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap';
        document.head.appendChild(fonts);
    }

    // 3. Inject CSS Styles
    const css = `
        /* --- ROBOT AIS MODULAR WIDGET STYLES --- */
        .ai-widget-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 75px;
            height: 75px;
            background: #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.7);
            cursor: pointer;
            z-index: 2147483647 !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 3px solid #0ea5e9;
            user-select: none;
            overflow: hidden;
            animation: aiPulse 2s infinite;
        }
        .ai-widget-btn img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 50%;
        }

        @keyframes aiPulse {
            0% { box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.4); }
            70% { box-shadow: 0 0 0 15px rgba(14, 165, 233, 0); }
            100% { box-shadow: 0 0 0 0 rgba(14, 165, 233, 0); }
        }

        .ai-widget-btn:hover { 
            transform: scale(1.1) translateY(-5px); 
            animation: none;
            box-shadow: 0 15px 30px rgba(14, 165, 233, 0.3); 
        }

        #aiChatModal {
            display: none;
            position: fixed;
            bottom: 105px;
            right: 30px;
            width: 400px;
            height: 550px;
            max-height: calc(100vh - 140px);
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(25px) saturate(180%);
            -webkit-backdrop-filter: blur(25px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.65);
            border-radius: 24px;
            z-index: 9999;
            flex-direction: column;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255,255,255,0.8);
            overflow: hidden;
            animation: slideInAI 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            color: #0f172a;
            font-family: 'Outfit', 'Inter', sans-serif;
        }

        @keyframes slideInAI {
            from { opacity: 0; transform: translateY(30px) scale(0.9); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        .ai-header {
            padding: 18px 24px;
            background: rgba(255, 255, 255, 0.4);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
        }

        .ai-header-title {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .ai-header-title i {
            color: #0ea5e9;
            font-size: 1.15rem;
        }

        .ai-header-title span {
            font-weight: 800;
            font-size: 0.95rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .ai-close-btn {
            cursor: pointer;
            opacity: 0.5;
            font-size: 1.1rem;
            transition: opacity 0.2s;
        }
        .ai-close-btn:hover {
            opacity: 0.9;
        }

        .ai-body {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
            scrollbar-width: thin;
        }

        .ai-msg {
            padding: 12px 16px;
            border-radius: 16px;
            max-width: 85%;
            font-size: 0.9rem;
            line-height: 1.5;
            word-wrap: break-word;
            animation: messageFadeIn 0.3s ease-out;
        }

        @keyframes messageFadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .msg-bot { 
            background: rgba(255, 255, 255, 0.9); 
            align-self: flex-start; 
            border-bottom-left-radius: 4px; 
            border: 1px solid rgba(0, 0, 0, 0.05); 
            color: #0f172a; 
        }
        .msg-bot b, .msg-bot strong {
            color: #0ea5e9;
            font-weight: 700;
        }
        .msg-user { 
            background: linear-gradient(135deg, #00f2fe, #4facfe); 
            color: #020617; 
            align-self: flex-end; 
            border-bottom-right-radius: 4px; 
            font-weight: 600; 
            box-shadow: 0 4px 10px rgba(0, 242, 254, 0.15);
        }

        .ai-input-area {
            padding: 15px;
            background: rgba(255, 255, 255, 0.6);
            display: flex;
            gap: 10px;
            border-top: 1px solid rgba(0, 0, 0, 0.06);
        }

        .ai-input-area input {
            flex: 1;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(0, 0, 0, 0.1);
            padding: 10px 15px;
            border-radius: 12px;
            color: #0f172a;
            outline: none;
            font-size: 0.9rem;
            font-family: inherit;
            transition: border-color 0.2s;
        }
        .ai-input-area input:focus {
            border-color: #0ea5e9;
        }

        .ai-input-area button {
            background: linear-gradient(135deg, #0ea5e9, #3b82f6);
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            box-shadow: 0 4px 10px rgba(14, 165, 233, 0.2);
        }
        .ai-input-area button:hover { 
            transform: translateY(-1px);
            box-shadow: 0 6px 14px rgba(14, 165, 233, 0.35); 
        }

        /* Responsive */
        @media (max-width: 480px) {
            #aiChatModal {
                width: calc(100% - 40px);
                right: 20px;
                bottom: 90px;
                height: 480px;
            }
            .ai-widget-btn {
                bottom: 20px;
                right: 20px;
            }
        }
    `;

    const styleEl = document.createElement('style');
    styleEl.innerHTML = css;
    document.head.appendChild(styleEl);

    // 4. Create and Inject HTML markup dynamically
    function initializeWidget() {
        // Prevent duplicate creation
        if (document.getElementById('aiChatModal')) return;

        // Create Widget Trigger Button
        const widgetBtn = document.createElement('div');
        widgetBtn.className = 'ai-widget-btn';
        widgetBtn.title = 'Tanya neng Ais';
        widgetBtn.innerHTML = `
            <img src="/static/neng_ais.png" alt="neng Ais">
        `;
        widgetBtn.addEventListener('click', toggleAIChat);
        document.body.appendChild(widgetBtn);

        // Create Chat Modal Window
        const modal = document.createElement('div');
        modal.id = 'aiChatModal';
        modal.innerHTML = `
            <div class="ai-header">
                <div class="ai-header-title">
                    <i class="fas fa-robot"></i>
                    <span>neng Ais</span>
                </div>
                <span class="ai-close-btn" onclick="window.RobotAIS.toggle()">&times;</span>
            </div>
            <div id="aiChatBody" class="ai-body">
                <div class="ai-msg msg-bot">
                    Halo Bos! Ada <b>URUSAN</b> apa hari ini? Saya siap bantu analisa data <b>SF</b> dengan filosofi 5 Bit Logic. 🚀
                </div>
            </div>
            <div class="ai-input-area">
                <input type="text" id="aiChatInput" placeholder="Ketik pesan..." autocomplete="off">
                <button id="aiChatSendBtn"><i class="fas fa-paper-plane"></i></button>
            </div>
        `;
        document.body.appendChild(modal);

        // Attach event listeners inside the modal
        const input = document.getElementById('aiChatInput');
        const sendBtn = document.getElementById('aiChatSendBtn');

        input.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                sendAISMessage();
            }
        });

        sendBtn.addEventListener('click', sendAISMessage);
    }

    // Toggle function
    function toggleAIChat() {
        const modal = document.getElementById('aiChatModal');
        if (!modal) return;
        
        if (modal.style.display === 'none' || modal.style.display === '') {
            modal.style.display = 'flex';
            document.getElementById('aiChatInput').focus();
        } else {
            modal.style.display = 'none';
        }
    }

    // Send message function
    async function sendAISMessage() {
        const input = document.getElementById('aiChatInput');
        const body = document.getElementById('aiChatBody');
        const text = input.value.trim();
        if (!text) return;

        // 1. Append User Message
        const uMsg = document.createElement('div');
        uMsg.className = 'ai-msg msg-user';
        uMsg.innerText = text;
        body.appendChild(uMsg);
        input.value = '';
        body.scrollTop = body.scrollHeight;

        // 2. Append Thinking Indicator
        const loading = document.createElement('div');
        loading.className = 'ai-msg msg-bot';
        loading.innerHTML = '<i>Sedang berpikir... 🧠</i>';
        body.appendChild(loading);
        body.scrollTop = body.scrollHeight;

        try {
            const response = await fetch('/robot_ais/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            
            // Remove loader
            if (body.contains(loading)) {
                body.removeChild(loading);
            }

            const bMsg = document.createElement('div');
            bMsg.className = 'ai-msg msg-bot';
            if (data.status === 'success') {
                // Formatting (Markdown equivalent replacements for **bold** and \n)
                bMsg.innerHTML = data.text
                    .replace(/\n/g, '<br>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            } else {
                bMsg.innerText = "Error: " + (data.message || "Sinyal ke Brain terganggu.");
            }
            body.appendChild(bMsg);
        } catch (err) {
            if (body.contains(loading)) {
                body.removeChild(loading);
            }
            const eMsg = document.createElement('div');
            eMsg.className = 'ai-msg msg-bot';
            eMsg.innerText = "Koneksi ke server terputus, Bos.";
            body.appendChild(eMsg);
        }
        body.scrollTop = body.scrollHeight;
    }

    // Export API globally so they can be triggered programmatically if needed
    window.RobotAIS = {
        init: initializeWidget,
        toggle: toggleAIChat,
        send: sendAISMessage
    };

    // Auto init on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeWidget);
    } else {
        initializeWidget();
    }
})();

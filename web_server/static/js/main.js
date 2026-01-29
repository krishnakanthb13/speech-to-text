document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const micBtn = document.getElementById('mic-btn');
    const statusText = document.getElementById('status-text');
    const profileSelect = document.getElementById('profile-select');
    const promptDisplay = document.getElementById('prompt-display');
    const historyList = document.getElementById('history-list');

    // Modals
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeSettingsBtn = document.querySelector('.close-settings');
    const saveSettingsBtn = document.getElementById('save-settings');

    const historyBtn = document.getElementById('history-btn');
    const historyModal = document.getElementById('history-modal');
    const closeHistoryBtn = document.querySelector('.close-history');

    // State
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let config = null;

    // 1. Initial Load
    fetchConfig();
    fetchHistory();

    // 2. Config & Profiles
    async function fetchConfig() {
        try {
            const res = await fetch('/api/config');
            config = await res.json();
            populateProfiles();
            populateSettings();
        } catch (e) {
            console.error("Config load failed", e);
        }
    }

    function populateProfiles() {
        if (!config || !config.profiles) return;
        profileSelect.innerHTML = '';
        config.profiles.forEach((p, index) => {
            const opt = document.createElement('option');
            opt.value = p.name;
            opt.textContent = p.name; // Removed hotkey display
            profileSelect.appendChild(opt);
        });

        // Trigger generic selection
        if (config.profiles.length > 0) {
            updatePromptPreview(config.profiles[0].name);
        }
    }

    function updatePromptPreview(profileName) {
        const p = config.profiles.find(x => x.name === profileName);
        if (p) promptDisplay.textContent = p.prompt;
    }

    profileSelect.addEventListener('change', (e) => {
        updatePromptPreview(e.target.value);
    });

    // 3. Settings Handling
    function populateSettings() {
        if (!config) return;
        document.getElementById('stt-model-select').value = config.stt_model;
        document.getElementById('refinement-model-select').value = config.refinement_model;
        document.getElementById('refinement-toggle').checked = config.refinement_enabled;
    }

    saveSettingsBtn.addEventListener('click', async () => {
        const newConfig = { ...config };
        newConfig.stt_model = document.getElementById('stt-model-select').value;
        newConfig.refinement_model = document.getElementById('refinement-model-select').value;
        newConfig.refinement_enabled = document.getElementById('refinement-toggle').checked;

        await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newConfig)
        });

        config = newConfig;
        toggleModal(settingsModal, false);
    });

    // Modal Generic Logic
    function toggleModal(modal, show) {
        if (show) modal.classList.remove('hidden');
        else modal.classList.add('hidden');
    }

    settingsBtn.addEventListener('click', () => toggleModal(settingsModal, true));
    closeSettingsBtn.addEventListener('click', () => toggleModal(settingsModal, false));

    historyBtn.addEventListener('click', () => toggleModal(historyModal, true));
    closeHistoryBtn.addEventListener('click', () => toggleModal(historyModal, false));

    // Close on simple outside click
    window.addEventListener('click', (e) => {
        if (e.target === settingsModal) toggleModal(settingsModal, false);
        if (e.target === historyModal) toggleModal(historyModal, false);
    });

    // Shortcuts
    document.addEventListener('keydown', (e) => {
        // ESC to close any modal
        if (e.key === 'Escape') {
            toggleModal(settingsModal, false);
            toggleModal(historyModal, false);
        }

        // Ctrl+C to close (User Request), but ONLY if no text is selected
        if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'C')) {
            const selection = window.getSelection();
            // If text is highlighted, let default copy happen.
            // If nothing is highlighted, treat as "Cancel/Close"
            if (!selection || selection.toString().length === 0) {
                // Check which modal is open and close it
                if (!settingsModal.classList.contains('hidden')) {
                    e.preventDefault(); // Prevent copy sound/action if empty
                    toggleModal(settingsModal, false);
                }
                if (!historyModal.classList.contains('hidden')) {
                    e.preventDefault();
                    toggleModal(historyModal, false);
                }
            }
        }
    });

    // 4. Recording Logic
    micBtn.addEventListener('click', async () => {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener('stop', async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                processAudio(audioBlob);

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            });

            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add('recording');
            micBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
            statusText.textContent = "Listening...";
        } catch (err) {
            console.error("Mic access error:", err);
            alert("Microphone access denied or not available. Please ensure use HTTPS or localhost.");
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            micBtn.classList.remove('recording');
            micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            statusText.textContent = "Processing...";
        }
    }

    async function processAudio(blob) {
        const formData = new FormData();
        formData.append('audio', blob, 'recording.webm');
        formData.append('profile', profileSelect.value);
        formData.append('chatParams', JSON.stringify(chatParams));

        console.log("Sending Audio with Params:", chatParams); // Debug Log

        try {
            const res = await fetch('/api/record', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.status === 'success') {
                document.getElementById('last-text-display').textContent = data.refined;

                // Copy to Clipboard (Silent)
                try {
                    await navigator.clipboard.writeText(data.refined);
                } catch (err) {
                    console.error("Clipboard copy failed:", err);
                }

                // Update Status Text with Instruction
                statusText.innerHTML = 'Done! <span style="font-size:0.85em; opacity:0.8; margin-left: 5px;">(Ctrl+V to paste)</span>';

                // Longer timeout to read message
                setTimeout(() => statusText.textContent = "Ready to Record", 4000);

                fetchHistory(); // Refresh history
            } else {
                statusText.textContent = "Error";
                alert("Error: " + (data.error || "Unknown"));
            }
        } catch (err) {
            console.error(err);
            statusText.textContent = "Error";
            alert("Network Error: " + err.message);
        }
    }

    // 5. Chat Parameters Logic
    const chatParamsModal = document.getElementById('chat-params-modal');
    const chatParamsBtn = document.getElementById('chat-params-btn');
    const closeChatParamsBtn = document.querySelector('.close-chat-params');
    const saveChatParamsBtn = document.getElementById('save-chat-params');
    const resetChatParamsBtn = document.getElementById('reset-chat-params');

    // Load from localStorage or use defaults
    const defaultChatParams = {
        humanRobot: 50,
        factCreative: 50,
        funnyRage: 50,
        expertLame: 50,
        formalSlang: 50
    };

    let chatParams = { ...defaultChatParams };
    
    try {
        const stored = localStorage.getItem('chatParams');
        if (stored) {
            const parsed = JSON.parse(stored);
            // Validate stored values
            const validKeys = Object.keys(defaultChatParams);
            let isValid = true;
            for (const key of validKeys) {
                if (typeof parsed[key] !== 'number' || parsed[key] < 0 || parsed[key] > 100) {
                    isValid = false;
                    break;
                }
            }
            if (isValid) {
                chatParams = parsed;
            }
        }
    } catch (e) {
        console.error("Failed to load chatParams from localStorage:", e);
    }

    // Function to save chatParams to localStorage
    function saveChatParams() {
        try {
            localStorage.setItem('chatParams', JSON.stringify(chatParams));
        } catch (e) {
            console.error("Failed to save chatParams to localStorage:", e);
        }
    }

    // Function to update personality button indicator
    function updatePersonalityIndicator() {
        if (!chatParamsBtn) return;
        const isCustom = Object.values(chatParams).some(v => v < 40 || v > 60);
        chatParamsBtn.classList.toggle('active-personality', isCustom);
    }

    // Sliders
    const sliders = {
        humanRobot: { el: document.getElementById('slider-human-robot'), val: document.getElementById('val-human-robot') },
        factCreative: { el: document.getElementById('slider-fact-creative'), val: document.getElementById('val-fact-creative') },
        funnyRage: { el: document.getElementById('slider-funny-rage'), val: document.getElementById('val-funny-rage') },
        expertLame: { el: document.getElementById('slider-expert-lame'), val: document.getElementById('val-expert-lame') },
        formalSlang: { el: document.getElementById('slider-formal-slang'), val: document.getElementById('val-formal-slang') }
    };

    // Initialize Sliders with stored values
    Object.keys(sliders).forEach(key => {
        const s = sliders[key];
        if (s && s.el) {
            // Set initial value from localStorage
            s.el.value = chatParams[key];
            s.val.textContent = chatParams[key] + '%';
            
            s.el.addEventListener('input', (e) => {
                chatParams[key] = parseInt(e.target.value);
                s.val.textContent = e.target.value + '%';
                saveChatParams();
                updatePersonalityIndicator();
            });
        }
    });

    // Initial indicator update
    updatePersonalityIndicator();

    // Reset Logic
    if (resetChatParamsBtn) {
        resetChatParamsBtn.addEventListener('click', () => {
            chatParams = { ...defaultChatParams };
            Object.keys(sliders).forEach(key => {
                const s = sliders[key];
                if (s && s.el) {
                    s.el.value = defaultChatParams[key];
                    s.val.textContent = defaultChatParams[key] + '%';
                }
            });
            document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
            saveChatParams();
            updatePersonalityIndicator();
        });
    }

    // Presets
    const presets = {
        friend: { humanRobot: 10, factCreative: 80, funnyRage: 20, expertLame: 80, formalSlang: 90 }, // Very human, creative, funny, not expert, slangy
        professional: { humanRobot: 40, factCreative: 20, funnyRage: 50, expertLame: 10, formalSlang: 10 }, // Balanced, factual, NEUTRAL tone, expert, formal
        lover: { humanRobot: 0, factCreative: 90, funnyRage: 10, expertLame: 90, formalSlang: 50 }, // Total human, creative, sweet, balanced language
        roast: { humanRobot: 30, factCreative: 100, funnyRage: 100, expertLame: 0, formalSlang: 100 } // Sassy
    };

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const presetName = btn.dataset.preset;
            const vals = presets[presetName];
            if (vals) {
                // Update State
                chatParams = { ...vals };
                // Update UI
                Object.keys(sliders).forEach(key => {
                    const s = sliders[key];
                    if (s && s.el) {
                        s.el.value = vals[key];
                        s.val.textContent = vals[key] + '%';
                    }
                });

                // Visual feedback
                document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Save and update indicator
                saveChatParams();
                updatePersonalityIndicator();
            }
        });
    });

    // Modal Handling
    if (chatParamsBtn) {
        chatParamsBtn.addEventListener('click', () => toggleModal(chatParamsModal, true));
    }
    if (closeChatParamsBtn) {
        closeChatParamsBtn.addEventListener('click', () => toggleModal(chatParamsModal, false));
    }

    window.addEventListener('click', (e) => {
        if (e.target === chatParamsModal) toggleModal(chatParamsModal, false);
    });

    if (saveChatParamsBtn) {
        saveChatParamsBtn.addEventListener('click', () => {
            // Just close, variables are already updated on input
            toggleModal(chatParamsModal, false);
        });
    }

    // UI Toggles (Prompt & Last Transcription)
    // promptDisplay already declared at top
    // Toggle button removed per user request

    const toggleLastTransBtn = document.getElementById('toggle-last-transcription');
    const lastTransContent = document.getElementById('last-transcription-content');

    if (toggleLastTransBtn && lastTransContent) {
        toggleLastTransBtn.addEventListener('click', () => {
            lastTransContent.classList.toggle('hidden');
            toggleLastTransBtn.classList.toggle('active');
        });
    }

    // History Logic (Existing)
    async function fetchHistory() {
        try {
            const res = await fetch('/api/history');
            const history = await res.json();
            historyList.innerHTML = '';

            if (history.length === 0) {
                historyList.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--text-muted); opacity: 0.7;">
                        <i class="fa-solid fa-ghost" style="font-size: 2.5rem; margin-bottom: 1rem;"></i>
                        <p style="font-style: italic;">It's ghost-town quiet in here... 👻<br>Start yapping to scare them away!</p>
                    </div>
                `;
            } else {
                history.forEach(item => addHistoryItem(item, false));
            }

            // Restore last transcription from history on load
            if (history.length > 0) {
                const latest = history[0]; // API returns newest first
                const text = latest.refined_text || latest.raw_text;
                const display = document.getElementById('last-text-display');
                if (display) display.textContent = text;
            }
        } catch (err) {
            console.error("Failed to fetch history:", err);
            historyList.innerHTML = '<div style="padding:1rem; text-align:center;">Could not load history 😓</div>';
        }
    }

    function addHistoryItem(item, prepend) {
        const div = document.createElement('div');
        div.className = 'history-item';

        // Escape HTML to prevent XSS
        const escapeHtml = (text) => {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return (text || '').replace(/[&<>"']/g, function (m) { return map[m]; });
        };

        // Check for Custom Personality
        let personalityBadge = '';
        if (item.chat_params) {
            try {
                const params = JSON.parse(item.chat_params);
                const isCustom = Object.values(params).some(val => val < 40 || val > 60);
                if (isCustom) {
                    personalityBadge = `<span class="history-profile-badge" style="background: rgba(255, 69, 0, 0.2); color: #ff9f43; margin-left: 5px;"><i class="fa-solid fa-masks-theater"></i> Custom</span>`;
                }
            } catch (e) {
                // Ignore parse error
            }
        }

        div.innerHTML = `
            <div class="history-header">
                <div>
                    <span>${escapeHtml(item.timestamp)}</span>
                    <span class="history-profile-badge">${escapeHtml(item.profile)}</span>
                    ${personalityBadge}
                </div>
            </div>
            <div class="history-content">
                ${escapeHtml(item.refined_text)}
                <div class="history-raw">Raw: ${escapeHtml(item.raw_text)}</div>
            </div>
            <button class="copy-btn" title="Copy Text"><i class="fa-regular fa-copy"></i></button>
            <button class="delete-btn" title="Delete"><i class="fa-solid fa-trash"></i></button>
        `;

        // Delete Logic
        const deleteBtn = div.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to delete this specific recording?')) return;

            try {
                const res = await fetch('/api/history/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ timestamp: item.timestamp })
                });
                const data = await res.json();

                if (data.status === 'success') {
                    // Smooth removal
                    div.style.transition = 'all 0.3s';
                    div.style.opacity = '0';
                    div.style.transform = 'translateX(20px)';
                    setTimeout(() => div.remove(), 300);
                } else {
                    alert('Error deleting item: ' + (data.error || 'Unknown error'));
                }
            } catch (e) {
                console.error(e);
                alert('Connection error while deleting.');
            }
        });

        // Copy Logic
        const copyBtn = div.querySelector('.copy-btn');
        copyBtn.addEventListener('click', () => {
            const textToCopy = item.refined_text || item.raw_text;
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalIcon = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
                copyBtn.style.color = '#00ff00';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>';
                    copyBtn.style.color = '';
                }, 1500);
            });
        });

        if (prepend) historyList.prepend(div);
        else historyList.appendChild(div);
    }
});

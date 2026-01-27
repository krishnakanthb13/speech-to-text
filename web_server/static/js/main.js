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

        try {
            const res = await fetch('/api/record', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.status === 'success') {
                statusText.textContent = "Done!";
                setTimeout(() => statusText.textContent = "Ready to Record", 2000);
                addHistoryItem(data.entry, true); // Add to top

                // Auto-open history on success if desired, or just let user browse
                // toggleModal(historyModal, true); 
            } else {
                statusText.textContent = "Error";
                alert("Error: " + data.error);
            }
        } catch (e) {
            statusText.textContent = "Error";
            console.error(e);
        }
    }

    // 5. History
    async function fetchHistory() {
        const res = await fetch('/api/history');
        const history = await res.json();
        historyList.innerHTML = '';
        history.forEach(item => addHistoryItem(item, false));
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

        div.innerHTML = `
            <div class="history-header">
                <span>${escapeHtml(item.timestamp)}</span>
                <span class="history-profile-badge">${escapeHtml(item.profile)}</span>
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

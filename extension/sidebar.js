// DOM Elements
let currentDocumentText = '';
let chatHistory = [];
let currentMode = 'quick';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('LegalGuardianGPT sidebar loaded');
    
    // Initialize connections
    checkConnections();
    setupEventListeners();
    loadPageContent();
});

// Connection Management
async function checkConnections() {
    const statusEl = document.getElementById('connectionStatus');
    const apiStatusEl = document.getElementById('apiStatus');
    
    try {
        // Check CUAD backend
        const response = await chrome.runtime.sendMessage({ 
            action: 'CHECK_CUAD_HEALTH' 
        });
        
        if (response.status === 'healthy') {
            statusEl.innerHTML = '<span class="status-dot connected"></span><span class="status-text">CUAD RAG Connected</span>';
            apiStatusEl.textContent = `CUAD: ${response.data.collection_info.document_count} clauses`;
        } else {
            statusEl.innerHTML = '<span class="status-dot disconnected"></span><span class="status-text">CUAD Disconnected</span>';
            apiStatusEl.textContent = 'CUAD: Offline';
        }
    } catch (error) {
        console.error('Connection check failed:', error);
        statusEl.innerHTML = '<span class="status-dot error"></span><span class="status-text">Connection Error</span>';
        apiStatusEl.textContent = 'CUAD: Error';
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Mode switching
    document.getElementById('quickModeBtn').addEventListener('click', () => switchMode('quick'));
    document.getElementById('chatModeBtn').addEventListener('click', () => switchMode('chat'));
    
    // Quick analysis buttons
    document.getElementById('summarizeBtn').addEventListener('click', () => analyzeDocument('summarize'));
    document.getElementById('explainBtn').addEventListener('click', () => analyzeDocument('explain'));
    document.getElementById('simplifyBtn').addEventListener('click', () => analyzeDocument('simplify'));
    
    // Chat functionality
    document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
    
    // Settings
    document.getElementById('settingsBtn').addEventListener('click', toggleSettings);
    document.getElementById('closeSettings').addEventListener('click', toggleSettings);
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    document.getElementById('similarity').addEventListener('input', (e) => {
        document.getElementById('similarityValue').textContent = e.target.value;
    });
}

// Mode Switching
function switchMode(mode) {
    currentMode = mode;
    
    // Update active buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    
    // Show/hide mode content
    document.querySelectorAll('.mode-content').forEach(content => {
        content.classList.toggle('active', content.id === `${mode}Mode`);
    });
    
    // If switching to chat mode, scroll to bottom
    if (mode === 'chat') {
        setTimeout(() => {
            scrollChatToBottom();
        }, 100);
    }
}

// Load page content
function loadPageContent() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const tab = tabs[0];
        document.getElementById('pageTitle').textContent = 
            tab.title || 'Current Page';
        
        // Get document text from content script
        chrome.tabs.sendMessage(tab.id, { action: 'GET_DOCUMENT_TEXT' }, (response) => {
            if (response && response.text) {
                currentDocumentText = response.text;
                updateTextStats(response.text);
            } else {
                currentDocumentText = 'Unable to extract text from this page.';
                updateTextStats('');
            }
        });
    });
}

function updateTextStats(text) {
    const charCount = text.length;
    const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
    
    document.getElementById('charCount').textContent = `${charCount} chars`;
    document.getElementById('wordCount').textContent = `${wordCount} words`;
}

// Quick Analysis Functions
async function analyzeDocument(mode) {
    const loadingEl = document.getElementById('loading');
    const resultsEl = document.getElementById('resultsContent');
    
    // Show loading
    loadingEl.style.display = 'flex';
    resultsEl.innerHTML = '';
    
    const prompts = {
        summarize: 'Please provide a concise summary of this legal document.',
        explain: 'Explain the key legal provisions and implications of this document.',
        simplify: 'Translate this legal document into plain, understandable English.'
    };
    
    try {
        const response = await chrome.runtime.sendMessage({
            action: 'GET_ENHANCED_RESPONSE',
            prompt: prompts[mode],
            documentText: currentDocumentText,
            question: prompts[mode]
        });
        
        displayAnalysisResults(response, mode);
    } catch (error) {
        console.error('Analysis error:', error);
        resultsEl.innerHTML = `
            <div class="error-message">
                <p>❌ Error analyzing document:</p>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        loadingEl.style.display = 'none';
    }
}

function displayAnalysisResults(response, mode) {
    const resultsEl = document.getElementById('resultsContent');
    
    if (response.fallback) {
        resultsEl.innerHTML = `
            <div class="warning-message">
                <p>⚠️ Using limited analysis (OpenAI not configured)</p>
                <p>${response.content}</p>
            </div>
        `;
    } else {
        resultsEl.innerHTML = `
            <div class="analysis-result">
                <div class="result-header">
                    <h4>${getModeTitle(mode)} Analysis</h4>
                    <span class="result-timestamp">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="result-content">
                    ${formatResponse(response.content)}
                </div>
                ${response.usage ? `
                <div class="result-footer">
                    <small>Tokens: ${response.usage.total_tokens} (${response.usage.prompt_tokens} prompt + ${response.usage.completion_tokens} completion)</small>
                </div>
                ` : ''}
            </div>
        `;
    }
}

function getModeTitle(mode) {
    const titles = {
        summarize: 'Summary',
        explain: 'Explanation',
        simplify: 'Simplification'
    };
    return titles[mode] || 'Analysis';
}

// Chat Functions
async function sendChatMessage() {
    const inputEl = document.getElementById('chatInput');
    const message = inputEl.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage('user', message);
    inputEl.value = '';
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    try {
        const useCUAD = document.getElementById('useCUAD').checked;
        const includeContext = document.getElementById('autoContext').checked;
        
        let response;
        
        if (useCUAD && includeContext) {
            // Enhanced analysis with CUAD and context
            response = await chrome.runtime.sendMessage({
                action: 'GET_ENHANCED_RESPONSE',
                prompt: message,
                documentText: currentDocumentText,
                question: message
            });
        } else if (useCUAD) {
            // CUAD only (no document context)
            const cuadResponse = await chrome.runtime.sendMessage({
                action: 'ANALYZE_WITH_CUAD',
                documentText: message,
                question: message
            });
            
            if (cuadResponse && cuadResponse.analysis_prompt) {
                response = await chrome.runtime.sendMessage({
                    action: 'GET_GPT_RESPONSE',
                    prompt: cuadResponse.analysis_prompt
                });
            }
        } else {
            // Regular GPT response
            response = await chrome.runtime.sendMessage({
                action: 'GET_GPT_RESPONSE',
                prompt: message
            });
        }
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Add assistant response
        addChatMessage('assistant', response.content || 'No response received.');
        
        // Update CUAD context if available
        if (useCUAD) {
            updateCUADContext(message);
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingId);
        addChatMessage('assistant', `Error: ${error.message}`);
    }
    
    scrollChatToBottom();
}

function addChatMessage(role, content) {
    const chatHistoryEl = document.getElementById('chatHistory');
    const messageId = `msg_${Date.now()}`;
    
    const messageEl = document.createElement('div');
    messageEl.className = `chat-message ${role}-message`;
    messageEl.id = messageId;
    
    const avatar = role === 'user' ? '👤' : '⚖️';
    const name = role === 'user' ? 'You' : 'Legal Assistant';
    
    messageEl.innerHTML = `
        <div class="message-header">
            <span class="message-avatar">${avatar}</span>
            <span class="message-sender">${name}</span>
            <span class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
        <div class="message-content">
            ${formatResponse(content)}
        </div>
    `;
    
    // Remove welcome message if it exists
    const welcomeMsg = chatHistoryEl.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    chatHistoryEl.appendChild(messageEl);
    chatHistory.push({ role, content, timestamp: new Date().toISOString() });
    
    return messageId;
}

function showTypingIndicator() {
    const chatHistoryEl = document.getElementById('chatHistory');
    const typingId = `typing_${Date.now()}`;
    
    const typingEl = document.createElement('div');
    typingEl.className = 'chat-message assistant-message typing';
    typingEl.id = typingId;
    
    typingEl.innerHTML = `
        <div class="message-header">
            <span class="message-avatar">⚖️</span>
            <span class="message-sender">Legal Assistant</span>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    chatHistoryEl.appendChild(typingEl);
    scrollChatToBottom();
    
    return typingId;
}

function removeTypingIndicator(id) {
    const typingEl = document.getElementById(id);
    if (typingEl) {
        typingEl.remove();
    }
}

async function updateCUADContext(query) {
    try {
        const response = await chrome.runtime.sendMessage({
            action: 'SEARCH_CUAD',
            query: query,
            nResults: 3
        });
        
        const contextEl = document.getElementById('contextContent');
        
        if (response && response.length > 0) {
            contextEl.innerHTML = response.map((clause, index) => `
                <div class="cuad-reference">
                    <div class="reference-header">
                        <span class="reference-type">${clause.clause_type}</span>
                        <span class="reference-score">Similarity: ${clause.similarity_score.toFixed(3)}</span>
                    </div>
                    <div class="reference-text">
                        ${clause.text}
                    </div>
                </div>
            `).join('');
            
            // Update context title
            document.querySelector('#cuadContext h4').textContent = `🔍 CUAD References (${response.length} found)`;
        }
    } catch (error) {
        console.error('Failed to update CUAD context:', error);
    }
}

// Utility Functions
function formatResponse(text) {
    // Basic formatting for line breaks
    return text.replace(/\n/g, '<br>');
}

function scrollChatToBottom() {
    const chatHistoryEl = document.getElementById('chatHistory');
    chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
}

// Settings Functions
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.classList.toggle('visible');
}

function saveSettings() {
    const apiUrl = document.getElementById('apiUrl').value;
    const openaiKey = document.getElementById('openaiKey').value;
    
    // Save to storage
    chrome.storage.local.set({
        apiUrl: apiUrl,
        openaiKey: openaiKey
    }, () => {
        alert('Settings saved!');
        toggleSettings();
        checkConnections(); // Recheck connections with new settings
    });
}

// Load saved settings
function loadSettings() {
    chrome.storage.local.get(['apiUrl', 'openaiKey'], (items) => {
        if (items.apiUrl) {
            document.getElementById('apiUrl').value = items.apiUrl;
        }
        if (items.openaiKey) {
            document.getElementById('openaiKey').value = items.openaiKey;
        }
    });
}

// Initialize settings
loadSettings();
// Simplified content script - minimal overhead
console.log('LegalGuardianGPT content script loading...');

// Extract text efficiently
function extractTextSimple() {
    // Try to get main content
    const mainSelectors = [
        'main',
        'article',
        '[role="main"]',
        '.content',
        '.document',
        'body'
    ];
    
    for (const selector of mainSelectors) {
        const element = document.querySelector(selector);
        if (element && element.textContent && element.textContent.trim().length > 100) {
            return element.textContent.substring(0, 5000); // Limit size
        }
    }
    
    // Fallback to body
    return document.body.textContent.substring(0, 5000);
}

// Create simple sidebar
function createSimpleSidebar() {
    if (document.getElementById('lg-sidebar')) return;
    
    const iframe = document.createElement('iframe');
    iframe.id = 'lg-sidebar';
    iframe.src = chrome.runtime.getURL('sidebar.html');
    
    iframe.style.cssText = `
        position: fixed;
        top: 0;
        right: 0;
        width: 400px;
        height: 100vh;
        border: none;
        z-index: 999999;
        background: white;
        box-shadow: -2px 0 10px rgba(0,0,0,0.1);
    `;
    
    document.body.appendChild(iframe);
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '×';
    closeBtn.style.cssText = `
        position: fixed;
        top: 10px;
        right: 410px;
        width: 30px;
        height: 30px;
        background: #4a5568;
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        z-index: 1000000;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    closeBtn.onclick = () => {
        iframe.remove();
        closeBtn.remove();
    };
    
    document.body.appendChild(closeBtn);
}

// Message handler
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    switch (request.action) {
        case 'GET_DOCUMENT_TEXT':
            sendResponse({ 
                text: extractTextSimple(),
                url: window.location.href,
                title: document.title 
            });
            break;
            
        case 'TOGGLE_SIDEBAR':
            if (document.getElementById('lg-sidebar')) {
                document.getElementById('lg-sidebar').remove();
                document.querySelector('[style*="right: 410px"]')?.remove();
            } else {
                createSimpleSidebar();
            }
            sendResponse({ success: true });
            break;
            
        case 'PING':
            sendResponse({ status: 'active', url: window.location.href });
            break;
    }
});

// Auto-inject on legal pages
function shouldAutoInject() {
    const url = window.location.href.toLowerCase();
    const legalKeywords = ['terms', 'privacy', 'contract', 'agreement', 'legal', 'policy'];
    return legalKeywords.some(keyword => url.includes(keyword));
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

function init() {
    console.log('✅ LegalGuardianGPT content script loaded');
    
    if (shouldAutoInject()) {
        setTimeout(() => {
            createSimpleSidebar();
        }, 1500);
    }
}
// extension/popup.js
document.addEventListener('DOMContentLoaded', function() {
    const backendUrl = 'http://localhost:8000';
    
    // Elements
    const backendStatus = document.getElementById('backendStatus');
    const agentCount = document.getElementById('agentCount');
    const pageStatus = document.getElementById('pageStatus');
    const agentsLive = document.getElementById('agentsLive');
    const toolsLive = document.getElementById('toolsLive');
    const lastScan = document.getElementById('lastScan');
    const analyzePageBtn = document.getElementById('analyzePage');
    const openDashboardBtn = document.getElementById('openDashboard');
    
    // Check backend status
    async function checkBackendStatus() {
        try {
            const response = await fetch(`${backendUrl}/`);
            const data = await response.json();
            
            backendStatus.textContent = 'Connected';
            backendStatus.className = 'status-value connected';
            
            // Update agent and tool counts
            if (data.agents !== undefined) {
                agentCount.textContent = `${data.agents}/6`;
                agentsLive.textContent = `${data.agents} agents`;
            }
            
            if (data.tools !== undefined) {
                toolsLive.textContent = `${data.tools} tools`;
            }
            
            // Get detailed agent info
            try {
                const agentsResponse = await fetch(`${backendUrl}/agents`);
                const agentsData = await agentsResponse.json();
                agentCount.textContent = `${agentsData.total}/6`;
            } catch (e) {
                console.log('Could not fetch agent details');
            }
            
        } catch (error) {
            backendStatus.textContent = 'Disconnected';
            backendStatus.className = 'status-value disconnected';
            agentCount.textContent = '0/6';
            console.error('Backend connection failed:', error);
        }
    }
    
    // Analyze current page
    analyzePageBtn.addEventListener('click', async () => {
        pageStatus.textContent = 'Analyzing...';
        analyzePageBtn.disabled = true;
        
        try {
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Send message to content script
            chrome.tabs.sendMessage(tab.id, { action: 'analyzePage' }, (response) => {
                if (response && response.status === 'analyzing') {
                    pageStatus.textContent = 'Analysis started';
                    lastScan.textContent = 'Just now';
                    
                    // Close popup after 1 second
                    setTimeout(() => window.close(), 1000);
                } else {
                    pageStatus.textContent = 'Failed';
                }
                
                analyzePageBtn.disabled = false;
            });
            
        } catch (error) {
            pageStatus.textContent = 'Error';
            analyzePageBtn.disabled = false;
            console.error('Failed to analyze page:', error);
        }
    });
    
    // Open dashboard
    openDashboardBtn.addEventListener('click', () => {
        chrome.tabs.create({ url: backendUrl });
        window.close();
    });
    
    // Initialize
    checkBackendStatus();
    
    // Update last scan time
    chrome.storage.local.get(['lastScan'], (result) => {
        if (result.lastScan) {
            lastScan.textContent = result.lastScan;
        }
    });
});
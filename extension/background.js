// Simplified background script for LegalGuardianGPT
console.log('LegalGuardianGPT background script loading...');

// Configuration
const CONFIG = {
    CUAD_API_URL: 'http://localhost:8000',
    MAX_RETRIES: 3,
    TIMEOUT: 10000 // 10 seconds
};

// Cache for responses
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute

// Helper: Make fetch with timeout
async function fetchWithTimeout(url, options = {}, timeout = CONFIG.TIMEOUT) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
}

// Check CUAD health
async function checkCUADHealth() {
    const cacheKey = 'health_check';
    const cached = cache.get(cacheKey);
    
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
        return cached.data;
    }
    
    try {
        const response = await fetchWithTimeout(`${CONFIG.CUAD_API_URL}/health`);
        const data = await response.json();
        
        cache.set(cacheKey, {
            data: { status: 'healthy', data },
            timestamp: Date.now()
        });
        
        return { status: 'healthy', data };
    } catch (error) {
        console.warn('CUAD health check failed:', error.message);
        return { 
            status: 'error', 
            error: error.message,
            fallback: true
        };
    }
}

// Simple search
async function searchCUADSimple(query, nResults = 3) {
    const cacheKey = `search_${query}_${nResults}`;
    const cached = cache.get(cacheKey);
    
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
        return cached.data;
    }
    
    try {
        const response = await fetchWithTimeout(`${CONFIG.CUAD_API_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                n_results: nResults,
                min_similarity: 0.2
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });
        
        return data;
    } catch (error) {
        console.warn('CUAD search failed:', error.message);
        // Return sample data as fallback
        return getFallbackClauses(query, nResults);
    }
}

// Fallback clauses when CUAD is unavailable
function getFallbackClauses(query, nResults) {
    const sampleClauses = [
        {
            text: "Confidential Information means all information disclosed by one party to another that is marked confidential or should reasonably be considered confidential.",
            clause_type: "Confidentiality",
            similarity_score: 0.85,
            metadata: { source: "fallback", document_title: "Sample NDA" }
        },
        {
            text: "This Agreement may be terminated by either party upon thirty (30) days written notice to the other party.",
            clause_type: "Termination",
            similarity_score: 0.72,
            metadata: { source: "fallback", document_title: "Sample Agreement" }
        },
        {
            text: "Neither party shall be liable for any indirect, special, incidental, or consequential damages.",
            clause_type: "Liability",
            similarity_score: 0.65,
            metadata: { source: "fallback", document_title: "Sample Contract" }
        }
    ];
    
    // Filter based on query keywords
    const queryLower = query.toLowerCase();
    const filtered = sampleClauses.filter(clause => 
        clause.text.toLowerCase().includes(queryLower) || 
        clause.clause_type.toLowerCase().includes(queryLower)
    ).slice(0, nResults);
    
    return filtered.length > 0 ? filtered : sampleClauses.slice(0, nResults);
}

// Simple analyze
async function analyzeSimple(documentText, question = null) {
    const cacheKey = `analyze_${documentText.substring(0, 50)}_${question}`;
    const cached = cache.get(cacheKey);
    
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
        return cached.data;
    }
    
    try {
        const response = await fetchWithTimeout(`${CONFIG.CUAD_API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_text: documentText.substring(0, 2000), // Limit size
                question: question,
                n_references: 2
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });
        
        return data;
    } catch (error) {
        console.warn('CUAD analyze failed:', error.message);
        // Return simple fallback
        return {
            status: "fallback",
            document_preview: documentText.substring(0, 200),
            relevant_clauses_found: 0,
            analysis_prompt: question || "Please analyze this legal document.",
            analysis_ready: false
        };
    }
}

// Message handler - SIMPLIFIED
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background received:', request.action);
    
    // Handle requests immediately
    (async () => {
        try {
            switch (request.action) {
                case 'CHECK_CUAD_HEALTH':
                    sendResponse(await checkCUADHealth());
                    break;
                    
                case 'SEARCH_CUAD':
                    sendResponse(await searchCUADSimple(request.query, request.nResults || 3));
                    break;
                    
                case 'ANALYZE_WITH_CUAD':
                    sendResponse(await analyzeSimple(request.documentText, request.question));
                    break;
                    
                case 'GET_GPT_RESPONSE':
                    // Simple fallback for GPT
                    sendResponse({
                        fallback: true,
                        content: "Analysis based on CUAD references: This appears to be a legal document containing standard provisions. For detailed analysis, please configure OpenAI API key in settings.",
                        timestamp: new Date().toISOString()
                    });
                    break;
                    
                case 'GET_ENHANCED_RESPONSE':
                    // Simplified enhanced response
                    const analysis = await analyzeSimple(request.documentText, request.question);
                    sendResponse({
                        fallback: true,
                        content: `Analysis based on document context: ${analysis.analysis_prompt}\n\n[Using CUAD RAG system - ${analysis.relevant_clauses_found} references found]`,
                        analysis: analysis,
                        timestamp: new Date().toISOString()
                    });
                    break;
                    
                case 'PING':
                    sendResponse({ status: 'pong', timestamp: Date.now() });
                    break;
                    
                default:
                    sendResponse({ error: 'Unknown action', action: request.action });
            }
        } catch (error) {
            console.error('Background error:', error);
            sendResponse({ 
                error: error.message,
                fallback: true,
                timestamp: new Date().toISOString()
            });
        }
    })();
    
    return true; // Keep message channel open for async response
});

// Initialize
console.log('✅ LegalGuardianGPT background script loaded');
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const instructionTextarea = document.getElementById('instruction');
    const submitBtn = document.getElementById('submit-btn');
    const statusBadge = document.getElementById('status-badge');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');
    const reportContent = document.getElementById('report-content');
    const downloadReportBtn = document.getElementById('download-report-btn');
    
    // Environment elements
    const browserStatus = document.getElementById('browser-status');
    const terminalStatus = document.getElementById('terminal-status');
    const filesystemStatus = document.getElementById('filesystem-status');
    const browserContent = document.getElementById('browser-content');
    const terminalContent = document.getElementById('terminal-content');
    const filesystemContent = document.getElementById('filesystem-content');
    
    // Event Listeners
    submitBtn.addEventListener('click', processInstruction);
    downloadReportBtn.addEventListener('click', downloadReport);
    
    // Process the user instruction
    async function processInstruction() {
        const instruction = instructionTextarea.value.trim();
        
        if (!instruction) {
            alert('Please enter an instruction for the AI agent.');
            return;
        }
        
        // Update UI to show processing state
        setStatus('processing');
        showLoading('Processing your instruction...');
        resetEnvironments();
        
        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ instruction })
            });
            
            const result = await response.json();
            
            // Hide loading overlay
            hideLoading();
            
            // Update UI based on result
            if (result.status === 'completed') {
                setStatus('completed');
                displayResults(result);
                displayReport(result.report);
                downloadReportBtn.disabled = false;
            } else {
                setStatus('failed');
                displayError(result.message);
            }
        } catch (error) {
            hideLoading();
            setStatus('failed');
            displayError('An error occurred while processing your instruction: ' + error.message);
        }
    }
    
    // Update the status badge
    function setStatus(status) {
        statusBadge.className = 'status-badge ' + status;
        statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }
    
    // Show loading overlay
    function showLoading(message) {
        loadingMessage.textContent = message;
        loadingOverlay.classList.remove('hidden');
    }
    
    // Hide loading overlay
    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }
    
    // Reset environment displays
    function resetEnvironments() {
        browserStatus.textContent = 'Inactive';
        browserStatus.className = 'env-status';
        terminalStatus.textContent = 'Inactive';
        terminalStatus.className = 'env-status';
        filesystemStatus.textContent = 'Inactive';
        filesystemStatus.className = 'env-status';

        browserContent.innerHTML = '<p class="env-placeholder">No browser tasks executed yet</p>';
        terminalContent.innerHTML = '<p class="env-placeholder">No terminal commands executed yet</p>';
        filesystemContent.innerHTML = '<p class="env-placeholder">No file operations executed yet</p>';

        // Clear the result container
        const resultContainer = document.getElementById('result-container');
        if (resultContainer) {
            resultContainer.innerHTML = '';
        }

        reportContent.innerHTML = '<p class="report-placeholder">The execution report will appear here after task completion</p>';
        downloadReportBtn.disabled = true;
    }
    
    // Display execution results in the environment cards
    function displayResults(result) {
        const results = result.results || [];
        
        // Process each result and update the appropriate environment card
        results.forEach(stepResult => {
            if (stepResult.status === 'error') {
                displayError(stepResult.message);
                return;
            }
            
            // Determine which environment this result belongs to
            if (stepResult.environment === "browser") {
                // Browser environment
                displayBrowserResult(stepResult);
            } else if (stepResult.environment === "terminal") {
                // Terminal environment
                displayTerminalResult(stepResult);
            } else if (stepResult.environment === "file_system") {
                // File system environment
                displayFileSystemResult(stepResult);
            } else if (stepResult.environment === "general_response") {
                // General response environment
                displayGeneralResponseResult(stepResult);
            } else if (stepResult.url || stepResult.query || stepResult.action_type === "review") {
                // Browser environment (fallback detection)
                displayBrowserResult(stepResult);
            } else if (stepResult.command || stepResult.stdout) {
                // Terminal environment (fallback detection)
                displayTerminalResult(stepResult);
            } else if (stepResult.action && ['create_file', 'read_file', 'write_file', 'append_file', 'delete_file'].includes(stepResult.action)) {
                // File system environment (fallback detection)
                displayFileSystemResult(stepResult);
            } else if (stepResult.action_type === "general_response") {
                // General response (fallback detection)
                displayGeneralResponseResult(stepResult);
            }
        });
    }
    
    // Display browser results
    function displayBrowserResult(result) {
        browserStatus.textContent = 'Active';
        browserStatus.className = 'env-status active';

        // Clear placeholder
        if (browserContent.querySelector('.env-placeholder')) {
            browserContent.innerHTML = '';
        }

        const resultElement = document.createElement('div');
        resultElement.className = 'browser-result';

        // Add step number if available
        if (result.step_number) {
            const stepBadge = document.createElement('div');
            stepBadge.className = 'step-badge';
            stepBadge.textContent = `Step ${result.step_number}`;
            resultElement.appendChild(stepBadge);
        }

        if (result.url) {
            // Web navigation result
            resultElement.innerHTML += `
                <h4>Page Visited</h4>
                <div class="url">${result.url}</div>
                <div class="title">${result.title || 'No title'}</div>
                <div class="content-preview">${result.content_preview || ''}</div>
            `;
        } else if (result.query) {
            // Search result
            resultElement.innerHTML += `
                <h4>Search Results for "${result.query}"</h4>
                <div class="search-source">${result.source === 'serpapi' ? 'Results from SerpAPI' : 'Results from web search'}</div>
                <ul class="search-results">
                    ${result.results.map(item => `
                        <li class="search-result-item">
                            <div class="result-title">${item.title}</div>
                            <a href="${item.link}" target="_blank" class="result-link">${item.link}</a>
                            ${item.snippet ? `<div class="result-snippet">${item.snippet}</div>` : ''}
                        </li>
                    `).join('')}
                </ul>
            `;
        } else if (result.action_type === "review") {
            // Review action
            resultElement.innerHTML += `
                <h4>Content Review</h4>
                <div class="review-target"><strong>Reviewed:</strong> ${result.review_target}</div>
                <div class="review-summary"><strong>Summary:</strong> ${result.summary}</div>
                <div class="review-analysis">${result.analysis}</div>

                ${result.previous_results && result.previous_results.length > 0 ? `
                    <div class="previous-results">
                        <h5>Based on these sources:</h5>
                        <ul class="search-results">
                            ${result.previous_results.map(item => `
                                <li class="search-result-item">
                                    <div class="result-title">${item.title || 'No title'}</div>
                                    ${item.link ? `<a href="${item.link}" target="_blank" class="result-link">${item.link}</a>` : ''}
                                    ${item.snippet ? `<div class="result-snippet">${item.snippet}</div>` : ''}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
        } else if (result.action_type === "extraction") {
            // Extraction action
            const extractionType = result.extraction_type;

            resultElement.innerHTML += `
                <h4>Content Extraction</h4>
                <div class="extraction-target"><strong>Extracted:</strong> ${result.target}</div>
                <div class="extraction-type"><strong>Type:</strong> ${extractionType}</div>
            `;

            if (extractionType === "headlines") {
                resultElement.innerHTML += `
                    <div class="extracted-content">
                        <h5>Top Headlines</h5>
                        <ul class="headline-list">
                            ${result.extracted_content.map(item => `
                                <li class="headline-item">
                                    <div class="headline-title">${item.headline || 'No headline'}</div>
                                    <div class="headline-source">Source: ${item.source || 'Unknown'}</div>
                                    <a href="${item.url}" target="_blank" class="headline-link">${item.url}</a>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            } else if (extractionType === "pros_cons") {
                resultElement.innerHTML += `
                    <div class="extracted-content">
                        <h5>Product Reviews</h5>
                        ${result.extracted_content.map(item => `
                            <div class="product-review">
                                <h6>${item.product || 'Unknown Product'}</h6>
                                <div class="pros-cons-container">
                                    <div class="pros">
                                        <h6>Pros</h6>
                                        <ul>
                                            ${item.pros.map(pro => `<li>${pro}</li>`).join('')}
                                        </ul>
                                    </div>
                                    <div class="cons">
                                        <h6>Cons</h6>
                                        <ul>
                                            ${item.cons.map(con => `<li>${con}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                                <div class="product-source">Source: <a href="${item.source}" target="_blank">${item.source}</a></div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else if (extractionType === "trends") {
                resultElement.innerHTML += `
                    <div class="extracted-content">
                        <h5>Trend Analysis</h5>
                        <div class="trend-topics">
                            <h6>Key Trends</h6>
                            <ul>
                                ${result.extracted_content.trend_topics.map(topic => `<li>${topic}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="trend-data">
                            <h6>Trend Data</h6>
                            <table class="trend-table">
                                <thead>
                                    <tr>
                                        <th>Year</th>
                                        <th>Value</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${result.extracted_content.trend_data.map(data => `
                                        <tr>
                                            <td>${data.year}</td>
                                            <td>${data.value}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                        <div class="trend-sources">
                            <h6>Sources</h6>
                            <ul>
                                ${result.extracted_content.sources.map(source => `
                                    <li><a href="${source}" target="_blank">${source}</a></li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            } else if (extractionType === "summary") {
                resultElement.innerHTML += `
                    <div class="extracted-content">
                        <h5>Summary</h5>
                        <div class="summary-text">${result.extracted_content.summary}</div>
                        <div class="key-points">
                            <h6>Key Points</h6>
                            <ul>
                                ${result.extracted_content.key_points.map(point => `<li>${point}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="summary-sources">
                            <h6>Sources</h6>
                            <ul>
                                ${result.extracted_content.sources.map(source => `
                                    <li><a href="${source}" target="_blank">${source}</a></li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            } else {
                // General extraction
                resultElement.innerHTML += `
                    <div class="extracted-content">
                        <h5>Extracted Information</h5>
                        <div class="general-extraction">
                            ${result.extracted_content.map(item => `
                                <div class="extraction-item">
                                    <h6>${item.title || 'No title'}</h6>
                                    <div class="extraction-content">${item.content || 'No content'}</div>
                                    <div class="extraction-source">Source: <a href="${item.source}" target="_blank">${item.source}</a></div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }

            resultElement.innerHTML += `
                ${result.previous_results && result.previous_results.length > 0 ? `
                    <div class="previous-results">
                        <h5>Based on these sources:</h5>
                        <ul class="search-results">
                            ${result.previous_results.map(item => `
                                <li class="search-result-item">
                                    <div class="result-title">${item.title || 'No title'}</div>
                                    ${item.link ? `<a href="${item.link}" target="_blank" class="result-link">${item.link}</a>` : ''}
                                    ${item.snippet ? `<div class="result-snippet">${item.snippet}</div>` : ''}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
        } else if (result.action_type === "optional") {
            // Optional action
            resultElement.innerHTML += `
                <h4>Optional Step</h4>
                <div class="optional-action"><strong>Action:</strong> ${result.action}</div>
                <div class="optional-message">${result.message}</div>
            `;
        } else {
            // Generic browser action
            resultElement.innerHTML += `
                <h4>Browser Action</h4>
                <div class="action-description">${result.action || 'No action description'}</div>
                ${result.expected_outcome ? `<div class="expected-outcome"><strong>Expected outcome:</strong> ${result.expected_outcome}</div>` : ''}
                ${result.message ? `<div class="action-message">${result.message}</div>` : ''}
            `;
        }

        browserContent.appendChild(resultElement);
    }
    
    // Display terminal results
    function displayTerminalResult(result) {
        terminalStatus.textContent = 'Active';
        terminalStatus.className = 'env-status active';

        // Clear placeholder
        if (terminalContent.querySelector('.env-placeholder')) {
            terminalContent.innerHTML = '';
        }

        const resultElement = document.createElement('div');
        resultElement.className = 'terminal-result';

        // Add step number if available
        if (result.step_number) {
            const stepBadge = document.createElement('div');
            stepBadge.className = 'step-badge';
            stepBadge.textContent = `Step ${result.step_number}`;
            resultElement.appendChild(stepBadge);
        }

        resultElement.innerHTML += `
            <div>Command: <code>${result.command}</code></div>
            <pre class="terminal-output">${result.stdout || ''}${result.stderr ? '\nError: ' + result.stderr : ''}</pre>
            <div>Exit Code: ${result.return_code}</div>
            ${result.expected_outcome ? `<div class="expected-outcome"><strong>Expected outcome:</strong> ${result.expected_outcome}</div>` : ''}
        `;

        terminalContent.appendChild(resultElement);
    }
    
    // Display file system results
    function displayFileSystemResult(result) {
        filesystemStatus.textContent = 'Active';
        filesystemStatus.className = 'env-status active';

        // Clear placeholder
        if (filesystemContent.querySelector('.env-placeholder')) {
            filesystemContent.innerHTML = '';
        }

        const resultElement = document.createElement('div');
        resultElement.className = 'file-operation';

        // Add step number if available
        if (result.step_number) {
            const stepBadge = document.createElement('div');
            stepBadge.className = 'step-badge';
            stepBadge.textContent = `Step ${result.step_number}`;
            resultElement.appendChild(stepBadge);
        }

        let operationName = '';
        switch (result.action) {
            case 'create_file':
                operationName = 'Created File';
                break;
            case 'read_file':
                operationName = 'Read File';
                break;
            case 'write_file':
                operationName = 'Wrote to File';
                break;
            case 'append_file':
                operationName = 'Appended to File';
                break;
            case 'delete_file':
                operationName = 'Deleted File';
                break;
            case 'save_to_file':
                operationName = 'Saved to File';
                break;
            case 'create_directory':
                operationName = 'Created Directory';
                break;
            case 'list_directory':
                operationName = 'Listed Directory';
                break;
            default:
                operationName = 'File Operation';
        }

        if (result.action === 'list_directory') {
            resultElement.innerHTML += `
                <div><span class="operation-type">${operationName}</span>: <span class="directory">${result.directory}</span></div>
                ${result.message ? `<div>${result.message}</div>` : ''}
                <div class="file-list">
                    <h4>Files:</h4>
                    <ul>
                        ${result.files.map(file => `<li>${file}</li>`).join('')}
                    </ul>
                </div>
                ${result.expected_outcome ? `<div class="expected-outcome"><strong>Expected outcome:</strong> ${result.expected_outcome}</div>` : ''}
            `;
        } else if (result.action === 'create_directory') {
            resultElement.innerHTML += `
                <div><span class="operation-type">${operationName}</span>: <span class="directory">${result.directory}</span></div>
                ${result.message ? `<div>${result.message}</div>` : ''}
                ${result.expected_outcome ? `<div class="expected-outcome"><strong>Expected outcome:</strong> ${result.expected_outcome}</div>` : ''}
            `;
        } else if (result.action === 'save_to_file') {
            resultElement.innerHTML += `
                <div><span class="operation-type">${operationName}</span>: <span class="filename">${result.filename}</span></div>
                ${result.message ? `<div>${result.message}</div>` : ''}
                <div class="content-preview">
                    <h4>Content Preview:</h4>
                    <pre>${result.content_preview || 'No preview available'}</pre>
                </div>
                ${result.expected_outcome ? `<div class="expected-outcome"><strong>Expected outcome:</strong> ${result.expected_outcome}</div>` : ''}
            `;
        } else {
            resultElement.innerHTML += `
                <div><span class="operation-type">${operationName}</span>: <span class="filename">${result.filename}</span></div>
                ${result.message ? `<div>${result.message}</div>` : ''}
                ${result.content ? `<pre>${result.content}</pre>` : ''}
                ${result.expected_outcome ? `<div class="expected-outcome"><strong>Expected outcome:</strong> ${result.expected_outcome}</div>` : ''}
            `;
        }

        filesystemContent.appendChild(resultElement);
    }
    
    // Display error message
    function displayError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.style.color = 'var(--danger-color)';
        errorElement.style.padding = '10px';
        errorElement.style.marginTop = '10px';
        errorElement.style.border = '1px solid var(--danger-color)';
        errorElement.style.borderRadius = 'var(--border-radius)';
        errorElement.textContent = message;

        // Display in the result container if it exists
        const resultContainer = document.getElementById('result-container');
        if (resultContainer) {
            // Clear any previous content
            resultContainer.innerHTML = '';
            resultContainer.appendChild(errorElement);
        }

        // Also display in the report content area
        reportContent.innerHTML = '';
        reportContent.appendChild(errorElement.cloneNode(true));
    }
    
    // Display the execution report
    function displayReport(report) {
        if (!report) {
            reportContent.innerHTML = '<p class="report-placeholder">No report was generated</p>';
            return;
        }
        
        // Convert markdown-like formatting to HTML
        const formattedReport = report
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^#### (.*$)/gm, '<h4>$1</h4>')
            .replace(/^##### (.*$)/gm, '<h5>$1</h5>')
            .replace(/^###### (.*$)/gm, '<h6>$1</h6>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/```([\s\S]*?)```/g, '<pre>$1</pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
        
        reportContent.innerHTML = formattedReport;
    }
    
    // Download the report as a text file
    function downloadReport() {
        const reportText = reportContent.innerText || 'No report available';
        const blob = new Blob([reportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ai_agent_report.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
});
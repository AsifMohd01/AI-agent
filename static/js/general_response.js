// Function to display general response results
function displayGeneralResponseResult(result) {
    // Create a new div for general response
    const resultContainer = document.getElementById('result-container');

    // Safety check - if resultContainer doesn't exist, create it
    let resultElement;

    if (!resultContainer) {
        console.warn("Result container not found, creating a fallback container");
        // Create a fallback container if the main one doesn't exist
        const fallbackContainer = document.createElement('div');
        fallbackContainer.id = 'result-container';
        fallbackContainer.className = 'result-container';

        // Find a safe place to append it
        const mainElement = document.querySelector('main');
        if (mainElement) {
            mainElement.appendChild(fallbackContainer);
        } else {
            // Last resort - append to body
            document.body.appendChild(fallbackContainer);
        }

        resultElement = document.createElement('div');
        resultElement.className = 'general-response-result';
        fallbackContainer.appendChild(resultElement);
    } else {
        resultElement = document.createElement('div');
        resultElement.className = 'general-response-result';

        // Add step number if available
        if (result.step_number) {
            const stepBadge = document.createElement('div');
            stepBadge.className = 'step-badge';
            stepBadge.textContent = `Step ${result.step_number}`;
            resultElement.appendChild(stepBadge);
        }
    }
    
    // Add the response content
    if (result.status === 'success') {
        resultElement.innerHTML += `
            <h3>AI Response</h3>
            <div class="response-text">${result.response ? result.response.replace(/\n/g, '<br>') : 'No response provided'}</div>
        `;
        
        // If a document was created, add download link
        if (result.document_created) {
            resultElement.innerHTML += `
                <div class="document-section">
                    <h4>Document Created</h4>
                    <p>Type: ${result.document_type === 'pdf' ? 'PDF (HTML for printing)' : 'Text'}</p>
                    <p>Filename: ${result.document_filename}</p>
                    <div class="document-preview">
                        <h5>Preview:</h5>
                        <pre>${result.document_content_preview || 'No preview available'}</pre>
                    </div>
                    <div class="document-actions">
                        <a href="/static/downloads/${result.document_filename}" class="download-btn" target="_blank">
                            ${result.document_type === 'pdf' ? 'Open & Print PDF' : 'View Document'}
                        </a>
                        <a href="/static/downloads/${result.document_filename}" class="download-btn" download>
                            Download ${result.document_type === 'pdf' ? 'HTML' : 'Text'} File
                        </a>
                    </div>
                    ${result.document_type === 'pdf' ? `
                    <div class="pdf-instructions">
                        <p><strong>To save as PDF:</strong> Open the document, then use your browser's print function (Ctrl+P or Cmd+P) and select "Save as PDF".</p>
                    </div>
                    ` : ''}
                </div>
            `;
        }
    } else {
        resultElement.innerHTML += `
            <div class="error-message">Error: ${result.message || 'Unknown error'}</div>
        `;
    }
    
    // Add expected outcome if available
    if (result.expected_outcome) {
        resultElement.innerHTML += `
            <div class="expected-outcome"><strong>Expected outcome:</strong> ${result.expected_outcome}</div>
        `;
    }
    
    // Add to the result container
    resultContainer.appendChild(resultElement);
}
document.addEventListener('DOMContentLoaded', function() {
    // Handle multiple select styling
    const outputFormat = document.querySelector('select[name="output_format"]');
    if (outputFormat) {
        outputFormat.setAttribute('multiple', 'true');
        outputFormat.style.height = '100px');
    }

    // Add loading state to form submission
    const form = document.getElementById('scan-form');
    if (form) {
        form.addEventListener('submit', function() {
            const button = document.getElementById('scan-button');
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split"></i> Scanning...';
            
            // Add loading overlay
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = `
                <div class="loading-spinner"></div>
                <div class="loading-text">Scanning repository...</div>
            `;
            document.body.appendChild(loadingOverlay);
        });
    }
    
    // Add tooltips to form elements
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseover', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltipEl = document.createElement('div');
            tooltipEl.className = 'tooltip';
            tooltipEl.textContent = tooltipText;
            document.body.appendChild(tooltipEl);
            
            const rect = this.getBoundingClientRect();
            tooltipEl.style.top = `${rect.bottom + 10}px`;
            tooltipEl.style.left = `${rect.left + (rect.width / 2) - (tooltipEl.offsetWidth / 2)}px`;
            
            this.addEventListener('mouseout', function() {
                tooltipEl.remove();
            });
        });
    });
    
    // Add copy button to tree view
    const treeView = document.querySelector('.tree-view');
    if (treeView) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-secondary copy-btn';
        copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
        copyBtn.addEventListener('click', function() {
            navigator.clipboard.writeText(treeView.textContent).then(() => {
                this.innerHTML = '<i class="bi bi-clipboard-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
                }, 2000);
            });
        });
        
        const treeHeader = document.querySelector('.card h3:contains("Repository Structure")');
        if (treeHeader) {
            treeHeader.appendChild(copyBtn);
        }
    }
    
    // Add file size formatter
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    // Update file size displays
    const fileSizes = document.querySelectorAll('.file-size');
    fileSizes.forEach(el => {
        const bytes = parseInt(el.getAttribute('data-bytes'));
        if (!isNaN(bytes)) {
            el.textContent = formatFileSize(bytes);
        }
    });
});

function createProgressBar() {
    const progressContainer = document.createElement('div');
    progressContainer.className = 'progress-container';
    
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    progressBar.style.width = '0%';
    
    const progressText = document.createElement('div');
    progressText.className = 'progress-text';
    progressText.textContent = 'Initializing...';
    
    progressContainer.appendChild(progressBar);
    progressContainer.appendChild(progressText);
    
    return {
        container: progressContainer,
        bar: progressBar,
        text: progressText,
        update: function(percent, message) {
            this.bar.style.width = `${percent}%`;
            if (message) {
                this.text.textContent = message;
            }
        }
    };
}

// Use this in the form submission handler
if (form) {
    form.addEventListener('submit', function() {
        const button = document.getElementById('scan-button');
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split"></i> Scanning...';
        
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        
        const progress = createProgressBar();
        
        loadingOverlay.appendChild(progress.container);
        document.body.appendChild(loadingOverlay);
        
        // Simulate progress (since we can't get real-time progress from the backend)
        let percent = 0;
        const interval = setInterval(() => {
            percent += 5;
            if (percent > 95) {
                clearInterval(interval);
                percent = 95;
                progress.update(percent, 'Finalizing...');
            } else if (percent > 80) {
                progress.update(percent, 'Generating output files...');
            } else if (percent > 60) {
                progress.update(percent, 'Processing repository content...');
            } else if (percent > 30) {
                progress.update(percent, 'Scanning files...');
            } else {
                progress.update(percent, 'Analyzing repository structure...');
            }
        }, 500);
    });
}

// Theme toggle functionality
const themeToggle = document.getElementById('theme-toggle');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

// Check for saved theme preference or use the system preference
const currentTheme = localStorage.getItem('theme') || 
                    (prefersDarkScheme.matches ? 'dark' : 'light');

// Set initial theme
if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
} else {
    document.documentElement.setAttribute('data-theme', 'light');
    themeToggle.innerHTML = '<i class="bi bi-moon-fill"></i>';
}

// Toggle theme when button is clicked
themeToggle.addEventListener('click', function() {
    let theme = 'light';
    
    if (document.documentElement.getAttribute('data-theme') === 'light') {
        document.documentElement.setAttribute('data-theme', 'dark');
        theme = 'dark';
        this.innerHTML = '<i class="bi bi-sun-fill"></i>';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        this.innerHTML = '<i class="bi bi-moon-fill"></i>';
    }
    
    // Save preference to localStorage
    localStorage.setItem('theme', theme);
});

function validateForm() {
    const repoUrl = document.getElementById('repo_url');
    const sizeLimit = document.getElementById('size_limit');
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.error-message').forEach(el => el.remove());
    
    // Validate repository URL/path
    if (!repoUrl.value.trim()) {
        showError(repoUrl, 'Repository URL or path is required');
        isValid = false;
    }
    
    // Validate size limit (if provided)
    if (sizeLimit.value && isNaN(parseInt(sizeLimit.value))) {
        showError(sizeLimit, 'Size limit must be a number');
        isValid = false;
    }
    
    return isValid;
}

function showError(element, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    element.parentNode.appendChild(errorDiv);
    element.classList.add('is-invalid');
}

// Update form submission handler
if (form) {
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
        
        // Continue with loading state...
        const button = document.getElementById('scan-button');
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split"></i> Scanning...';
        // ...
    });
}

const repoUrlInput = document.getElementById('repo_url');
const previewButton = document.getElementById('preview-repo');

if (previewButton && repoUrlInput) {
    previewButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        const repoUrl = repoUrlInput.value.trim();
        if (!repoUrl) {
            showError(repoUrlInput, 'Please enter a repository URL or path');
            return;
        }
        
        // Show loading state
        this.disabled = true;
        this.innerHTML = '<i class="bi bi-hourglass-split"></i> Loading...';
        
        // Make AJAX request to preview endpoint
        fetch(`/preview-repo?repo=${encodeURIComponent(repoUrl)}`)
            .then(response => response.json())
            .then(data => {
                this.disabled = false;
                this.innerHTML = '<i class="bi bi-eye"></i> Preview';
                
                if (data.error) {
                    showError(repoUrlInput, data.error);
                    return;
                }
                
                // Show preview modal
                showRepoPreview(data.tree, data.repo_name);
            })
            .catch(error => {
                this.disabled = false;
                this.innerHTML = '<i class="bi bi-eye"></i> Preview';
                showError(repoUrlInput, 'Failed to preview repository');
            });
    });
}

function showRepoPreview(tree, repoName) {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="bi bi-folder"></i> ${repoName}</h3>
                <button class="close-button">&times;</button>
            </div>
            <div class="modal-body">
                <div class="tree-view">${tree}</div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary close-modal">Close</button>
                <button class="btn btn-primary" id="proceed-scan">Proceed with Scan</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Handle close button
    modal.querySelector('.close-button').addEventListener('click', () => {
        modal.remove();
    });
    
    // Handle close modal button
    modal.querySelector('.close-modal').addEventListener('click', () => {
        modal.remove();
    });
    
    // Handle proceed button
    modal.querySelector('#proceed-scan').addEventListener('click', () => {
        modal.remove();
        document.getElementById('scan-form').submit();
    });
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize syntax highlighting
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
    });
});

function setupFilePreviewButtons() {
    document.querySelectorAll('.preview-file-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const filePath = this.getAttribute('data-path');
            
            // Show loading state
            this.disabled = true;
            this.innerHTML = '<i class="bi bi-hourglass-split"></i>';
            
            // Make AJAX request to get file content
            fetch(`/preview-file?path=${encodeURIComponent(filePath)}`)
                .then(response => response.json())
                .then(data => {
                    this.disabled = false;
                    this.innerHTML = '<i class="bi bi-eye"></i>';
                    
                    if (data.error) {
                        alert(`Error: ${data.error}`);
                        return;
                    }
                    
                    // Show file content modal
                    showFilePreview(data.content, filePath, data.language);
                })
                .catch(error => {
                    this.disabled = false;
                    this.innerHTML = '<i class="bi bi-eye"></i>';
                    alert('Failed to preview file');
                });
        });
    });
}

function showFilePreview(content, filePath, language) {
    const fileName = filePath.split('/').pop();
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content file-preview-modal">
            <div class="modal-header">
                <h3><i class="bi bi-file-earmark"></i> ${fileName}</h3>
                <button class="close-button">&times;</button>
            </div>
            <div class="modal-body">
                <pre><code class="language-${language}">${escapeHtml(content)}</code></pre>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary close-modal">Close</button>
                <a href="/download-file?path=${encodeURIComponent(filePath)}" class="btn btn-primary">
                    <i class="bi bi-download"></i> Download
                </a>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Initialize syntax highlighting
    modal.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
    });
    
    // Handle close button
    modal.querySelector('.close-button').addEventListener('click', () => {
        modal.remove();
    });
    
    // Handle close modal button
    modal.querySelector('.close-modal').addEventListener('click', () => {
        modal.remove();
    });
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Call this function when the page loads
document.addEventListener('DOMContentLoaded', function() {
    setupFilePreviewButtons();
});

function setupAccordion() {
    document.querySelectorAll('.accordion-button').forEach(button => {
        button.addEventListener('click', function() {
            const target = document.querySelector(this.getAttribute('data-bs-target'));
            
            // Toggle this accordion item
            this.classList.toggle('collapsed');
            target.classList.toggle('show');
            
            // Close other accordion items
            if (!this.classList.contains('collapsed')) {
                document.querySelectorAll('.accordion-button').forEach(otherButton => {
                    if (otherButton !== this) {
                        otherButton.classList.add('collapsed');
                        const otherTarget = document.querySelector(otherButton.getAttribute('data-bs-target'));
                        otherTarget.classList.remove('show');
                    }
                });
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setupAccordion();
});

function saveRecentScan(repoUrl, summary) {
    let recentScans = JSON.parse(localStorage.getItem('recentScans') || '[]');
    
    // Add new scan to the beginning
    recentScans.unshift({
        repoUrl: repoUrl,
        repoName: summary.repo_name,
        timestamp: new Date().toISOString(),
        fileCount: summary.total_files,
        fileTypes: summary.file_types
    });
    
    // Keep only the last 5 scans
    recentScans = recentScans.slice(0, 5);
    
    localStorage.setItem('recentScans', JSON.stringify(recentScans));
}

function displayRecentScans() {
    const recentScans = JSON.parse(localStorage.getItem('recentScans') || '[]');
    const recentScansContainer = document.getElementById('recent-scans');
    
    if (!recentScansContainer || recentScans.length === 0) {
        return;
    }
    
    recentScansContainer.innerHTML = '';
    
    recentScans.forEach(scan => {
        const scanDate = new Date(scan.timestamp);
        const formattedDate = scanDate.toLocaleDateString() + ' ' + scanDate.toLocaleTimeString();
        
        const scanItem = document.createElement('div');
        scanItem.className = 'recent-scan-item';
        scanItem.innerHTML = `
            <div class="scan-info">
                <div class="scan-name">${scan.repoName}</div>
                <div class="scan-meta">${formattedDate} • ${scan.fileCount} files</div>
            </div>
            <button class="btn btn-sm btn-secondary use-repo-btn" data-repo="${scan.repoUrl}">
                Use
            </button>
        `;
        
        recentScansContainer.appendChild(scanItem);
    });
    
    // Add event listeners to "Use" buttons
    document.querySelectorAll('.use-repo-btn').forEach(button => {
        button.addEventListener('click', function() {
            const repoUrl = this.getAttribute('data-repo');
            document.getElementById('repo_url').value = repoUrl;
        });
    });
}

// Call this on page load
document.addEventListener('DOMContentLoaded', function() {
    displayRecentScans();
});

// Save scan when results page loads
if (document.querySelector('.results-header')) {
    const summaryData = JSON.parse(document.getElementById('summary-data').textContent);
    const repoUrl = document.getElementById('repo-url').textContent;
    saveRecentScan(repoUrl, summaryData);
}


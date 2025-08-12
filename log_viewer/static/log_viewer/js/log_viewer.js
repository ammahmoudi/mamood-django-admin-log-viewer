/**
 * Log Viewer JavaScript with Smart Auto-Refresh
 */

class LogViewer {
    constructor(options) {
        this.filename = options.filename;
        this.currentPage = options.currentPage;
        this.refreshInterval = Math.max(options.refreshInterval, 10000); // Minimum 10 seconds
        this.onlyRefreshWhenActive = options.onlyRefreshWhenActive !== false; // Default true
        this.autoRefreshDefault = options.autoRefreshDefault !== false; // Default true
        this.autoScrollToBottom = options.autoScrollToBottom !== false; // Default true
        this.ajaxUrl = options.ajaxUrl;
        this.autoRefresh = this.autoRefreshDefault; // Use default setting
        this.refreshTimer = null;
        this.lastRefreshTime = 0;
        this.refreshCount = 0;
        this.isVisible = true;
        this.lastLogContent = '';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupVisibilityDetection();
        // Start auto-refresh if enabled by default
        if (this.autoRefresh) {
            this.startAutoRefresh();
        }
        this.updateRefreshButton();
        // Auto-scroll to bottom on initial load if enabled
        if (this.autoScrollToBottom) {
            this.scrollToBottom();
        }
    }
    
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-log');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshLog(true)); // Manual refresh
        }
        
        // Auto-refresh toggle
        const autoRefreshBtn = document.getElementById('auto-refresh-toggle');
        if (autoRefreshBtn) {
            autoRefreshBtn.addEventListener('click', () => this.toggleAutoRefresh());
        }
        
        // Auto-scroll toggle
        const autoScrollBtn = document.getElementById('auto-scroll-toggle');
        if (autoScrollBtn) {
            autoScrollBtn.addEventListener('click', () => this.toggleAutoScroll());
        }
        
        // Log level filter
        const levelFilter = document.getElementById('log-level-filter');
        if (levelFilter) {
            levelFilter.addEventListener('change', (e) => this.filterByLevel(e.target.value));
        }
    }
    
    setupVisibilityDetection() {
        // Only refresh when page is visible (if the setting is enabled)
        if (this.onlyRefreshWhenActive) {
            document.addEventListener('visibilitychange', () => {
                this.isVisible = !document.hidden;
                if (this.isVisible && this.autoRefresh) {
                    // Resume auto-refresh when page becomes visible
                    this.startAutoRefresh();
                } else {
                    // Stop auto-refresh when page is hidden
                    this.stopAutoRefresh();
                }
            });
        }
    }
    
    startAutoRefresh() {
        const shouldRefresh = this.autoRefresh && this.refreshInterval > 0 && 
                             (this.onlyRefreshWhenActive ? this.isVisible : true);
        
        if (shouldRefresh) {
            // Clear any existing timer
            this.stopAutoRefresh();
            
            this.refreshTimer = setInterval(() => {
                this.refreshLog(false); // Auto refresh
            }, this.refreshInterval);
        }
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    toggleAutoRefresh() {
        const btn = document.getElementById('auto-refresh-toggle');
        this.autoRefresh = !this.autoRefresh;
        
        if (this.autoRefresh) {
            btn.textContent = `Auto-refresh: ON (${this.refreshInterval/1000}s)`;
            btn.className = 'button default active';
            this.startAutoRefresh();
        } else {
            btn.textContent = 'Auto-refresh: OFF';
            btn.className = 'button default inactive';
            this.stopAutoRefresh();
        }
    }
    
    toggleAutoScroll() {
        this.autoScrollToBottom = !this.autoScrollToBottom;
        this.updateRefreshButton(); // This will update the auto-scroll button appearance
        
        // If enabling auto-scroll, scroll to bottom immediately
        if (this.autoScrollToBottom) {
            this.scrollToBottom();
        }
    }
    
    updateRefreshButton() {
        const autoRefreshBtn = document.getElementById('auto-refresh-toggle');
        if (autoRefreshBtn) {
            autoRefreshBtn.textContent = this.autoRefresh ? 'Auto-refresh: ON' : 'Auto-refresh: OFF';
            autoRefreshBtn.className = this.autoRefresh ? 'button default active' : 'button default inactive';
        }
        
        const autoScrollBtn = document.getElementById('auto-scroll-toggle');
        if (autoScrollBtn) {
            autoScrollBtn.textContent = this.autoScrollToBottom ? 'Auto-scroll: ON' : 'Auto-scroll: OFF';
            autoScrollBtn.className = this.autoScrollToBottom ? 'button default active' : 'button default inactive';
        }
    }
    
    refreshLog(isManual = false) {
        const now = Date.now();
        
        // Rate limiting: prevent too frequent refreshes
        if (!isManual && (now - this.lastRefreshTime) < 5000) { // Minimum 5 seconds between auto-refreshes
            return;
        }
        
        this.lastRefreshTime = now;
        this.refreshCount++;
        
        // Show loading indicator for manual refresh
        if (isManual) {
            const refreshBtn = document.getElementById('refresh-log');
            if (refreshBtn) {
                refreshBtn.textContent = 'Refreshing...';
                refreshBtn.disabled = true;
            }
        }
        
        const url = new URL(this.ajaxUrl, window.location.origin);
        url.searchParams.set('page', this.currentPage);
        
        // Add a timestamp to prevent caching
        url.searchParams.set('t', now);
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error refreshing log:', data.error);
                    return;
                }
                
                // Check if content actually changed
                const newContent = JSON.stringify(data.log_lines);
                if (newContent !== this.lastLogContent) {
                    this.updateLogContent(data);
                    this.lastLogContent = newContent;
                    
                    // Show visual indicator that content was updated
                    if (!isManual) {
                        this.showUpdateIndicator();
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching log data:', error);
                
                // Slow down auto-refresh on errors
                if (!isManual && this.autoRefresh) {
                    this.refreshInterval = Math.min(this.refreshInterval * 1.5, 60000); // Max 1 minute
                }
            })
            .finally(() => {
                // Reset refresh button
                if (isManual) {
                    const refreshBtn = document.getElementById('refresh-log');
                    if (refreshBtn) {
                        refreshBtn.textContent = 'Refresh';
                        refreshBtn.disabled = false;
                    }
                }
            });
    }
    
    showUpdateIndicator() {
        // Create a small visual indicator that content was updated
        const indicator = document.createElement('div');
        indicator.className = 'update-indicator';
        indicator.textContent = '● Updated';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            opacity: 0.9;
            transition: opacity 0.3s;
        `;
        
        document.body.appendChild(indicator);
        
        // Remove the indicator after 2 seconds
        setTimeout(() => {
            if (indicator && indicator.parentNode) {
                indicator.style.opacity = '0';
                setTimeout(() => {
                    if (indicator.parentNode) {
                        indicator.parentNode.removeChild(indicator);
                    }
                }, 300);
            }
        }, 2000);
    }
    
    updateLogContent(data) {
        const tbody = document.getElementById('log-lines');
        if (!tbody) return;
        
        // Clear existing content
        tbody.innerHTML = '';
        
        // Add new log lines
        data.log_lines.forEach(line => {
            const row = this.createLogRow(line);
            tbody.appendChild(row);
        });
        
        // Update info display
        this.updateLogInfo(data);
        
        // Reapply current filter
        const currentFilter = document.getElementById('log-level-filter').value;
        if (currentFilter) {
            this.filterByLevel(currentFilter);
        }
        
        // Auto-scroll to bottom if enabled
        if (this.autoScrollToBottom) {
            this.scrollToBottom();
        }
    }
    
    createLogRow(line) {
        const row = document.createElement('tr');
        row.className = `log-line log-level-${line.level.toLowerCase()}`;
        row.setAttribute('data-level', line.level);
        
        row.innerHTML = `
            <td class="line-number">${line.number}</td>
            <td class="log-level">
                <span class="level-badge level-${line.level.toLowerCase()}">${line.level}</span>
            </td>
            <td class="timestamp">${line.timestamp}</td>
            <td class="message">${this.escapeHtml(line.content)}</td>
        `;
        
        return row;
    }
    
    updateLogInfo(data) {
        // Update total lines if element exists
        const totalLinesEl = document.querySelector('.log-file-info p:nth-child(4)');
        if (totalLinesEl) {
            totalLinesEl.innerHTML = `<strong>Total Lines:</strong> ${data.total_lines}`;
        }
        
        // Update showing range if element exists
        const showingEl = document.querySelector('.log-file-info p:nth-child(5)');
        if (showingEl) {
            showingEl.innerHTML = `<strong>Showing:</strong> Lines ${data.start_line} - ${data.end_line}`;
        }
        
        // Update last refresh time
        const refreshInfo = document.querySelector('.refresh-info') || this.createRefreshInfo();
        refreshInfo.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    }
    
    createRefreshInfo() {
        const info = document.createElement('p');
        info.className = 'refresh-info';
        info.style.cssText = 'font-size: 12px; color: #666; margin: 5px 0;';
        
        const logInfo = document.querySelector('.log-file-info');
        if (logInfo) {
            logInfo.appendChild(info);
        }
        
        return info;
    }
    
    filterByLevel(level) {
        const rows = document.querySelectorAll('.log-line');
        
        rows.forEach(row => {
            const rowLevel = row.getAttribute('data-level');
            
            if (!level || rowLevel === level) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        // Update visible count
        const visibleRows = document.querySelectorAll('.log-line:not([style*="display: none"])');
        console.log(`Showing ${visibleRows.length} of ${rows.length} log entries`);
    }
    
    scrollToBottom() {
        // Scroll to the bottom of the log content smoothly
        const logContainer = document.querySelector('.log-content');
        if (logContainer) {
            setTimeout(() => {
                logContainer.scrollTop = logContainer.scrollHeight;
            }, 100); // Small delay to ensure content is rendered
        }
        
        // Alternative: scroll to the last log row if container scroll doesn't work
        const lastRow = document.querySelector('#log-lines tr:last-child');
        if (lastRow) {
            lastRow.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    destroy() {
        this.stopAutoRefresh();
    }
}

// Export for use in templates
window.LogViewer = LogViewer;

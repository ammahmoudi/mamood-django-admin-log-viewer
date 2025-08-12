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
        
        // Filter state
        this.filters = {
            search: '',
            level: '',
            timeFrom: '',
            timeTo: '',
            regex: '',
            multilineOnly: ''
        };
        this.filteredRows = [];
        this.originalRows = [];
        
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
        
        // Toggle filters panel
        const toggleFiltersBtn = document.getElementById('toggle-filters');
        if (toggleFiltersBtn) {
            toggleFiltersBtn.addEventListener('click', () => this.toggleFiltersPanel());
        }
        
        // Filter controls
        this.setupFilterControls();
    }
    
    setupFilterControls() {
        // Search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.applyFilters(), 300));
        }
        
        // Log level filter
        const levelFilter = document.getElementById('log-level-filter');
        if (levelFilter) {
            levelFilter.addEventListener('change', () => this.applyFilters());
        }
        
        // Time filters
        const timeFrom = document.getElementById('time-from');
        const timeTo = document.getElementById('time-to');
        if (timeFrom) timeFrom.addEventListener('change', () => this.applyFilters());
        if (timeTo) timeTo.addEventListener('change', () => this.applyFilters());
        
        // Regex search
        const regexSearch = document.getElementById('regex-search');
        if (regexSearch) {
            regexSearch.addEventListener('input', this.debounce(() => this.applyFilters(), 500));
        }
        
        // Multiline filter
        const multilineOnly = document.getElementById('multiline-only');
        if (multilineOnly) {
            multilineOnly.addEventListener('change', () => this.applyFilters());
        }
        
        // Quick time filter buttons
        document.querySelectorAll('.quick-time-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.setQuickTimeFilter(e.target.dataset.hours));
        });
        
        // Filter action buttons
        const applyFiltersBtn = document.getElementById('apply-filters');
        const clearFiltersBtn = document.getElementById('clear-filters');
        if (applyFiltersBtn) applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        if (clearFiltersBtn) clearFiltersBtn.addEventListener('click', () => this.clearFilters());
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
    
    // Filter and Search Methods
    toggleFiltersPanel() {
        const panel = document.getElementById('filters-panel');
        const btn = document.getElementById('toggle-filters');
        
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            btn.textContent = 'Hide Filters';
        } else {
            panel.style.display = 'none';
            btn.textContent = 'Show Filters';
        }
    }
    
    setQuickTimeFilter(hours) {
        const now = new Date();
        const fromTime = new Date(now.getTime() - (hours * 60 * 60 * 1000));
        
        const timeFrom = document.getElementById('time-from');
        const timeTo = document.getElementById('time-to');
        
        if (timeFrom) timeFrom.value = this.formatDateTimeLocal(fromTime);
        if (timeTo) timeTo.value = this.formatDateTimeLocal(now);
        
        // Update active button
        document.querySelectorAll('.quick-time-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        this.applyFilters();
    }
    
    formatDateTimeLocal(date) {
        // Format date for datetime-local input
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    }
    
    applyFilters() {
        // Get current filter values
        this.filters.search = document.getElementById('search-input')?.value || '';
        this.filters.level = document.getElementById('log-level-filter')?.value || '';
        this.filters.timeFrom = document.getElementById('time-from')?.value || '';
        this.filters.timeTo = document.getElementById('time-to')?.value || '';
        this.filters.regex = document.getElementById('regex-search')?.value || '';
        this.filters.multilineOnly = document.getElementById('multiline-only')?.value || '';
        
        const tbody = document.getElementById('log-lines');
        if (!tbody) return;
        
        const rows = Array.from(tbody.querySelectorAll('tr'));
        this.originalRows = rows.slice(); // Keep original for clearing filters
        
        let visibleCount = 0;
        
        rows.forEach(row => {
            const shouldShow = this.shouldShowRow(row);
            row.style.display = shouldShow ? '' : 'none';
            if (shouldShow) visibleCount++;
        });
        
        this.updateFilterStatus(visibleCount, rows.length);
    }
    
    shouldShowRow(row) {
        // Level filter
        if (this.filters.level && row.getAttribute('data-level') !== this.filters.level) {
            return false;
        }
        
        // Multiline filter
        if (this.filters.multilineOnly === 'multiline' && !row.classList.contains('multiline-entry')) {
            return false;
        }
        if (this.filters.multilineOnly === 'single' && row.classList.contains('multiline-entry')) {
            return false;
        }
        
        // Get row text content for searching
        const messageCell = row.querySelector('.message');
        const timestampCell = row.querySelector('.timestamp');
        const messageText = messageCell ? messageCell.textContent : '';
        const timestamp = timestampCell ? timestampCell.textContent : '';
        
        // Text search
        if (this.filters.search) {
            if (!messageText.toLowerCase().includes(this.filters.search.toLowerCase())) {
                return false;
            }
        }
        
        // Regex search
        if (this.filters.regex) {
            try {
                const regex = new RegExp(this.filters.regex, 'i');
                if (!regex.test(messageText)) {
                    return false;
                }
            } catch (e) {
                // Invalid regex, ignore this filter
                console.warn('Invalid regex pattern:', this.filters.regex);
            }
        }
        
        // Time range filter
        if ((this.filters.timeFrom || this.filters.timeTo) && timestamp) {
            const logTime = this.parseLogTimestamp(timestamp);
            if (logTime) {
                if (this.filters.timeFrom) {
                    const fromTime = new Date(this.filters.timeFrom);
                    if (logTime < fromTime) return false;
                }
                if (this.filters.timeTo) {
                    const toTime = new Date(this.filters.timeTo);
                    if (logTime > toTime) return false;
                }
            }
        }
        
        return true;
    }
    
    parseLogTimestamp(timestampStr) {
        // Parse timestamp in format "YYYY-MM-DD HH:MM:SS"
        const match = timestampStr.match(/(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})/);
        if (match) {
            return new Date(`${match[1]}T${match[2]}`);
        }
        return null;
    }
    
    updateFilterStatus(visibleCount, totalCount) {
        // Show filter status
        let statusEl = document.getElementById('filter-status');
        if (!statusEl) {
            statusEl = document.createElement('div');
            statusEl.id = 'filter-status';
            statusEl.className = 'active-filters';
            const filtersPanel = document.getElementById('filters-panel');
            filtersPanel.parentNode.insertBefore(statusEl, filtersPanel.nextSibling);
        }
        
        const hasActiveFilters = Object.values(this.filters).some(value => value !== '');
        
        if (hasActiveFilters) {
            statusEl.style.display = 'block';
            statusEl.innerHTML = `
                <strong>Filters Active:</strong> Showing ${visibleCount} of ${totalCount} entries
                ${this.getActiveFilterTags()}
            `;
        } else {
            statusEl.style.display = 'none';
        }
    }
    
    getActiveFilterTags() {
        const tags = [];
        
        if (this.filters.search) {
            tags.push(`<span class="filter-tag">Search: "${this.filters.search}" <span class="remove-filter" onclick="clearSearchFilter()">×</span></span>`);
        }
        if (this.filters.level) {
            tags.push(`<span class="filter-tag">Level: ${this.filters.level} <span class="remove-filter" onclick="clearLevelFilter()">×</span></span>`);
        }
        if (this.filters.timeFrom || this.filters.timeTo) {
            const timeRange = `${this.filters.timeFrom || 'start'} to ${this.filters.timeTo || 'end'}`;
            tags.push(`<span class="filter-tag">Time: ${timeRange} <span class="remove-filter" onclick="clearTimeFilter()">×</span></span>`);
        }
        if (this.filters.regex) {
            tags.push(`<span class="filter-tag">Regex: ${this.filters.regex} <span class="remove-filter" onclick="clearRegexFilter()">×</span></span>`);
        }
        if (this.filters.multilineOnly) {
            tags.push(`<span class="filter-tag">Type: ${this.filters.multilineOnly} <span class="remove-filter" onclick="clearMultilineFilter()">×</span></span>`);
        }
        
        return tags.length > 0 ? '<br>' + tags.join(' ') : '';
    }
    
    clearFilters() {
        // Clear all filter inputs
        document.getElementById('search-input').value = '';
        document.getElementById('log-level-filter').value = '';
        document.getElementById('time-from').value = '';
        document.getElementById('time-to').value = '';
        document.getElementById('regex-search').value = '';
        document.getElementById('multiline-only').value = '';
        
        // Remove active state from quick time buttons
        document.querySelectorAll('.quick-time-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Clear filters object
        Object.keys(this.filters).forEach(key => {
            this.filters[key] = '';
        });
        
        // Show all rows
        const tbody = document.getElementById('log-lines');
        if (tbody) {
            const rows = tbody.querySelectorAll('tr');
            rows.forEach(row => {
                row.style.display = '';
            });
        }
        
        // Update status
        this.updateFilterStatus(this.originalRows.length, this.originalRows.length);
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Remove the old filterByLevel method since it's now handled by applyFilters
    
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
        
        // Reapply all current filters
        this.applyFilters();
        
        // Auto-scroll to bottom if enabled
        if (this.autoScrollToBottom) {
            this.scrollToBottom();
        }
    }
    
    createLogRow(line) {
        const row = document.createElement('tr');
        let className = `log-line log-level-${line.level.toLowerCase()}`;
        if (line.is_multiline) {
            className += ' multiline-entry';
        }
        row.className = className;
        row.setAttribute('data-level', line.level);
        
        // Create the view full button if needed
        let actionCell = '<td class="action"></td>';
        if (line.is_long || line.is_multiline) {
            const escapedContent = this.escapeHtml(line.full_content).replace(/'/g, "&#39;");
            actionCell = `<td class="action">
                <button class="view-full-btn" onclick="showLogModal('${escapedContent}', '${line.level}', '${line.timestamp}', '${line.line_range}')">View Full</button>
            </td>`;
        }
        
        // Add multiline indicator
        let lineNumberCell = line.line_range || line.number;
        if (line.is_multiline) {
            lineNumberCell += ' <span class="multiline-indicator" title="Multi-line entry (' + line.line_count + ' lines)">📄</span>';
        }
        
        row.innerHTML = `
            <td class="line-number">${lineNumberCell}</td>
            <td class="log-level">
                <span class="level-badge level-${line.level.toLowerCase()}">${line.level}</span>
            </td>
            <td class="timestamp">${line.timestamp}</td>
            <td class="message">
                <div class="message-preview">${this.escapeHtml(line.content)}</div>
                ${line.is_long ? '<div class="message-truncated-indicator">Content truncated...</div>' : ''}
            </td>
            ${actionCell}
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

// Global functions for filter tag removal
function clearSearchFilter() {
    document.getElementById('search-input').value = '';
    if (window.logViewer) window.logViewer.applyFilters();
}

function clearLevelFilter() {
    document.getElementById('log-level-filter').value = '';
    if (window.logViewer) window.logViewer.applyFilters();
}

function clearTimeFilter() {
    document.getElementById('time-from').value = '';
    document.getElementById('time-to').value = '';
    document.querySelectorAll('.quick-time-btn').forEach(btn => btn.classList.remove('active'));
    if (window.logViewer) window.logViewer.applyFilters();
}

function clearRegexFilter() {
    document.getElementById('regex-search').value = '';
    if (window.logViewer) window.logViewer.applyFilters();
}

function clearMultilineFilter() {
    document.getElementById('multiline-only').value = '';
    if (window.logViewer) window.logViewer.applyFilters();
}

// Export for use in templates
window.LogViewer = LogViewer;

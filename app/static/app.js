// Global state for filtering and sorting
let allJobs = []; // Полный список jobs
let activeFilters = {
    status: [],
    visa: [],
    match: []
};
let sortConfig = {
    field: null,
    direction: 'asc'
};

// Load filters from localStorage on startup
function loadFiltersFromStorage() {
    const saved = localStorage.getItem('jobFilters');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            activeFilters = parsed.filters || activeFilters;
            sortConfig = parsed.sort || sortConfig;
            applyFilterUIState();
            applySortUIState();
        } catch (e) {
            console.error('Error loading filters from storage:', e);
        }
    }
}

// Save filters to localStorage
function saveFiltersToStorage() {
    localStorage.setItem('jobFilters', JSON.stringify({
        filters: activeFilters,
        sort: sortConfig
    }));
}

// Apply filter UI state from loaded data
function applyFilterUIState() {
    document.querySelectorAll('.chip').forEach(chip => {
        const filterType = chip.dataset.filter;
        const value = chip.dataset.value;
        if (activeFilters[filterType] && activeFilters[filterType].includes(value)) {
            chip.classList.add('active');
        }
    });
}

// Apply sort UI state from loaded data
function applySortUIState() {
    if (sortConfig.field) {
        const th = document.querySelector(`th[data-sort="${sortConfig.field}"]`);
        if (th) {
            th.classList.add(`sort-${sortConfig.direction}`);
        }
    }
}

// Toast notification system
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Loading indicator helpers
function showLoading(button) {
    if (!button) return;
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.textContent = '⏳ Processing...';
}

function hideLoading(button) {
    if (!button) return;
    button.disabled = false;
    button.textContent = button.dataset.originalText;
}

// Загрузка всех jobs
async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        allJobs = await response.json();
        applyFiltersAndSort();
    } catch (error) {
        console.error('Error loading jobs:', error);
        showToast('❌ Error loading jobs', 'error');
    }
}

// Apply filters and sorting
function applyFiltersAndSort() {
    let filtered = filterJobs(allJobs);
    let sorted = sortJobs(filtered);
    renderJobs(sorted);
    updateJobCount(filtered.length, allJobs.length);
}

// Обновление счётчика jobs
function updateJobCount(filtered, total) {
    const countEl = document.getElementById('jobCount');
    if (filtered === total) {
        countEl.textContent = total;
    } else {
        countEl.textContent = `${filtered} / ${total}`;
    }
}

// Filter jobs based on active filters
function filterJobs(jobs) {
    console.log('Filtering', jobs.length, 'jobs with filters:', activeFilters);
    
    const filtered = jobs.filter(job => {
        // Filter by status
        if (activeFilters.status.length > 0) {
            if (!activeFilters.status.includes(job.status)) {
                console.log(`Job "${job.title}" filtered out by status: ${job.status} not in`, activeFilters.status);
                return false;
            }
        }
        
        // Filter by visa
        if (activeFilters.visa.length > 0) {
            const visaValue = String(job.has_visa_sponsorship);
            if (!activeFilters.visa.includes(visaValue)) {
                console.log(`Job "${job.title}" filtered out by visa: ${visaValue} not in`, activeFilters.visa);
                return false;
            }
        }
        
        // Filter by match percentage
        if (activeFilters.match.length > 0) {
            const matchPct = job.resume_match_percentage || 0;
            let matchesFilter = false;
            
            for (const threshold of activeFilters.match) {
                const thresholdNum = parseInt(threshold);
                if (thresholdNum === 0) {
                    // <40%
                    if (matchPct < 40) matchesFilter = true;
                } else if (matchPct >= thresholdNum) {
                    matchesFilter = true;
                }
            }
            
            if (!matchesFilter) {
                console.log(`Job "${job.title}" filtered out by match: ${matchPct}% doesn't match thresholds`, activeFilters.match);
                return false;
            }
        }
        
        return true;
    });
    
    console.log('Filtered result:', filtered.length, 'jobs remaining');
    return filtered;
}

// Sort jobs based on sort config
function sortJobs(jobs) {
    if (!sortConfig.field) return jobs;
    
    const sorted = [...jobs].sort((a, b) => {
        let aVal, bVal;
        
        switch (sortConfig.field) {
            case 'title':
            case 'company':
                aVal = (a[sortConfig.field] || '').toLowerCase();
                bVal = (b[sortConfig.field] || '').toLowerCase();
                break;
            
            case 'visa':
                // Yes > N/A > No
                const visaOrder = { 'true': 3, 'null': 2, 'false': 1 };
                aVal = visaOrder[String(a.has_visa_sponsorship)] || 0;
                bVal = visaOrder[String(b.has_visa_sponsorship)] || 0;
                break;
            
            case 'match':
                aVal = a.resume_match_percentage || 0;
                bVal = b.resume_match_percentage || 0;
                break;
            
            case 'status':
                // New → Applied → Interview → Offer/Rejected
                const statusOrder = { 'new': 1, 'applied': 2, 'interview': 3, 'offer': 4, 'rejected': 5 };
                aVal = statusOrder[a.status] || 0;
                bVal = statusOrder[b.status] || 0;
                break;
            
            case 'applied_date':
            case 'response_date':
                aVal = a[sortConfig.field] ? new Date(a[sortConfig.field]).getTime() : 0;
                bVal = b[sortConfig.field] ? new Date(b[sortConfig.field]).getTime() : 0;
                break;
            
            case 'days':
                aVal = a.days_to_response || 0;
                bVal = b.days_to_response || 0;
                break;
            
            default:
                return 0;
        }
        
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
    });
    
    return sorted;
}

// Отрисовка jobs в таблице
function renderJobs(jobs) {
    const tbody = document.getElementById('jobsTableBody');
    
    console.log('Rendering jobs:', jobs.length, 'filtered from', allJobs.length, 'total');
    console.log('Active filters:', activeFilters);
    console.log('Sort config:', sortConfig);
    
    if (jobs.length === 0) {
        // Показываем разное сообщение в зависимости от того, есть ли фильтры
        const hasFilters = activeFilters.status.length > 0 || 
                          activeFilters.visa.length > 0 || 
                          activeFilters.match.length > 0;
        
        const message = hasFilters 
            ? 'No jobs match current filters. Try adjusting your filters.'
            : 'No jobs yet. Add your first job above!';
        
        tbody.innerHTML = `<tr><td colspan="9" class="empty-state">${message}</td></tr>`;
        return;
    }
    
    tbody.innerHTML = jobs.map(job => `
        <tr>
            <td><strong>${escapeHtml(job.title)}</strong></td>
            <td>${escapeHtml(job.company)}</td>
            <td>
                ${job.has_visa_sponsorship === true 
                    ? '<div class="tooltip-wrapper"><span class="badge badge-yes">✓ Yes</span><span class="tooltip-text">' + escapeHtmlKeepNewlines(job.sponsorship_analysis || 'Visa sponsorship available') + '</span></div>'
                    : job.has_visa_sponsorship === false 
                    ? '<div class="tooltip-wrapper"><span class="badge badge-no">✗ No</span><span class="tooltip-text">' + escapeHtmlKeepNewlines(job.sponsorship_analysis || 'No visa sponsorship') + '</span></div>'
                    : '<div class="tooltip-wrapper"><span class="badge badge-na">N/A</span><span class="tooltip-text">' + escapeHtmlKeepNewlines(job.sponsorship_analysis || 'No information about visa sponsorship in job description') + '</span></div>'}
            </td>
            <td>
                ${job.resume_match_percentage !== null
                    ? '<div class="tooltip-wrapper"><span class="match-badge match-' + getMatchClass(job.resume_match_percentage) + '">' + job.resume_match_percentage + '%</span><span class="tooltip-text">' + escapeHtmlKeepNewlines(job.match_analysis || 'Resume match analysis') + '</span></div>'
                    : '<span class="badge badge-na">N/A</span>'}
            </td>
            <td>
                <select onchange="updateStatus(${job.id}, this.value)" class="status-${job.status}">
                    <option value="new" ${job.status === 'new' ? 'selected' : ''}>New</option>
                    <option value="applied" ${job.status === 'applied' ? 'selected' : ''}>Applied</option>
                    <option value="interview" ${job.status === 'interview' ? 'selected' : ''}>Interview</option>
                    <option value="offer" ${job.status === 'offer' ? 'selected' : ''}>Offer</option>
                    <option value="rejected" ${job.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                </select>
            </td>
            <td>${job.applied_date ? formatDate(job.applied_date) : '-'}</td>
            <td>${job.response_date ? formatDate(job.response_date) : '-'}</td>
            <td>${job.days_to_response !== null ? job.days_to_response + ' days' : '-'}</td>
            <td>
                <button onclick="generateCoverLetter(${job.id}, this)" class="btn-generate">Cover Letter</button>
                <button onclick="deleteJob(${job.id})" class="btn-delete">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

// Экранирование HTML для безопасности, сохраняя переносы строк
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Для tooltip текста - сохраняем переносы строк
function escapeHtmlKeepNewlines(text) {
    if (!text) return '';
    // Экранируем HTML, затем конвертируем переносы в <br>
    const div = document.createElement('div');
    div.textContent = text;
    // Заменяем двойные переносы на параграфы, одинарные на <br>
    return div.innerHTML
        .replace(/\n\n+/g, '<br><br>')  // двойные переносы → двойной <br>
        .replace(/\n/g, '<br>');          // одинарные → один <br>
}

// Создание нового job
document.getElementById('jobForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const description = document.getElementById('description').value;
    const title = document.getElementById('title').value;
    const company = document.getElementById('company').value;
    
    // Проверяем что есть хотя бы description
    if (!description && (!title || !company)) {
        showToast('❌ Please provide at least a job description', 'error');
        return;
    }
    
    showLoading(submitBtn);
    
    const job = {
        title: title || "",
        company: company || "",
        job_url: document.getElementById('jobUrl').value,
        job_description: description,
        status: 'new'
    };
    
    try {
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(job)
        });
        
        if (response.ok) {
            showToast('✅ Job added and analyzed!', 'success');
            e.target.reset();
            loadJobs();
        } else {
            const error = await response.json();
            showToast('❌ Error: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error creating job:', error);
        showToast('❌ Network error. Please try again.', 'error');
    } finally {
        hideLoading(submitBtn);
    }
});

// Обновление статуса job
async function updateStatus(jobId, status) {
    try {
        const response = await fetch(`/api/jobs/${jobId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status})
        });
        
        if (response.ok) {
            showToast('✅ Status updated', 'success');
            loadJobs();
        } else {
            showToast('❌ Error updating status', 'error');
        }
    } catch (error) {
        console.error('Error updating status:', error);
        showToast('❌ Error updating status', 'error');
    }
}

// Удаление job
async function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/jobs/${jobId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('✅ Job deleted', 'success');
            loadJobs();
        } else {
            showToast('❌ Error deleting job', 'error');
        }
    } catch (error) {
        console.error('Error deleting job:', error);
        showToast('❌ Error deleting job', 'error');
    }
}

// Функция для определения класса match badge
function getMatchClass(percentage) {
    if (percentage >= 70) return 'high';
    if (percentage >= 40) return 'medium';
    return 'low';
}

// Генерация cover letter
async function generateCoverLetter(jobId, button) {
    showLoading(button);
    try {
        const response = await fetch(`/api/generate-cover-letter/${jobId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const job = await response.json();
            showToast('✅ Cover letter generated!', 'success');
            showCoverLetterModal(job.cover_letter);
            loadJobs();
        } else {
            const error = await response.json();
            showToast('❌ Error: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error generating cover letter:', error);
        showToast('❌ Network error. Please try again.', 'error');
    } finally {
        hideLoading(button);
    }
}

// Показать модальное окно с cover letter
function showCoverLetterModal(coverLetter) {
    document.getElementById('coverLetterText').value = coverLetter;
    document.getElementById('coverLetterModal').style.display = 'block';
}

// Закрыть модальное окно
function closeCoverLetterModal() {
    document.getElementById('coverLetterModal').style.display = 'none';
}

// Копировать cover letter в буфер обмена
function copyCoverLetter() {
    const text = document.getElementById('coverLetterText');
    text.select();
    document.execCommand('copy');
    showToast('✅ Cover letter copied to clipboard!', 'success');
}

// Закрыть модальное окно при клике вне его
window.onclick = function(event) {
    const modal = document.getElementById('coverLetterModal');
    if (event.target == modal) {
        closeCoverLetterModal();
    }
}

// Динамическое позиционирование tooltips
document.addEventListener('mouseover', function(e) {
    const tooltipWrapper = e.target.closest('.tooltip-wrapper');
    if (tooltipWrapper) {
        const tooltip = tooltipWrapper.querySelector('.tooltip-text');
        if (tooltip) {
            const rect = tooltipWrapper.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) + 'px';
            tooltip.style.top = (rect.top - 10) + 'px';
            tooltip.style.transform = 'translate(-50%, -100%)';
        }
    }
});

// Handle filter chip clicks
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('chip')) {
        const filterType = e.target.dataset.filter;
        const value = e.target.dataset.value;
        
        console.log('Chip clicked:', filterType, '=', value);
        
        // Toggle chip active state
        e.target.classList.toggle('active');
        
        const isActive = e.target.classList.contains('active');
        console.log('Chip is now:', isActive ? 'active' : 'inactive');
        
        // Update activeFilters
        if (isActive) {
            if (!activeFilters[filterType].includes(value)) {
                activeFilters[filterType].push(value);
            }
        } else {
            activeFilters[filterType] = activeFilters[filterType].filter(v => v !== value);
        }
        
        console.log('Updated filters:', activeFilters);
        
        // Save and apply
        saveFiltersToStorage();
        applyFiltersAndSort();
    }
});

// Handle sortable header clicks
document.addEventListener('click', function(e) {
    const th = e.target.closest('th.sortable');
    if (th) {
        const field = th.dataset.sort;
        
        // Remove sort classes from all headers
        document.querySelectorAll('th.sortable').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Toggle sort direction
        if (sortConfig.field === field) {
            sortConfig.direction = sortConfig.direction === 'asc' ? 'desc' : 'asc';
        } else {
            sortConfig.field = field;
            sortConfig.direction = 'asc';
        }
        
        // Add sort class to clicked header
        th.classList.add(`sort-${sortConfig.direction}`);
        
        // Save and apply
        saveFiltersToStorage();
        applyFiltersAndSort();
    }
});

// Reset all filters
function resetFilters() {
    // Clear filter state
    activeFilters = {
        status: [],
        visa: [],
        match: []
    };
    sortConfig = {
        field: null,
        direction: 'asc'
    };
    
    // Clear UI
    document.querySelectorAll('.chip').forEach(chip => {
        chip.classList.remove('active');
    });
    document.querySelectorAll('th.sortable').forEach(header => {
        header.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Save and apply
    saveFiltersToStorage();
    applyFiltersAndSort();
    showToast('✅ Filters reset', 'info');
}

// Загрузка jobs и фильтров при старте страницы
console.log('=== Job Search Helper - Filters & Sorting Loaded ===');
console.log('Initial state:', { activeFilters, sortConfig });
loadFiltersFromStorage();
console.log('After loading from storage:', { activeFilters, sortConfig });
loadJobs();


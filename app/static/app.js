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
        const jobs = await response.json();
        renderJobs(jobs);
        updateJobCount(jobs.length);
    } catch (error) {
        console.error('Error loading jobs:', error);
        showToast('❌ Error loading jobs', 'error');
    }
}

// Обновление счётчика jobs
function updateJobCount(count) {
    document.getElementById('jobCount').textContent = count;
}

// Отрисовка jobs в таблице
function renderJobs(jobs) {
    const tbody = document.getElementById('jobsTableBody');
    
    if (jobs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No jobs yet. Add your first job above!</td></tr>';
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

// Загрузка jobs при старте страницы
loadJobs();


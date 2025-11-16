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
                    ? '<span class="badge badge-yes">✓ Visa</span>' 
                    : job.has_visa_sponsorship === false 
                    ? '<span class="badge badge-no">✗ No Visa</span>' 
                    : '<button onclick="checkSponsorship(' + job.id + ', this)" class="btn-check">Check Visa</button>'}
            </td>
            <td>
                ${job.resume_match_percentage !== null
                    ? '<span class="match-badge match-' + getMatchClass(job.resume_match_percentage) + '">' + job.resume_match_percentage + '%</span>'
                    : '<button onclick="analyzeMatch(' + job.id + ', this)" class="btn-check">Analyze Match</button>'}
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

// Экранирование HTML для безопасности
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Создание нового job
document.getElementById('jobForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const description = document.getElementById('description').value;
    let title = document.getElementById('title').value;
    let company = document.getElementById('company').value;
    
    showLoading(submitBtn);
    
    // Если нет title/company, но есть description - извлекаем через LLM
    if (description && (!title || !company)) {
        try {
            const extractResponse = await fetch('/api/extract-job-info', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({job_description: description})
            });
            
            if (extractResponse.ok) {
                const extracted = await extractResponse.json();
                if (!title) title = extracted.title;
                if (!company) company = extracted.company;
                showToast('✨ Job info extracted automatically', 'info');
            }
        } catch (error) {
            console.error('Error extracting job info:', error);
            showToast('⚠️ Auto-extraction failed, please fill manually', 'error');
        }
    }
    
    // Проверяем что есть минимум title и company
    if (!title || !company) {
        showToast('❌ Title and Company are required', 'error');
        hideLoading(submitBtn);
        return;
    }
    
    const job = {
        title: title,
        company: company,
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
            showToast('✅ Job added successfully!', 'success');
            e.target.reset();
            loadJobs();
        } else {
            showToast('❌ Error creating job', 'error');
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

// Проверка visa sponsorship
async function checkSponsorship(jobId, button) {
    showLoading(button);
    try {
        const response = await fetch(`/api/analyze-sponsorship/${jobId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('✅ Visa sponsorship analyzed!', 'success');
            loadJobs();
        } else {
            const error = await response.json();
            showToast('❌ Error: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error checking sponsorship:', error);
        showToast('❌ Network error. Please try again.', 'error');
    } finally {
        hideLoading(button);
    }
}

// Анализ соответствия резюме
async function analyzeMatch(jobId, button) {
    showLoading(button);
    try {
        const response = await fetch(`/api/analyze-match/${jobId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const job = await response.json();
            showToast(`✅ Resume match: ${job.resume_match_percentage}%`, 'success');
            loadJobs();
        } else {
            const error = await response.json();
            showToast('❌ Error: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error analyzing match:', error);
        showToast('❌ Network error. Please try again.', 'error');
    } finally {
        hideLoading(button);
    }
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

// Загрузка jobs при старте страницы
loadJobs();


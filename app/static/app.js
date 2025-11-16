// Загрузка всех jobs
async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        const jobs = await response.json();
        renderJobs(jobs);
        updateJobCount(jobs.length);
    } catch (error) {
        console.error('Error loading jobs:', error);
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
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No jobs yet. Add your first job above!</td></tr>';
        return;
    }
    
    tbody.innerHTML = jobs.map(job => `
        <tr>
            <td><strong>${escapeHtml(job.title)}</strong></td>
            <td>${escapeHtml(job.company)}</td>
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
    
    const job = {
        title: document.getElementById('title').value,
        company: document.getElementById('company').value,
        job_url: document.getElementById('jobUrl').value,
        job_description: document.getElementById('description').value,
        status: 'new'
    };
    
    try {
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(job)
        });
        
        if (response.ok) {
            e.target.reset();
            loadJobs();
        } else {
            alert('Error creating job');
        }
    } catch (error) {
        console.error('Error creating job:', error);
        alert('Error creating job');
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
            loadJobs();
        } else {
            alert('Error updating status');
        }
    } catch (error) {
        console.error('Error updating status:', error);
        alert('Error updating status');
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
            loadJobs();
        } else {
            alert('Error deleting job');
        }
    } catch (error) {
        console.error('Error deleting job:', error);
        alert('Error deleting job');
    }
}

// Загрузка jobs при старте страницы
loadJobs();


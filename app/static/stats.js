// Load LLM statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        // Overall statistics
        document.getElementById('totalCalls').textContent = data.total_calls;
        document.getElementById('successfulCalls').textContent = data.successful_calls;
        document.getElementById('totalTokens').textContent = data.total_tokens.toLocaleString();
        document.getElementById('estimatedCost').textContent = '$' + data.estimated_cost.toFixed(2);

        // Breakdown by function
        const tbody = document.getElementById('functionStatsBody');
        tbody.innerHTML = '';
        
        if (data.by_function.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">No data yet. Make some LLM calls first!</td></tr>';
            return;
        }

        data.by_function.forEach(func => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${func.function_name}</strong></td>
                <td>${func.call_count}</td>
                <td>${func.tokens_used.toLocaleString()}</td>
                <td>${func.avg_execution_time}s</td>
                <td>$${func.estimated_cost.toFixed(4)}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading stats:', error);
        alert('Error loading statistics');
    }
}

// Load on page open
loadStats();


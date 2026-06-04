// Physics Pipeline Dashboard JavaScript

const API_BASE = '';

// Fetch and display status
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();

        const statusClass = `status-${data.status}`;
        const statusEmoji = {
            'blocked': '🔴',
            'ready': '🟡',
            'complete': '✅'
        }[data.status] || '⚪';

        document.getElementById('status-content').innerHTML = `
            <div class="status-badge ${statusClass}">
                ${statusEmoji} ${data.status.toUpperCase()}
            </div>
            <div class="status-message">${data.message}</div>
            <div class="status-details">
                <div class="status-detail">
                    <div class="status-detail-label">Data Available</div>
                    <div class="status-detail-value">${data.data_available ? '✅' : '❌'}</div>
                </div>
                <div class="status-detail">
                    <div class="status-detail-label">Total Runs</div>
                    <div class="status-detail-value">${data.run_count}</div>
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('status-content').innerHTML = `
            <div class="error-state">Error loading status: ${error.message}</div>
        `;
    }
}

// Fetch and display recent runs
async function loadRuns() {
    try {
        const response = await fetch(`${API_BASE}/api/runs`);
        const data = await response.json();

        if (data.runs.length === 0) {
            document.getElementById('runs-content').innerHTML = `
                <div class="empty-state">No runs available yet</div>
            `;
            return;
        }

        const runsHtml = data.runs.map(run => {
            const modelsHtml = run.models.slice(0, 4).map(m =>
                `<span class="model-badge">${m.model} (χ²/ndf: ${m.chi2_ndf.toFixed(2)})</span>`
            ).join('');

            const bestModel = run.best_model ?
                `<div class="run-best">🏆 Best: ${run.best_model}</div>` : '';

            return `
                <div class="run-item">
                    <div class="run-header">
                        <div class="run-name">${run.name}</div>
                        <div class="run-date">${new Date(run.date).toLocaleDateString()}</div>
                    </div>
                    <div class="run-models">${modelsHtml}</div>
                    ${bestModel}
                </div>
            `;
        }).join('');

        document.getElementById('runs-content').innerHTML = runsHtml;
    } catch (error) {
        document.getElementById('runs-content').innerHTML = `
            <div class="error-state">Error loading runs: ${error.message}</div>
        `;
    }
}

// Fetch and display agenda
async function loadAgenda() {
    try {
        const response = await fetch(`${API_BASE}/api/agenda`);
        const data = await response.json();

        if (data.agenda.length === 0) {
            document.getElementById('agenda-content').innerHTML = `
                <div class="empty-state">No actions defined</div>
            `;
            return;
        }

        const agendaHtml = data.agenda.map(item => {
            const statusClass = `agenda-${item.status}`;
            const checkbox = item.status === 'completed' ? '✅' : '⬜';
            const idBadge = item.id ? `<span class="agenda-id">[${item.id}]</span> ` : '';

            return `
                <div class="agenda-item ${statusClass}">
                    <div class="agenda-checkbox">${checkbox}</div>
                    <div class="agenda-text">${idBadge}${item.text}</div>
                </div>
            `;
        }).join('');

        document.getElementById('agenda-content').innerHTML = agendaHtml;
    } catch (error) {
        document.getElementById('agenda-content').innerHTML = `
            <div class="error-state">Error loading agenda: ${error.message}</div>
        `;
    }
}

// Fetch and display evidence
async function loadEvidence() {
    try {
        const response = await fetch(`${API_BASE}/api/evidence`);
        const data = await response.json();

        const summaryHtml = `
            <div class="evidence-summary">
                <div class="evidence-stat">
                    <div class="evidence-stat-value evidence-verified">${data.verified}</div>
                    <div class="evidence-stat-label">Verified</div>
                </div>
                <div class="evidence-stat">
                    <div class="evidence-stat-value evidence-pending">${data.pending}</div>
                    <div class="evidence-stat-label">Pending</div>
                </div>
                <div class="evidence-stat">
                    <div class="evidence-stat-value evidence-blocked">${data.blocked}</div>
                    <div class="evidence-stat-label">Blocked</div>
                </div>
            </div>
        `;

        if (data.claims.length === 0) {
            document.getElementById('evidence-content').innerHTML = summaryHtml + `
                <div class="empty-state">No claims tracked yet</div>
            `;
            return;
        }

        const claimsHtml = data.claims.map(claim => {
            const statusEmoji = {
                'verified': '✅',
                'pending': '🟡',
                'blocked': '🔴'
            }[claim.status] || '⚪';

            return `
                <div class="claim-item">
                    <div class="claim-text">${claim.text}</div>
                    <div class="claim-status evidence-${claim.status}">
                        ${statusEmoji} ${claim.status.toUpperCase()}
                    </div>
                </div>
            `;
        }).join('');

        document.getElementById('evidence-content').innerHTML = summaryHtml + claimsHtml;
    } catch (error) {
        document.getElementById('evidence-content').innerHTML = `
            <div class="error-state">Error loading evidence: ${error.message}</div>
        `;
    }
}

// Fetch and display models
async function loadModels() {
    try {
        const response = await fetch(`${API_BASE}/api/models`);
        const data = await response.json();

        const modelsHtml = data.models.map(model => `
            <div class="model-item">
                <div class="model-name">${model.name}</div>
                <div class="model-type">${model.type}</div>
                <div class="model-params">Parameters: ${model.parameters.join(', ')}</div>
                <div class="model-status">${model.status}</div>
            </div>
        `).join('');

        document.getElementById('models-content').innerHTML = modelsHtml;
    } catch (error) {
        document.getElementById('models-content').innerHTML = `
            <div class="error-state">Error loading models: ${error.message}</div>
        `;
    }
}

// Refresh all data
function refreshAll() {
    loadStatus();
    loadRuns();
    loadAgenda();
    loadEvidence();
    loadModels();
    updateTimestamp();
}

// Update timestamp
function updateTimestamp() {
    const now = new Date().toLocaleString();
    document.getElementById('last-updated').textContent = now;
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    refreshAll();

    // Auto-refresh every 30 seconds
    setInterval(refreshAll, 30000);
});

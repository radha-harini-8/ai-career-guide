document.addEventListener('DOMContentLoaded', function () {
    const navToggle = document.getElementById('nav-toggle');
    const nav = document.getElementById('main-nav');

    if (navToggle && nav) {
        navToggle.addEventListener('click', function () {
            nav.classList.toggle('open');
        });
    }
});

function showLoading(elementId, message = 'Analyzing your information...') {
    const loader = document.getElementById(elementId);
    if (!loader) return;
    loader.querySelector('p').textContent = message;
    loader.classList.remove('hidden');
}

function hideLoading(elementId) {
    const loader = document.getElementById(elementId);
    if (!loader) return;
    loader.classList.add('hidden');
}

function showError(elementId, message) {
    const target = document.getElementById(elementId);
    if (!target) return;
    target.classList.remove('hidden');
    target.innerHTML = `<div class="error-box">${message}</div>`;
}

function showSuccess(elementId, message) {
    const target = document.getElementById(elementId);
    if (!target) return;
    target.classList.remove('hidden');
    target.innerHTML = `<div class="success-box">${message}</div>`;
}

function renderResults(elementId, html) {
    const container = document.getElementById(elementId);
    if (!container) return;
    container.classList.remove('hidden');
    container.innerHTML = html;
}

function formatPercentage(value) {
    if (typeof value === 'number') {
        return `${Math.round(value)}%`;
    }
    return value || 'N/A';
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

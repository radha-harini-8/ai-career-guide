document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('career-form');
    if (!form) return;

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        showLoading('career-loader', 'Building your personalized roadmap...');
        const resultBox = document.getElementById('career-result');
        resultBox.classList.add('hidden');

        try {
            const response = await fetch('/api/career-plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await response.json();

            if (!response.ok || !json.success) {
                throw new Error(json.error || 'Unable to generate your career plan.');
            }

            const { user_id, plan } = json.data;
            localStorage.setItem('careerGuideUserId', user_id);
            renderCareerPlan(plan, user_id);
        } catch (error) {
            hideLoading('career-loader');
            showError('career-result', error.message || 'Something went wrong while generating your plan.');
        }
    });
});

function renderCareerPlan(plan, userId) {
    const resultBox = document.getElementById('career-result');
    if (!resultBox) return;

    const summary = plan.summary || 'Your roadmap is ready.';
    const readiness = plan.readiness_estimate || { score: 76, explanation: 'AI-generated estimate' };
    const currentSkills = (plan.current_skills || []).join(', ') || 'Not provided';
    const requiredSkills = (plan.required_skills || []).join(', ') || 'Not provided';
    const skillGaps = (plan.skill_gaps || []).join(', ') || 'No large gaps detected';
    const days = plan.days || [];
    const projects = plan.projects || [];
    const certifications = plan.certifications || [];
    const interviewTopics = plan.interview_topics || [];

    const html = `
        <div class="result-section">
            <h3>Career Readiness Summary</h3>
            <p>${escapeHtml(summary)}</p>
            <div class="metric-grid">
                <div class="metric-box">
                    <span>Career Readiness</span>
                    <strong>${escapeHtml(readiness.score || 76)}/100</strong>
                </div>
                <div class="metric-box">
                    <span>Current Skills</span>
                    <strong>${escapeHtml(currentSkills)}</strong>
                </div>
                <div class="metric-box">
                    <span>Required Skills</span>
                    <strong>${escapeHtml(requiredSkills)}</strong>
                </div>
                <div class="metric-box">
                    <span>Skill Gaps</span>
                    <strong>${escapeHtml(skillGaps)}</strong>
                </div>
            </div>
            <p><strong>Estimate note:</strong> This score is an AI-generated estimate based on the information provided and should be used as guidance.</p>
        </div>

        <div class="list-card">
            <h4>Skill Gap Analysis</h4>
            <ul>
                ${(plan.skill_gaps || []).map((skill) => `<li>${escapeHtml(skill)}</li>`).join('') || '<li>No major gaps detected.</li>'}
            </ul>
        </div>

        <div class="list-card">
            <h4>30-Day Learning Plan</h4>
            <div class="day-list">
                ${days.slice(0, 12).map((day) => `
                    <div class="day-pill ${day.day % 2 === 0 ? 'done' : 'in-progress'}">
                        Day ${day.day}<br>${escapeHtml(day.topic || 'Practice')}
                    </div>
                `).join('')}
            </div>
            <ul>
                ${days.map((day) => `
                    <li><strong>Day ${day.day}: </strong>${escapeHtml(day.topic)} — ${escapeHtml((day.tasks || []).join(', '))}</li>
                `).join('')}
            </ul>
        </div>

        <div class="list-card">
            <h4>Projects</h4>
            <ul>
                ${projects.map((project) => `<li><strong>${escapeHtml(project.title || 'Project')}</strong> — ${escapeHtml(project.description || '')}</li>`).join('')}
            </ul>
        </div>

        <div class="list-card">
            <h4>Certification Suggestions</h4>
            <ul>
                ${certifications.map((cert) => `<li><strong>${escapeHtml(cert.name || 'Certification')}</strong> — ${escapeHtml(cert.provider || '')}</li>`).join('')}
            </ul>
        </div>

        <div class="list-card">
            <h4>Interview Preparation Topics</h4>
            <ul>
                ${interviewTopics.map((topic) => `<li>${escapeHtml(topic)}</li>`).join('')}
            </ul>
        </div>

        <div class="quick-actions">
            <a class="btn btn-primary" href="/dashboard?user_id=${encodeURIComponent(userId)}">View Dashboard</a>
            <a class="btn btn-secondary" href="/report?user_id=${encodeURIComponent(userId)}">View Report</a>
        </div>
    `;

    renderResults('career-result', html);
    resultBox.classList.remove('hidden');
    hideLoading('career-loader');
}

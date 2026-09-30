document.addEventListener('DOMContentLoaded', async function () {
    const dashboardNode = document.getElementById('dashboard-content');
    const reportNode = document.getElementById('report-content');
    const userId = getUserId();

    if (dashboardNode) {
        try {
            const response = await fetch(`/api/dashboard/${encodeURIComponent(userId)}`);
            const json = await response.json();
            if (!json.success) throw new Error(json.error || 'Unable to load dashboard data.');
            renderDashboard(json.data.dashboard || {});
        } catch (error) {
            dashboardNode.innerHTML = `<div class="result-panel"><p>${escapeHtml(error.message || 'Unable to load dashboard.')}</p></div>`;
        }
    }

    if (reportNode) {
        try {
            const response = await fetch(`/api/report/${encodeURIComponent(userId)}`);
            const json = await response.json();
            if (!json.success) throw new Error(json.error || 'Unable to load report data.');
            renderReport(json.data.report || {});
        } catch (error) {
            reportNode.innerHTML = `<div class="result-panel"><p>${escapeHtml(error.message || 'Unable to load report.')}</p></div>`;
        }
    }

    const downloadButton = document.getElementById('download-report');
    if (downloadButton) {
        downloadButton.addEventListener('click', function () {
            const node = document.getElementById('report-content');
            if (!node) return;
            const printWindow = window.open('', '_blank');
            printWindow.document.write(node.innerHTML);
            printWindow.document.close();
            printWindow.focus();
            printWindow.print();
        });
    }
});

function getUserId() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('user_id')) return params.get('user_id');
    return localStorage.getItem('careerGuideUserId') || 'demo_user';
}

function renderDashboard(data) {
    const userName = data.user?.name || 'Student';
    const targetRole = data.target_role || 'Data Analyst';
    const readiness = data.career_readiness || 76;
    const atsEstimate = data.resume_ats_estimate || 82;
    const skillMatch = data.skill_match || '8/11';
    const learningProgress = data.learning_progress || 0;
    const skillGap = data.skill_gap || 3;
    const plan = data.plan || {};
    const days = plan.days || [];
    const completedDays = Array.isArray(days) ? days.filter((day) => day.day <= Math.round((learningProgress / 100) * 30)).map((day) => day.day) : [];

    const dashboardHtml = `
        <section class="dashboard-header">
            <div>
                <span class="eyebrow">Welcome back</span>
                <h2>Welcome, ${escapeHtml(userName)} 👋</h2>
            </div>
            <div class="quick-actions">
                <a href="/career-guide" class="btn btn-primary">Create Career Plan</a>
                <a href="/resume-analyzer" class="btn btn-secondary">Analyze Resume</a>
                <a href="/job-analyzer" class="btn btn-secondary">Analyze Job</a>
            </div>
        </section>

        <section class="inline-metric">
            <div class="metric-box">
                <span>Target Role</span>
                <strong>${escapeHtml(targetRole)}</strong>
            </div>
            <div class="metric-box">
                <span>Career Readiness</span>
                <strong>${escapeHtml(readiness)}/100</strong>
            </div>
            <div class="metric-box">
                <span>Resume ATS Estimate</span>
                <strong>${escapeHtml(atsEstimate)}%</strong>
            </div>
            <div class="metric-box">
                <span>Skill Match</span>
                <strong>${escapeHtml(skillMatch)}</strong>
            </div>
        </section>

        <section class="content-card">
            <div class="section-heading">
                <span class="eyebrow">Learning Progress</span>
                <h3>Skill Gap & Progress</h3>
            </div>
            <div class="progress-wrap">
                <div class="progress-bar"><span class="progress-fill" style="width: ${Math.min(100, Number(learningProgress || 0))}%"></span></div>
                <p>Learning Progress: ${escapeHtml(learningProgress)}%</p>
            </div>
            <p>Skill Gap: ${escapeHtml(skillGap)} major areas identified.</p>
        </section>

        <section class="content-card">
            <div class="section-heading">
                <span class="eyebrow">30-Day Plan</span>
                <h3>Progress Tracking</h3>
            </div>
            <div class="day-list">
                ${(days.slice(0, 12)).map((day) => {
                    const isDone = Number(day.day) <= Number(completedDays.length || 0);
                    const label = isDone ? 'done' : 'in-progress';
                    return `<div class="day-pill ${label}">Day ${day.day}</div>`;
                }).join('') || '<div class="day-pill in-progress">No plan yet</div>'}
            </div>
        </section>

        <section class="content-card">
            <div class="section-heading">
                <span class="eyebrow">Quick Actions</span>
                <h3>Continue your journey</h3>
            </div>
            <div class="quick-actions">
                <a href="/resume-analyzer" class="btn btn-primary">Analyze Resume</a>
                <a href="/job-analyzer" class="btn btn-secondary">Analyze Job</a>
                <a href="/interview-prep" class="btn btn-secondary">Practice Interview</a>
                <a href="/report?user_id=${encodeURIComponent(getUserId())}" class="btn btn-secondary">View Report</a>
            </div>
        </section>
    `;

    const node = document.getElementById('dashboard-content');
    if (node) node.innerHTML = dashboardHtml;
}

function renderReport(data) {
    const user = data.user || {};
    const plan = data.career_plan || {};
    const readiness = data.career_readiness_estimate || 76;
    const resumeAnalysis = data.resume_analysis || {};
    const techTopics = (plan.interview_topics || []).slice(0, 4).join(', ') || 'Not available';
    const skills = (plan.required_skills || []).join(', ') || 'Not available';
    const gaps = (plan.skill_gaps || []).join(', ') || 'No major gaps detected';

    const html = `
        <h3>User Information</h3>
        <p><strong>Name:</strong> ${escapeHtml(user.name || 'Student')}</p>
        <p><strong>Target Role:</strong> ${escapeHtml(plan.target_role || 'Data Analyst')}</p>

        <div class="metric-grid">
            <div class="metric-box"><span>Career Readiness</span><strong>${escapeHtml(readiness)}/100</strong></div>
            <div class="metric-box"><span>Existing Skills</span><strong>${escapeHtml((plan.current_skills || []).join(', ') || 'Not provided')}</strong></div>
            <div class="metric-box"><span>Required Skills</span><strong>${escapeHtml(skills)}</strong></div>
            <div class="metric-box"><span>Skill Gaps</span><strong>${escapeHtml(gaps)}</strong></div>
        </div>

        <div class="list-card">
            <h4>Resume Analysis</h4>
            <p>${escapeHtml(resumeAnalysis.summary || 'Resume analysis summary is not available.')}</p>
        </div>

        <div class="list-card">
            <h4>30-Day Plan</h4>
            <ul>
                ${(plan.days || []).slice(0, 5).map((day) => `<li><strong>Day ${day.day}:</strong> ${escapeHtml(day.topic || '')}</li>`).join('')}
            </ul>
        </div>

        <div class="list-card">
            <h4>Recommended Projects</h4>
            <ul>
                ${(plan.projects || []).slice(0, 3).map((item) => `<li>${escapeHtml(item.title || 'Project')}</li>`).join('')}
            </ul>
        </div>

        <div class="list-card">
            <h4>Interview Preparation Topics</h4>
            <p>${escapeHtml(techTopics)}</p>
        </div>
    `;

    const node = document.getElementById('report-content');
    if (node) node.innerHTML = html;
}

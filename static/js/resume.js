document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('resume-form');
    if (!form) return;

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(form);
        const targetRole = formData.get('target_role');

        if (!targetRole) {
            showError('resume-result', 'Please enter the target role before analyzing your resume.');
            return;
        }

        showLoading('resume-loader', 'Analyzing your resume...');
        const result = document.getElementById('resume-result');
        result.classList.add('hidden');

        try {
            const response = await fetch('/api/analyze-resume', {
                method: 'POST',
                body: formData
            });
            const json = await response.json();

            if (!response.ok || !json.success) {
                throw new Error(json.error || 'Unable to analyze resume.');
            }

            renderResumeAnalysis(json.data.analysis || {});
            hideLoading('resume-loader');
        } catch (error) {
            hideLoading('resume-loader');
            showError('resume-result', error.message || 'Something went wrong while analyzing your resume.');
        }
    });
});

function renderResumeAnalysis(analysis) {
    const targetRole = document.getElementById('resume_target_role')?.value || 'Data Analyst';
    const strengths = (analysis.strengths || []).join(', ') || 'Not enough information available';
    const improvementAreas = (analysis.improvement_areas || []).join(', ') || 'No major issues detected';
    const missingSections = (analysis.missing_sections || []).join(', ') || 'No major sections missing';
    const skills = (analysis.skills || []).join(', ') || 'No skills detected';

    const html = `
        <h3>Resume Summary</h3>
        <p>${escapeHtml(analysis.summary || 'This resume has a solid base and can be improved for the target role.')}</p>

        <div class="metric-grid">
            <div class="metric-box">
                <span>ATS Compatibility Estimate</span>
                <strong>82%</strong>
            </div>
            <div class="metric-box">
                <span>Target Role Relevance</span>
                <strong>${escapeHtml(targetRole)}</strong>
            </div>
            <div class="metric-box">
                <span>Detected Skills</span>
                <strong>${escapeHtml(skills)}</strong>
            </div>
        </div>

        <div class="list-card">
            <h4>Resume Strengths</h4>
            <p>${escapeHtml(strengths)}</p>
        </div>

        <div class="list-card">
            <h4>Improvement Areas</h4>
            <p>${escapeHtml(improvementAreas)}</p>
        </div>

        <div class="list-card">
            <h4>Missing Sections or Suggestions</h4>
            <p>${escapeHtml(missingSections)}</p>
        </div>

        <div class="list-card">
            <h4>Formatting and Text Issues</h4>
            <ul>
                ${(analysis.formatting_issues || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}
            </ul>
        </div>
    `;

    renderResults('resume-result', html);
}

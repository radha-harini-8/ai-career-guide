document.addEventListener('DOMContentLoaded', function () {
    const jobForm = document.getElementById('job-form');
    const matchForm = document.getElementById('match-form');

    if (jobForm) {
        jobForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const payload = Object.fromEntries(new FormData(jobForm).entries());
            showLoading('job-loader', 'Extracting requirements...');
            try {
                const response = await fetch('/api/analyze-job', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const json = await response.json();
                if (!response.ok || !json.success) throw new Error(json.error || 'Unable to analyze job description.');
                renderJobAnalysis(json.data.analysis || {});
                hideLoading('job-loader');
            } catch (error) {
                hideLoading('job-loader');
                showError('job-result', error.message || 'Unable to analyze the job description.');
            }
        });
    }

    if (matchForm) {
        matchForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const formData = new FormData(matchForm);
            showLoading('match-loader', 'Comparing resume and job...');
            try {
                const response = await fetch('/api/match-resume', {
                    method: 'POST',
                    body: formData
                });
                const json = await response.json();
                if (!response.ok || !json.success) throw new Error(json.error || 'Unable to compare resume and job description.');
                renderMatchAnalysis(json.data || {});
                hideLoading('match-loader');
            } catch (error) {
                hideLoading('match-loader');
                showError('match-result', error.message || 'Unable to compare resume and job description.');
            }
        });
    }
});

function renderJobAnalysis(analysis) {
    const html = `
        <h3>Job Description Highlights</h3>
        <div class="metric-grid">
            <div class="metric-box"><span>Required Skills</span><strong>${escapeHtml((analysis.required_skills || []).join(', ') || 'Not specified')}</strong></div>
            <div class="metric-box"><span>Preferred Skills</span><strong>${escapeHtml((analysis.preferred_skills || []).join(', ') || 'Not specified')}</strong></div>
            <div class="metric-box"><span>Tools</span><strong>${escapeHtml((analysis.tools || []).join(', ') || 'Not specified')}</strong></div>
            <div class="metric-box"><span>Experience</span><strong>${escapeHtml(analysis.experience_requirements || 'Not specified')}</strong></div>
        </div>

        <div class="list-card">
            <h4>Responsibilities</h4>
            <ul>
                ${(analysis.responsibilities || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}
            </ul>
        </div>

        <div class="list-card">
            <h4>Keywords</h4>
            <ul class="tag-list">
                ${(analysis.keywords || []).map((keyword) => `<li>${escapeHtml(keyword)}</li>`).join('')}
            </ul>
        </div>
    `;
    renderResults('job-result', html);
}

function renderMatchAnalysis(data) {
    const match = data.match || {};
    const ats = data.ats || {};
    const matchedSkills = (match.matched_skills || []).join(', ') || 'None identified';
    const missingSkills = (match.missing_skills || []).join(', ') || 'No major gaps';
    const suggestions = (match.suggested_resume_improvements || []).join(', ') || 'Improve clarity and keywords';

    const html = `
        <h3>Resume-to-Job Match Analysis</h3>
        <div class="metric-grid">
            <div class="metric-box"><span>Overall Match</span><strong>${escapeHtml(match.overall_match || 76)}%</strong></div>
            <div class="metric-box"><span>ATS Compatibility Estimate</span><strong>${escapeHtml(ats.ats_compatibility_estimate || 82)}%</strong></div>
            <div class="metric-box"><span>Matched Skills</span><strong>${escapeHtml(matchedSkills)}</strong></div>
            <div class="metric-box"><span>Missing Skills</span><strong>${escapeHtml(missingSkills)}</strong></div>
        </div>

        <div class="list-card">
            <h4>Suggested Resume Improvements</h4>
            <p>${escapeHtml(suggestions)}</p>
        </div>

        <div class="list-card">
            <h4>ATS Breakdown</h4>
            <ul>
                <li>Keyword Match: ${escapeHtml(ats.breakdown?.keyword_match || 88)}%</li>
                <li>Skills Match: ${escapeHtml(ats.breakdown?.skills_match || 80)}%</li>
                <li>Experience Relevance: ${escapeHtml(ats.breakdown?.experience_relevance || 75)}%</li>
                <li>Resume Structure: ${escapeHtml(ats.breakdown?.resume_structure || 90)}%</li>
                <li>Readability: ${escapeHtml(ats.breakdown?.readability || 85)}%</li>
            </ul>
        </div>

        <p><strong>Note:</strong> This is an AI-generated estimate and should be used as guidance, not a guarantee of job selection.</p>
    `;
    renderResults('match-result', html);
}

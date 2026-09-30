document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('interview-form');
    if (!form) return;

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        const payload = Object.fromEntries(new FormData(form).entries());
        showLoading('interview-loader', 'Preparing interview questions...');

        try {
            const response = await fetch('/api/interview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await response.json();
            if (!response.ok || !json.success) throw new Error(json.error || 'Unable to generate interview questions.');

            renderInterviewQuestions(json.data.questions || {});
            hideLoading('interview-loader');
        } catch (error) {
            hideLoading('interview-loader');
            showError('interview-result', error.message || 'Unable to prepare interview content.');
        }
    });
});

function renderInterviewQuestions(questions) {
    const sections = [
        { title: 'Technical Questions', items: questions.technical_questions || [] },
        { title: 'HR Questions', items: questions.hr_questions || [] },
        { title: 'Behavioral Questions', items: questions.behavioral_questions || [] },
        { title: 'Resume-based Questions', items: questions.resume_based_questions || [] },
        { title: 'Scenario-based Questions', items: questions.scenario_based_questions || [] }
    ];

    const html = sections.map((section) => {
        const list = section.items.map((item) => `
            <li>
                <strong>${escapeHtml(item.question || 'Question')}</strong><br>
                <small>Difficulty: ${escapeHtml(item.difficulty || 'Medium')} | Topic: ${escapeHtml(item.topic || 'General')}</small>
                <p>${escapeHtml(item.answer_guidance || 'Prepare a structured answer using examples and clear reasoning.')}</p>
            </li>
        `).join('') || '<li>No questions generated for this section.</li>';

        return `
            <div class="list-card">
                <h4>${escapeHtml(section.title)}</h4>
                <ul>${list}</ul>
            </div>
        `;
    }).join('');

    renderResults('interview-result', html);
}

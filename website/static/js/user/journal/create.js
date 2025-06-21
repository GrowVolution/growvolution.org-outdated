import { closeModal } from "/static/js/shared/modal_control.js";
const modalId = 'createJournalModal';
const createJournalToggle = document.getElementById('journalCreationToggle');

const steps = document.querySelectorAll('.journal-step');
let currentStep = 0;

const backBtn = document.getElementById('journalBackBtn');
const nextBtn = document.getElementById('journalNextBtn');
const finishBtn = document.getElementById('journalFinishBtn');
const questionsContainer = document.getElementById('journalQuestions');
const addBtn = document.getElementById('addJournalQuestion');

function updateButtons() {
    backBtn.disabled = currentStep === 0;
    nextBtn.classList.toggle('d-none', currentStep === steps.length - 1);
    finishBtn.classList.toggle('d-none', currentStep !== steps.length - 1);
}

function goToStep(step) {
    steps[currentStep].classList.add('d-none');
    currentStep = step;
    steps[currentStep].classList.remove('d-none');
    updateButtons();
}

backBtn.onclick = () => goToStep(currentStep - 1);
nextBtn.onclick = () => goToStep(currentStep + 1);

addBtn.onclick = () => {
    const count = questionsContainer.querySelectorAll('.journal-question').length + 1;
    const div = document.createElement('div');
    div.className = 'journal-question mb-4';
    div.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <strong>Frage ${count}</strong>
        <i class="bi bi-trash text-danger cursor-pointer delete-question"></i>
      </div>
      <input type="text" class="form-control mb-2 question-input" maxlength="50" placeholder="Welche Frage möchtest du dir stellen?">
      <select class="form-select">
        <option value="text" selected>Text</option>
        <option value="checkbox">Checkbox</option>
      </select>
    `;
    questionsContainer.appendChild(div);
    updateSaveButton();
};

questionsContainer.addEventListener('click', (e) => {
    if (!e.target.classList.contains('delete-question')) return;
    const question = e.target.closest('.journal-question');
    question.remove();
    Array.from(questionsContainer.children).forEach((el, i) => {
        const title = el.querySelector('strong');
        if (title) title.textContent = `Frage ${i + 1}`;
    });
    updateSaveButton();
});

function updateSaveButton() {
    const allFilled = Array.from(document.querySelectorAll('.question-input')).every(inp => inp.value.trim().length > 0);
    finishBtn.disabled = !allFilled;
}

questionsContainer.addEventListener('input', updateSaveButton);

finishBtn.onclick = async () => {
    const data = Array.from(questionsContainer.children).map(q => {
        return {
            question: q.querySelector('input').value.trim(),
            type: q.querySelector('select').value
        };
    });

    const res = await fetch('/journal/set', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ questions: JSON.stringify(data) })
    });

    if (res.ok) {
        closeModal(modalId);

        createJournalToggle.classList.remove('d-none');
        createJournalToggle.role = "link";
        createJournalToggle.href = "/journal";
        createJournalToggle.dataset.bsToggle = null;
        createJournalToggle.dataset.bsTarget = null;
        createJournalToggle.textContent = "Mein Tagebuch";
    }
};
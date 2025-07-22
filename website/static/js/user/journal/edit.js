import { closeModal } from "/static/js/shared/modal_control.js";
const modalId = 'editJournalModal';

const form = document.getElementById('editJournalForm');
const container = document.getElementById('editJournalQuestions');
const addBtn = document.getElementById('editAddQuestion');
const saveBtn = document.getElementById('editJournalSave') || document.querySelector('button[type="submit"][form="editJournalForm"]');

// Ensure all inputs have the correct class for event handling
container.querySelectorAll('input[type="text"]').forEach(inp => inp.classList.add('question-input'));

function getCurrentState() {
    return Array.from(container.querySelectorAll('.journal-question')).map(q => ({
        question: q.querySelector('input')?.value.trim() || '',
        type: q.querySelector('select')?.value || 'text'
    }));
}

let initialState = JSON.stringify(getCurrentState());

function updateSaveBtn() {
    const state = getCurrentState();
    const hasEmpty = state.some(q => q.question.length === 0);
    const unchanged = JSON.stringify(state) === initialState;
    saveBtn.disabled = hasEmpty || unchanged;
}

updateSaveBtn();

container.addEventListener('input', updateSaveBtn);
container.addEventListener('change', updateSaveBtn);

addBtn.addEventListener('click', () => {
    const count = container.querySelectorAll('.journal-question').length + 1;
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
    container.appendChild(div);
    updateSaveBtn();
});

container.addEventListener('click', e => {
    if (!e.target.classList.contains('delete-question')) return;
    const box = e.target.closest('.journal-question');
    if (box) box.remove();
    Array.from(container.querySelectorAll('.journal-question')).forEach((el, i) => {
        const label = el.querySelector('strong');
        if (label) label.textContent = `Frage ${i + 1}`;
    });
    updateSaveBtn();
});

form.addEventListener('submit', async e => {
    e.preventDefault();
    const data = getCurrentState();
    const res = await fetch('/journal/set', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ questions: data })
    });
    if (res.ok) {
        initialState = JSON.stringify(data);
        closeModal(modalId);
    }
});
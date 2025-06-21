import { addTaskToDOM } from './add_task.js';

const weekModeSelect = document.getElementById('weekMode');
const submitBtn = document.getElementById('submitWeekBtn');

const dayCodes = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'];

socket.on('load_weekplan', ({ mode, week }) => {
    if (!mode || !week) return;

    weekModeSelect.value = mode;
    weekModeSelect.dispatchEvent(new Event('change'));

    const allFreeTasks = {};

    dayCodes.forEach(day => {
        const group = document.querySelector(`.day-group[data-day-index="${dayCodes.indexOf(day)}"]`);
        const toggle = group.querySelector('.rest-day-toggle');

        const value = week[day];
        if (value === 'restday') {
            toggle.checked = true;
            toggle.dispatchEvent(new Event('change'));
            return;
        }

        if (!value) return;

        if (mode === 'simple') {
            const select = group.querySelector('.task-select');
            if (!select) return;
            if ([...select.options].some(opt => opt.value === value)) {
                select.value = value;
            } else {
                select.value = 'custom';
                const input = group.querySelector('.custom-input');
                if (input) {
                    input.classList.remove('d-none');
                    input.value = value;
                }
            }
        } else if (mode === 'medium') {
            const selects = group.querySelectorAll('.multi-task-select');
            const list = Array.isArray(value) ? value : [];
            selects.forEach((sel, i) => {
                const val = list[i];
                if (!val) return;
                if ([...sel.options].some(opt => opt.value === val)) {
                    sel.value = val;
                } else {
                    sel.value = 'custom';
                    const input = sel.parentElement.querySelector('.custom-input');
                    if (input) {
                        input.classList.remove('d-none');
                        input.value = val;
                    }
                }
            });
        } else if (mode === 'free') {
            const list = Array.isArray(value) ? value : [];
            allFreeTasks[day] = {};
            list.forEach((task, index) => {
                const taskId = `${day}-${index}`;
                allFreeTasks[day][taskId] = task;
                addTaskToDOM(day, taskId, task);
            });
        }
    });

    if (mode === 'free') {
        localStorage.setItem('weeklyPlanTasks', JSON.stringify(allFreeTasks));
    }

    submitBtn.disabled = false;
});

emit('request_weekplan');

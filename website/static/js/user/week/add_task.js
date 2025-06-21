let currentTaskDayCode = null;
let editingTaskId = null;
let editingTaskDays = [];
const localTasksKey = 'weeklyPlanTasks';
const newTaskForm = document.getElementById('newTaskForm');
const addTaskBtn = document.getElementById('addNewTaskBtn');
const dayCheckboxex = document.querySelectorAll('#taskWeekdaysWrapper input[type="checkbox"]');
const weekdayMap = { mo: 1, di: 2, mi: 3, do: 4, fr: 5, sa: 6, so: 0 };
const freqMap = {
    weekly: 'wöchentlich',
    biweekly: 'alle 2 Wochen',
    triweekly: 'alle 3 Wochen',
    fourweekly: 'alle 4 Wochen'
};

document.getElementById('multiWeekSwitch').addEventListener('change', e => {
    const wrapper = document.getElementById('taskWeekdaysWrapper');
    const isMulti = e.target.checked;
    wrapper.classList.toggle('d-none', !isMulti);

    if (!isMulti) {
        dayCheckboxex.forEach(
            cb => cb.checked = cb.value === currentTaskDayCode
        );
    }

    updateTaskStartDate();
});

function getSelectedDays() {
    const codes = [];
    dayCheckboxex.forEach(cb => {
        if (cb.checked) codes.push(cb.value);
    });
    return codes;
}

function updateDaycodes() {
    updateTaskStartDate(getSelectedDays());
}

dayCheckboxex.forEach(cb => {
    cb.addEventListener('change', updateDaycodes);
});

function updateTaskStartDate(dayCodes = [currentTaskDayCode]) {
    const startInput = document.getElementById('taskStartDate');
    const validDates = getNextDatesForWeekdays(dayCodes);

    startInput.value = validDates[0];
    startInput.min = validDates[0];
    startInput.max = validDates.at(-1);
    startInput.setAttribute('data-valid-dates', JSON.stringify(validDates));
}

document.getElementById('taskStartDate').addEventListener('input', e => {
    const allowedDates = JSON.parse(e.target.getAttribute('data-valid-dates') || '[]');
    if (!allowedDates.includes(e.target.value)) {
        e.target.value = allowedDates[0];
        showInfo("Ungültige Auswahl", "Das gewählte Startdatum passt nicht zu den ausgewählten Wochentagen.");
    }
});

function getNextDatesForWeekdays(dayCodes, count = 10) {
    const weekdays = dayCodes.map(code => (weekdayMap[code] + 1));
    const today = new Date();
    const dates = [];

    for (let i = 0; i < count * weekdays.length; i++) {
        const d = new Date(today);
        d.setDate(d.getDate() + i);
        if (weekdays.includes((d.getDay() || 7))) {
            dates.push(d.toISOString().split("T")[0]);
        }
    }

    return dates.slice(0, count);
}

function prepareNewTaskModal(dayCode) {
    currentTaskDayCode = dayCode;
    const wrapper = document.getElementById('taskWeekdaysWrapper');
    const weekdayCheckboxes = wrapper.querySelectorAll('input[type="checkbox"]');
    const multiSwitch = document.getElementById('multiWeekSwitch');

    multiSwitch.checked = false;
    wrapper.classList.add('d-none');

    weekdayCheckboxes.forEach(cb => {
        cb.checked = cb.value === dayCode;
    });

    updateTaskStartDate([dayCode]);
}

document.querySelectorAll('.add-task-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const group = btn.closest('.day-group');
        currentTaskDayCode = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'][group.dataset.dayIndex];
        prepareNewTaskModal(currentTaskDayCode);
    });
});


function makeSafeId(timeStr) {
    return `task_${timeStr.replace(/[^0-9]/g, '_')}`;
}

function addTaskBtnHandler() {
    const data = Object.fromEntries(new FormData(newTaskForm));
    const selectedDays = getSelectedDays();
    const multi = document.getElementById('multiWeekSwitch').checked;
    const frequency = data.frequency;
    const timeId = makeSafeId(data.time_from);

    const days = multi ? selectedDays : [currentTaskDayCode];
    const startDay = (new Date(data.start_date)).getDay();
    const startDayCode = ['so', 'mo', 'di', 'mi', 'do', 'fr', 'sa'][startDay];

    const allTasks = JSON.parse(localStorage.getItem(localTasksKey) || '{}');

    if (editingTaskId && editingTaskDays.length) {
        editingTaskDays.forEach(d => {
            if (allTasks[d]?.[editingTaskId]) {
                delete allTasks[d][editingTaskId];
                const el = document.getElementById(editingTaskId);
                if (el) el.remove();
            }
        });
    }

    days.forEach(day => {
        const entry = {
            ...data,
            multi: multi ? '1' : '',
            weekdays: selectedDays,
            frequency,
            start_day: startDayCode
        };

        if (!allTasks[day]) allTasks[day] = {};
        allTasks[day][timeId] = entry;
        addTaskToDOM(day, timeId, entry, day === startDayCode);
    });

    localStorage.setItem(localTasksKey, JSON.stringify(allTasks));

    bootstrap.Modal.getInstance(document.getElementById('newTaskModal')).hide();
    newTaskForm.reset();

    const actionBtn = document.getElementById('addNewTaskBtn');
    actionBtn.textContent = 'Hinzufügen';
    actionBtn.classList.remove('btn-success');
    actionBtn.classList.add('btn-primary');
    editingTaskId = null;
    editingTaskDays = [];
}

addTaskBtn.addEventListener('click', addTaskBtnHandler);

function sortTaskContainer(container) {
    const tasks = [...container.children];
    tasks.sort((a, b) => {
        const ta = a.id.split('_').slice(1).join(':');
        const tb = b.id.split('_').slice(1).join(':');
        return ta.localeCompare(tb);
    });
    tasks.forEach(el => container.appendChild(el));
}

export function addTaskToDOM(dayCode, id, data, isStartDay) {
    const container = document.getElementById(`tasks-${dayCode}`);
    const existing = container.querySelector(`#${id}`);
    if (existing) existing.remove();

    const wrapper = document.createElement('div');
    wrapper.id = id;
    wrapper.className = 'task-preview border rounded p-2 mb-2 bg-light';

    const formattedDate = new Date(data.start_date).toLocaleDateString('de-DE');
    const label = data.title + (isStartDay ? ` <span class="fw-normal text-muted">(Start: ${formattedDate})</span>` : '');
    const freqLabel = freqMap[data.frequency] || '';


    wrapper.innerHTML = `
    <div class="d-flex justify-content-between align-items-center">
      <div>
        <div class="fw-bold">${label}</div>
        <div class="text-muted small">${data.time_from} – ${data.time_to} ${freqLabel ? `(${freqLabel})` : ''}</div>
        ${data.notes ? `<div class="small">${data.notes}</div>` : ''}
      </div>
      <button type="button" class="btn btn-sm btn-outline-primary edit-task" data-day="${dayCode}" data-id="${id}">Bearbeiten</button>
    </div>
  `;

    container.appendChild(wrapper);
    sortTaskContainer(container);
}

document.addEventListener('click', e => {
    if (!e.target.matches('.edit-task')) return;

    const btn = e.target;
    const day = btn.dataset.day;
    const id = btn.dataset.id;

    const allTasks = JSON.parse(localStorage.getItem(localTasksKey) || '{}');
    const task = allTasks?.[day]?.[id];
    if (!task) return;

    currentTaskDayCode = day;
    editingTaskId = id;
    editingTaskDays = Object.keys(allTasks).filter(k => allTasks[k]?.[id]);

    Object.entries(task).forEach(([k, v]) => {
        const input = newTaskForm.querySelector(`[name="${k}"]`);
        if (!input) return;

        if (input.type === 'checkbox' && input.name === 'weekdays') {
            dayCheckboxex.forEach(cb => cb.checked = task.weekdays?.includes(cb.value));
        } else {
            input.value = v;
        }
    });
    updateTaskStartDate(task.weekdays?.length ? task.weekdays : [day]);

    document.getElementById('multiWeekSwitch').checked = !!task.multi;
    document.getElementById('taskWeekdaysWrapper').classList.toggle('d-none', !task.multi);

    const validDates = getNextDatesForWeekdays(task.weekdays || [day]);
    const startInput = document.getElementById('taskStartDate');
    startInput.setAttribute('data-valid-dates', JSON.stringify(validDates));
    startInput.min = validDates[0];
    startInput.max = validDates.at(-1);

    const actionBtn = document.getElementById('addNewTaskBtn');
    actionBtn.textContent = 'Speichern';
    actionBtn.classList.remove('btn-primary');
    actionBtn.classList.add('btn-success');

    bootstrap.Modal.getOrCreateInstance(document.getElementById('newTaskModal')).show();
});

function updateFreeModeRestdays() {
    document.querySelectorAll('.day-group').forEach((group, index) => {
        const dayCode = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'][index];
        const toggle = group.querySelector('.rest-day-toggle');
        const cb = document.querySelector(`input[name="weekdays"][value="${dayCode}"]`);

        if (document.getElementById('weekMode').value !== 'free') return;

        const isRestday = toggle.checked;

        if (cb) {
            cb.disabled = isRestday;
            if (isRestday) cb.checked = false;
        }

        if (isRestday) {
            const container = document.getElementById(`tasks-${dayCode}`);
            const allTasks = JSON.parse(localStorage.getItem(localTasksKey) || '{}');

            container.innerHTML = '';

            if (allTasks[dayCode]) {
                delete allTasks[dayCode];

                for (const [otherDay, tasks] of Object.entries(allTasks)) {
                    if (otherDay === dayCode) continue;

                    for (const [taskId, task] of Object.entries(tasks)) {
                        if (Array.isArray(task.weekdays) && task.weekdays.includes(dayCode)) {
                            task.weekdays = task.weekdays.filter(dc => dc !== dayCode);
                        }
                    }
                }

                localStorage.setItem(localTasksKey, JSON.stringify(allTasks));
            }
        }
    });
}

document.querySelectorAll('.rest-day-toggle').forEach(toggle => {
    toggle.addEventListener('change', updateFreeModeRestdays);
});

updateFreeModeRestdays();

document.getElementById('taskTimeFrom').addEventListener('change', e => {
    const start = e.target.value;
    if (!start) return;

    const [h, m] = start.split(':').map(Number);
    const startDate = new Date();
    startDate.setHours(h, m + 30, 0); // +30 Minuten

    const hh = String(startDate.getHours()).padStart(2, '0');
    const mm = String(startDate.getMinutes()).padStart(2, '0');

    const timeTo = document.getElementById('taskTimeTo');
    if (!timeTo.value) timeTo.value = `${hh}:${mm}`;
});

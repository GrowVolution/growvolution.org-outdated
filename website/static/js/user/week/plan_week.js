const weekMode = document.getElementById('weekMode');
const dayGroups = document.querySelectorAll('.day-group');
const submitBtn = document.getElementById('submitWeekBtn');
const planForm = document.getElementById('planWeekForm');

let restDays = 0;

weekMode.addEventListener('change', () => {
  const mode = weekMode.value;
  restDays = 0;

  dayGroups.forEach(group => {
    const toggle = group.querySelector('.rest-day-toggle');
    toggle.checked = false;

    group.querySelectorAll('.task-block').forEach(el => el.classList.add('d-none'));
    const modeBlock = group.querySelector(`.mode-${mode}`);
    if (modeBlock) modeBlock.classList.remove('d-none');
  });

  validateForm();
});


dayGroups.forEach(group => {
  const toggle = group.querySelector('.rest-day-toggle');

  toggle.addEventListener('change', () => {
    const mode = weekMode.value;
    const dayCode = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'][group.dataset.dayIndex];
    const blocks = group.querySelectorAll('.task-block');

    if (toggle.checked) {
      if (restDays >= 2) {
        toggle.checked = false;
        flash('Du kannst maximal zwei Ruhetage festlegen.', 'warning');
        return;
      }
      restDays++;
      blocks.forEach(block => block.classList.add('d-none'));

      if (mode === 'simple') {
        const select = group.querySelector('.task-select');
        if (select) {
          select.value = '';
          const input = group.querySelector('.custom-input');
          if (input) input.classList.add('d-none');
        }
      } else if (mode === 'medium') {
        group.querySelectorAll('.multi-task-select').forEach(sel => {
          sel.value = '';
          const input = sel.parentElement.querySelector('.custom-input');
          if (input) input.classList.add('d-none');
        });
      } else if (mode === 'free') {
        const container = document.getElementById(`tasks-${dayCode}`);
        if (container) container.innerHTML = '';
        const all = JSON.parse(localStorage.getItem('weeklyPlanTasks') || '{}');
        if (all[dayCode]) {
          delete all[dayCode];
          localStorage.setItem('weeklyPlanTasks', JSON.stringify(all));
        }
      }
    } else {
      restDays--;
      const activeBlock = group.querySelector(`.mode-${mode}`);
      if (activeBlock) activeBlock.classList.remove('d-none');
    }

    validateForm();
  });
});

document.querySelectorAll('.task-select, .multi-task-select').forEach((select, idx) => {
  select.addEventListener('change', () => {
    const input = select.parentElement.querySelector('.custom-input');
    input?.classList.toggle('d-none', select.value !== 'custom');
    validateForm();
  });
});

function validateForm() {
  const mode = weekMode.value;
  let valid = false;

  if (mode === 'simple') {
    valid = [...document.querySelectorAll('.task-select')]
        .some(select => select.value !== '');
  } else if (mode === 'medium') {
    valid = [...document.querySelectorAll('.multi-task-select')]
        .some(select => select.value !== '');
  } else {
    const allTasks = JSON.parse(localStorage.getItem('weeklyPlanTasks') || '{}');
    const taskCount = Object.values(allTasks)
        .reduce((sum, tasks) => sum + Object.keys(tasks).length, 0);
    valid = taskCount >= 2;
  }

  submitBtn.disabled = !valid;
}


planForm.addEventListener('submit', async e => {
  e.preventDefault();

  const formData = new FormData();
  const mode = weekMode.value;
  const allFreeTasks = JSON.parse(localStorage.getItem('weeklyPlanTasks') || '{}');

  formData.set('mode', mode);

  dayGroups.forEach((group, i) => {
    const dayCode = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'][i];
    const isRest = group.querySelector('.rest-day-toggle').checked;

    if (isRest) {
      formData.set(dayCode, 'restday');
      return;
    }

    if (mode === 'simple') {
      const sel = group.querySelector('.task-select');
      let val = sel.value;
      if (val === 'custom') {
        val = sel.parentElement.querySelector('.custom-input').value.trim();
      }
      formData.set(dayCode, val || '');
    } else if (mode === 'medium') {
      const selects = group.querySelectorAll('.multi-task-select');
      const tasks = [];
      selects.forEach(sel => {
        let val = sel.value;
        if (val === 'custom') {
          val = sel.parentElement.querySelector('.custom-input').value.trim();
        }
        if (val) tasks.push(val);
      });

      const compacted = tasks.filter(Boolean);
      formData.set(dayCode, compacted.length ? JSON.stringify(compacted) : '');
    } else if (mode === 'free') {
      const rawTasks = allFreeTasks?.[dayCode];
      if (!rawTasks || Object.keys(rawTasks).length === 0) {
        formData.set(dayCode, '');
        return;
      }

      const formatted = Object.entries(rawTasks).map(([id, task]) => {
        const base = {
          time_from: task.time_from,
          time_to: task.time_to,
          title: task.title,
          notes: task.notes || '',
          frequency: task.frequency || 'weekly',
          start_date: task.start_date,
        };

        if (task.multi === '1') {
          base.multi = true;
          base.weekdays = Array.isArray(task.weekdays) ? task.weekdays : [];
        }

        return base;
      });

      formData.set(dayCode, JSON.stringify(formatted));
    }
  });

  const setupMode = location.href.endsWith('week/');
  let route = '/week/setup';
  if(!setupMode) route = '/week/update';

  const res = await fetch(route, { method: 'POST', body: formData });
  if (res.ok) {
    if (setupMode) location.reload();
    else location.href = '/week';
  } else {
    flash('Fehler beim Speichern der Daten!', 'warning');
  }
});

function resetLocalTasks() {
  localStorage.removeItem('weeklyPlanTasks');
  ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'].forEach(dayCode => {
    const container = document.getElementById(`tasks-${dayCode}`);
    if (container) container.innerHTML = '';
  });
}


if (planForm.dataset.edit !== 'true')
  showInfo("Wie du deine Woche planst", null, `
  <p>
      Hey! Schön, dass du deine Woche planen möchtest. 🤩<br><br>
      Du kannst selbst entscheiden, wie ausführlich du diesen Schritt gestalten möchtest.
      Insgesamt hast du dazu 3 Auswahlmöglichkeiten:
  </p>
  <ol>
      <li>Ganz grob (<span class="text-success small">+25 XP</span>): Um für bestimmte Tage eine Tagesaufgabe festzulegen.</li>
      <li>Etwas erweitert (<span class="text-success small">+50 XP</span>): Um dir für jeden Tag bis zu 3 Aufgaben einzuteilen.</li>
      <li>Völlig frei (<span class="text-success small">+75 XP</span>): Um dir flexibel deine Woche einzuteilen, Intervalle / Häufigkeiten
       festzulegen und deinen eigenen Wochenkalender zu entwickeln.</li>
  </ol>
  <p>
      ⚠️ Denk aber daran, es geht hier nicht allein um Erfahrungspunkte!<br><br>
      Solltest du noch ganz am Anfang stehen, dann übertreibe es nicht gleich mit deiner Wochenplanung. Wenn du sie zu komplex
      gestaltest, wird es dir schwerfallen, dich an deinen Plan zu halten. Fang lieber klein an, du kannst deinen Plan später
      jederzeit ausbauen. 🔨<br><br>
      Außerdem empfehlen wir dir, dir einen festen Ruhetag einzuplanen. Gerade wenn du sehr ambitioniert bist, wirst du sehen, dass
      eine bewusste Entscheidung zum Faulenzen Wunder wirken kann. 💤
  </p>
  `);

resetLocalTasks();
import { closeModal } from '/static/js/shared/modal_control.js';

const input = document.getElementById('newUsername');
const hint = document.getElementById('usernameHint');
const saveBtn = document.getElementById('saveUsername');

if (input && hint && saveBtn && typeof emit !== 'undefined') {
  const original = input.value.trim();
  let timeout;

  input.addEventListener('input', () => {
    const val = input.value.trim();
    const changed = val !== original;

    saveBtn.disabled = !changed || !val;

    if (!val) {
      hint.classList.add('d-none');
      return;
    }

    clearTimeout(timeout);
    timeout = setTimeout(() => {
      emit('check_username', { value: val });
    }, 300);
  });

  saveBtn.addEventListener('click', () => {
    emit('update_username', { username: input.value.trim() });
  });

  socket.on('username_status', data => {
    hint.classList.remove('d-none');
    if (data.available) {
      hint.classList.remove('text-danger');
      hint.classList.add('text-success');
      hint.innerHTML = '<i class="bi bi-check-circle me-1"></i> Verfügbar';
    } else {
      hint.classList.remove('text-success');
      hint.classList.add('text-danger');
      hint.innerHTML = '<i class="bi bi-x-circle me-1"></i> Vergeben';
      saveBtn.disabled = true;
    }
  });

  socket.on('username_updated', res => {
    if (res.success) {
      closeModal('usernameEditModal');
      const display = document.getElementById('profileUsername');
      if (display) {
        display.textContent = `@${res.username}`;
      }
    } else {
      alert(res.error || 'Fehler beim Speichern');
    }
  });
}

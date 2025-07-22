import { validatePasswordStrength, validateMatch } from '/static/js/shared/hint_validation.js';
import { closeModal } from '/static/js/shared/modal_control.js';

const current = document.getElementById('currentPassword');
const fresh = document.getElementById('newPassword');
const repeat = document.getElementById('repeatPassword');
const saveBtn = document.getElementById('savePassword');
const hintNew = document.getElementById('passwordHint');
const hintRepeat = document.getElementById('repeatHint');
const rotateIcon = document.getElementById('passwordRotateIcon');

if (current && fresh && repeat && saveBtn) {
  const validate = () => {
    const strong = validatePasswordStrength(fresh, hintNew);
    const match = validateMatch(fresh, repeat, hintRepeat);
    saveBtn.disabled = !(current.value && fresh.value && repeat.value && strong && match);
  };

  current.addEventListener('input', validate);
  fresh.addEventListener('input', validate);
  repeat.addEventListener('input', validate);
}

saveBtn.addEventListener('click', () => {
  emit('change_password', {
    current: current.value,
    new: fresh.value
  });
});

socket.on('password_changed', res => {
  if (res.success) {
    closeModal('passwordChangeModal');
  } else {
    showInfo('Fehler beim Speichern', res.error);
  }
});

if (rotateIcon) {
  const modal = document.getElementById('passwordChangeModal');

  modal.addEventListener('show.bs.modal', () => {
    rotateIcon.style.transform = 'rotate(180deg)';
  });

  modal.addEventListener('hidden.bs.modal', () => {
    rotateIcon.style.transform = 'rotate(0deg)';
  });
}

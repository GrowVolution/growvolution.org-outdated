import { closeModal } from '/static/js/shared/modal_control.js';

const emailInput = document.getElementById('newEmail');
const saveEmailBtn = document.getElementById('saveEmail');
const changePendingInfo = document.getElementById('emailChangePending');

if (emailInput && saveEmailBtn) {
  const original = emailInput.value.trim();

  const validate = () => {
    const input = emailInput.value.trim();
    const changed = input !== original;
    saveEmailBtn.disabled = !changed;
  };

  emailInput.addEventListener('input', validate);
  validate();
}

saveEmailBtn.addEventListener('click', () => {
  emit('request_email_change', {
    email: emailInput.value.trim()
  });
});

socket.on('email_change_requested', res => {
  if (res.success) {
    closeModal('emailChangeModal');
    changePendingInfo.classList.remove('d-none');
    const display = document.getElementById('profileEmail');
    if (display) {
      display.textContent = res.email ? `${res.email} (ausstehend)` : 'Fehler';
    }
  } else {
    showInfo('Fehler beim Speichern', res.error);
  }
});

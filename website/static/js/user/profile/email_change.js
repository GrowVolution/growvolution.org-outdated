import { closeModal } from '/static/js/shared/modal_control.js';

const emailInput = document.getElementById('emailInput');
const saveEmailBtn = document.getElementById('saveEmail');
const emailBlockedBox = document.getElementById('emailSocialBlock');

if (emailInput && saveEmailBtn) {
  const original = emailInput.value;
  saveEmailBtn.disabled = true;

  emailInput.addEventListener('input', () => {
    const changed = emailInput.value.trim() !== original.trim();
    saveEmailBtn.disabled = !changed;
  });
}

if (emailBlockedBox) {
  saveEmailBtn.disabled = true;
  emailInput.disabled = true;
}

saveEmailBtn.addEventListener('click', () => {
  emit('request_email_change', {
    email: emailInput.value.trim()
  });
});

socket.on('email_change_requested', res => {
  if (res.success) {
    closeModal('emailChangeModal');
  } else {
    alert(res.error || 'Fehler beim Speichern');
  }
});

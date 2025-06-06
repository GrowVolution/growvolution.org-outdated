import { closeModal } from '/static/js/shared/modal_control.js';

const modal = document.getElementById('twoFAModal');
const qr = document.getElementById('twoFAQr');
const secretCode = document.querySelector('#twoFASecret code');
const tokenInput = document.getElementById('twoFAToken');
const completeBtn = document.getElementById('complete2FA');
const successSection = document.getElementById('twoFASuccessSection');
const setupSection = document.getElementById('twoFASetupSection');
const recoveryCodes = document.getElementById('recoveryCodes');
const closeBtn = document.getElementById('close2FAModal');
const actionButtons = document.getElementById('twoFAActionButtons');
const twoFAStatus = document.getElementById('twoFAStatus');
const twoFAControl = document.getElementById('twoFAControl');

let entry_code

const updateStatus = enabled => {
  if (!twoFAStatus) return;
  twoFAStatus.innerHTML = enabled
    ? '<i class="bi bi-check-circle text-success"></i>'
    : '<i class="bi bi-x-circle text-danger"></i>';
};

if (modal && completeBtn && qr && secretCode && twoFAControl) {
  twoFAControl.addEventListener('click', () => {
    const active = twoFAStatus.querySelector('.text-success');
    if (active) {
      if (confirm('Möchtest du die Zwei-Faktor-Authentifizierung wirklich deaktivieren?')) {
        emit('disable_2fa');
      }
    } else {
      bootstrap.Modal.getOrCreateInstance(modal).show();
    }
  });

  modal.addEventListener('shown.bs.modal', () => {
    if (modal.dataset.setupLoaded === 'true') return;

    fetch('/api/2fa-setup')
      .then(res => res.json())
      .then(data => {
        qr.src = data.qr;
        qr.classList.remove('d-none');
        secretCode.textContent = data.secret;
        secretCode.parentElement.classList.remove('d-none');
        setupSection.classList.remove('d-none');
        successSection.classList.add('d-none');
        completeBtn.disabled = true;
        tokenInput.value = '';
        recoveryCodes.innerHTML = '';
        closeBtn.classList.add('d-none');
        actionButtons.classList.remove('d-none');

        entry_code = data.code;
        modal.dataset.setupLoaded = 'true'
      });
  });

  tokenInput.addEventListener('input', () => {
    completeBtn.disabled = !/^\d{6}$/.test(tokenInput.value.trim());
  });

  completeBtn.addEventListener('click', () => {
    const code = tokenInput.value.trim();
    if (!/^\d{6}$/.test(code)) return;
    emit('confirm_2fa', { token: code, secret_entry: entry_code });
  });

  socket.on('2fa_confirmed', res => {
    if (!res.success) {
      alert("Fehler: Code ungültig oder abgelaufen.");
      return;
    }

    setupSection.classList.add('d-none');
    successSection.classList.remove('d-none');
    completeBtn.disabled = true;
    actionButtons.classList.add('d-none');
    closeBtn.classList.remove('d-none');

    recoveryCodes.innerHTML = '';
    res.recovery_codes.forEach(code => {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      li.textContent = code;
      recoveryCodes.appendChild(li);
    });

    updateStatus(true);
  });

  closeBtn.addEventListener('click', () => {
    closeModal(modal.id);
  })

  socket.on('2fa_disabled', res => {
    if (res.success) {
      updateStatus(false);
    } else {
      alert(res.error || 'Fehler beim Deaktivieren');
    }
  });
}

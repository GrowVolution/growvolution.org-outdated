import { closeModal } from '/static/js/shared/modal_control.js';

const birthdayUnsetCheckbox = document.getElementById('birthdayUnset');
const birthdayInput = document.getElementById('birthdayInput');
const saveBirthdayBtn = document.getElementById('saveBirthday');

if (birthdayUnsetCheckbox && birthdayInput && saveBirthdayBtn) {
  const toggleBirthdayField = () => {
    birthdayInput.disabled = birthdayUnsetCheckbox.checked;
    validateBirthday();
  };

  const validateBirthday = () => {
    const valid = birthdayInput.value;
    saveBirthdayBtn.disabled = birthdayUnsetCheckbox.checked || !valid;
  };

  birthdayUnsetCheckbox.addEventListener('change', toggleBirthdayField);
  birthdayInput.addEventListener('input', validateBirthday);

  toggleBirthdayField();
}

saveBirthdayBtn.addEventListener('click', () => {
  const birthday = birthdayUnsetCheckbox.checked ? null : birthdayInput.value;
  emit('update_birthday', { birthday });
});

socket.on('birthday_updated', res => {
  if (res.success) {
    closeModal('birthdayChangeModal');
  } else {
    alert(res.error || 'Fehler beim Speichern');
  }
});

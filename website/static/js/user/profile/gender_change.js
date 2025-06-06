import { closeModal } from '/static/js/shared/modal_control.js';

const genderSelect = document.getElementById('gender');
const saveGenderBtn = document.getElementById('saveGender');

if (genderSelect && saveGenderBtn) {
  const original = genderSelect.dataset.original;
  const validateGender = () => {
    saveGenderBtn.disabled = (genderSelect.value === original);
  };

  genderSelect.addEventListener('change', validateGender);
  validateGender();
}

saveGenderBtn.addEventListener('click', () => {
  emit('update_gender', {
    gender: genderSelect.value || null
  });
});

socket.on('gender_updated', res => {
  if (res.success) {
    closeModal('genderChangeModal');
  } else {
    alert(res.error || 'Fehler beim Speichern');
  }
});

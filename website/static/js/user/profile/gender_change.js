import { closeModal } from '/static/js/shared/modal_control.js';

const genderSelect = document.getElementById('gender');
const saveGenderBtn = document.getElementById('saveGender');
const profileGender = document.getElementById('profileGender');
const genderId = profileGender.querySelector('span');

if (genderSelect && saveGenderBtn) {
  const validateGender = () => {
    saveGenderBtn.disabled = (genderSelect.value === genderId.id);
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
    let genderText;
    switch (res.gender) {
      case 'm': {
        genderId.id = 'm';
        genderText = 'Männlich';
        break;
      }
      case 'w': {
        genderId.id = 'w';
        genderText = 'Weiblich';
        break;
      }
      case 'd': {
        genderId.id = 'd';
        genderText = 'Divers';
        break;
      }
      default:
        genderId.id = '';
        genderText = 'Keine Angabe';
    }
    profileGender.textContent = genderText;
    saveGenderBtn.disabled = true;
  } else {
    alert(res.error || 'Fehler beim Speichern');
  }
});

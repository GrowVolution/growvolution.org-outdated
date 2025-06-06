import { toggleInputs } from '/static/js/shared/input_toggle.js';
import { closeModal } from '/static/js/shared/modal_control.js';

const phoneUnsetCheckbox = document.getElementById('phoneUnset');
const phonePrefixSelect = document.getElementById('phonePrefix');
const phoneNumberInput = document.getElementById('phoneNumber');
const savePhoneBtn = document.getElementById('savePhone');

if (phoneUnsetCheckbox && phonePrefixSelect && phoneNumberInput && savePhoneBtn) {
  const validatePhoneInputs = () => {
    const valid = phonePrefixSelect.value && phoneNumberInput.value.trim();
    savePhoneBtn.disabled = phoneUnsetCheckbox.checked || !valid;
  };

  phoneUnsetCheckbox.addEventListener('change', () => {
    toggleInputs(phoneUnsetCheckbox.checked, phonePrefixSelect, phoneNumberInput);
    validatePhoneInputs();
  });

  phonePrefixSelect.addEventListener('input', validatePhoneInputs);
  phoneNumberInput.addEventListener('input', validatePhoneInputs);

  toggleInputs(phoneUnsetCheckbox.checked, phonePrefixSelect, phoneNumberInput);
  validatePhoneInputs();
}

savePhoneBtn.addEventListener('click', () => {
  const phone = phoneUnsetCheckbox.checked ? null : {
    prefix: phonePrefixSelect.value,
    number: phoneNumberInput.value.trim()
  };

  emit('update_phone', { phone });
});

socket.on('phone_updated', res => {
  if (res.success) {
    closeModal('phoneChangeModal');
  } else {
    alert(res.error || 'Fehler beim Speichern');
  }
});

import { toggleInputs } from '/static/js/shared/input_toggle.js';
import { closeModal } from '/static/js/shared/modal_control.js';

const addressUnsetCheckbox = document.getElementById('addressUnset');
const addressStreet = document.getElementById('addressStreet');
const addressNumber = document.getElementById('addressNumber');
const addressZip = document.getElementById('addressZip');
const addressCity = document.getElementById('addressCity');
const saveAddressBtn = document.getElementById('saveAddress');
const profileAddress = document.getElementById('profileAddress');

let addressGiven = profileAddress.textContent.trim() !== 'Keine Angabe';

if (addressUnsetCheckbox && addressStreet && addressZip && addressCity && saveAddressBtn) {
  const validateAddress = () => {
    const valid = addressStreet.value.trim() && addressNumber.value.trim() && addressZip.value.trim() && addressCity.value.trim();
    if (addressGiven)
      saveAddressBtn.disabled = !addressUnsetCheckbox.checked;
    else
      saveAddressBtn.disabled = addressUnsetCheckbox.checked || !valid;
  };

  addressUnsetCheckbox.addEventListener('change', () => {
    toggleInputs(addressUnsetCheckbox.checked, addressStreet, addressNumber, addressZip, addressCity);
    validateAddress();
  });

  addressStreet.addEventListener('input', validateAddress);
  addressNumber.addEventListener('input', validateAddress);
  addressZip.addEventListener('input', validateAddress);
  addressCity.addEventListener('input', validateAddress);

  toggleInputs(addressUnsetCheckbox.checked, addressStreet, addressNumber, addressZip, addressCity);
  validateAddress();

  saveAddressBtn.addEventListener('click', () => {
    const address = addressUnsetCheckbox.checked ? null : {
      street: addressStreet.value.trim(),
      number: addressNumber.value.trim(),
      postal: addressZip.value.trim(),
      city: addressCity.value.trim()
    };

    emit('update_address', { address });
  });

  socket.on('address_updated', res => {
    if (res.success) {
      closeModal('addressChangeModal');
      profileAddress.textContent = res.address ? res.address : 'Keine Angabe';
      addressGiven = !addressGiven;
      saveAddressBtn.disabled = true;
    } else {
      alert(res.error || 'Fehler beim Speichern');
    }
  });
}

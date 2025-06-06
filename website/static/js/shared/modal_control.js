export function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    const instance = bootstrap.Modal.getInstance(modal);
    if (instance) instance.hide();
  }
}

export function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    const instance = new bootstrap.Modal(modal);
    instance.show();
  }
}

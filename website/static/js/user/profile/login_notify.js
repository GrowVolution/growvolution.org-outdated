const notifyToggle = document.getElementById('loginNotifyToggle');
const notifyStatus = document.getElementById('loginNotifyStatus');

if (notifyToggle && notifyStatus) {
  notifyToggle.addEventListener('click', () => {
    const enabled = notifyStatus.querySelector('.text-success') !== null;
    emit('toggle_login_notify', { enable: !enabled });
  });

  socket.on('login_notify_updated', res => {
    if (!res || typeof res.enabled === 'undefined') return;

    notifyStatus.innerHTML = res.enabled
      ? '<i class="bi bi-check-circle text-success"></i>'
      : '<i class="bi bi-x-circle text-danger"></i>';
  });
}

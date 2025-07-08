const toggle = document.getElementById('hideLastNameToggle');
const status = document.getElementById('hideLastNameStatus');

function getIcon() {
    return status.querySelector('i');
}

function isCurrentlyHidden() {
    return getIcon().classList.contains('bi-check-circle');
}

let requestedValue;

toggle.onclick = () => {
    requestedValue = !isCurrentlyHidden();
    emit('set_setting', { hide_last_name: requestedValue });
};

socket.on('setting_updated', res => {
    if (!res.success) {
        flash("Fehler beim Ändern der Einstellung: 'Nachnamen verbergen'.", 'warning');
        return;
    }

    const icon = getIcon();
    icon.className = requestedValue
        ? 'bi bi-check-circle text-success'
        : 'bi bi-x-circle text-danger';
});

const submitBtn = document.getElementById('submitTrack');
const form = document.getElementById('trackForm');
const requiredFields = ['week_good', 'week_bad', 'goal_next_week'].map(id => document.getElementById(id));

function validateInputs() {
    const allValid = requiredFields.every(field => field.value.trim().length >= 20);
    submitBtn.disabled = !allValid;
}

requiredFields.forEach(field => {
    field.addEventListener('input', validateInputs);
});

validateInputs();

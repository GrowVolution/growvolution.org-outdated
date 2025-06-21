const form = document.getElementById("reflectionForm");
const submitBtn = document.getElementById("submitBtn");
const focusCheckboxes = form.querySelectorAll("input[name='focus']");
const stepCheckboxes = form.querySelectorAll("input[name='steps']");
const currentInput = form.querySelector("#currentState");
const goalInput = form.querySelector("#goalState");
const stepThoughts = form.querySelector("#stepThoughts");

const originalData = {
current: currentInput.value.trim(),
goal: goalInput.value.trim(),
step_thoughts: stepThoughts.value.trim(),
focus: new Set([...focusCheckboxes].filter(cb => cb.checked).map(cb => cb.value)),
steps: new Set([...stepCheckboxes].filter(cb => cb.checked).map(cb => cb.value)),
};

function updateFocusLimit(e) {
const checked = [...focusCheckboxes].filter(cb => cb.checked);
if (checked.length > 3) {
  e.target.checked = false;
  showInfo("Limit erreicht","Du kannst maximal 3 Bereiche auswählen.");
}
}

function hasChanged() {
const current = currentInput.value.trim();
const goal = goalInput.value.trim();
const stepT = stepThoughts.value.trim();
const focus = new Set([...focusCheckboxes].filter(cb => cb.checked).map(cb => cb.value));
const steps = new Set([...stepCheckboxes].filter(cb => cb.checked).map(cb => cb.value));

const focusChanged = focus.size !== originalData.focus.size ||
  [...focus].some(val => !originalData.focus.has(val));
const stepsChanged = steps.size !== originalData.steps.size ||
  [...steps].some(val => !originalData.steps.has(val));

return (
  (current !== originalData.current && current.length > 50) ||
  (goal !== originalData.goal && goal.length > 50) ||
  (stepT !== originalData.step_thoughts) ||
  focusChanged || stepsChanged
);
}

function checkValidity() {
const current = currentInput.value.trim();
const goal = goalInput.value.trim();
submitBtn.classList.toggle("d-none", !(hasChanged() && current.length > 50 && goal.length > 50));
}

focusCheckboxes.forEach(cb => {
cb.addEventListener("change", (e) => {
  updateFocusLimit(e);
  checkValidity();
});
});

stepCheckboxes.forEach(cb => cb.addEventListener("change", checkValidity));
[currentInput, goalInput, stepThoughts].forEach(el => el.addEventListener("input", checkValidity));

checkValidity();
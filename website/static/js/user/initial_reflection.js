import { openModal, closeModal } from "/static/js/shared/modal_control.js";

const modalId = 'reflectionModal';

let reflectionShown = document.getElementById('reflectionShown').textContent === 'true';
const reflectionToggle = document.getElementById('reflectionToggle');
const modalCloseBtn = document.getElementById(modalId).querySelector('.btn-close');
modalCloseBtn.dataset.bsDismiss = null;

const steps = document.querySelectorAll(".step");
const progressBar = document.getElementById("reflectionProgress");
const nextBtn = document.getElementById("nextStep");
const prevBtn = document.getElementById("prevStep");

let currentStep = 0;
let navigatedFurther;
const formData = new FormData();

function updateStepDisplay() {
  steps.forEach((step, index) => {
    step.classList.toggle("d-none", index !== currentStep);
  });

  prevBtn.disabled = currentStep === 0;
  nextBtn.textContent = currentStep === steps.length - 1 ? "Fertig" : "Weiter";
  nextBtn.className = currentStep === steps.length - 1 ? "btn btn-success" : "btn btn-primary";
  progressBar.style.width = `${(currentStep / (steps.length - 1)) * 100}%`;

  validateCurrentStep();
}

function validateCurrentStep() {
  let isValid;

  switch (currentStep) {
    case 1: {
      const val = document.getElementById("current").value.trim();
      isValid = val.length > 50;
      break;
    }
    case 2: {
      const val = document.getElementById("goal").value.trim();
      const selected = document.querySelectorAll(".focus-option.active");
      isValid = val.length > 50 && selected.length >= 1;
      break;
    }
    case 3: {
      const checked = document.querySelectorAll("#stepSelect input[type=checkbox]:checked");
      const thoughts = document.getElementById("stepThoughts").value.trim();
      isValid = checked.length >= 1 || thoughts.length > 0;
      break;
    }
    default:
      isValid = true;
  }

  nextBtn.disabled = !isValid;
}

const group = document.getElementById("focusGroup");
group.addEventListener("click", (e) => {
  if (!e.target.classList.contains("focus-option")) return;

  e.target.classList.toggle("active");

  const active = group.querySelectorAll(".focus-option.active");

  if (active.length > 3) {
    e.target.classList.remove("active");
    alert("Bitte wähle maximal 3 Bereiche aus.");
    return;
  }

  validateCurrentStep();
});

["current", "goal", "stepThoughts"].forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener("input", validateCurrentStep);
  }
});

document.querySelectorAll("#stepSelect input[type=checkbox]").forEach(cb => {
  cb.addEventListener("change", validateCurrentStep);
});

nextBtn.addEventListener("click", async () => {
  collectStepData(currentStep);

  if (currentStep < steps.length - 1) {
    navigatedFurther = true;
    currentStep++;
    updateStepDisplay();
  } else {
    sendReflectionData();
  }
});

prevBtn.addEventListener("click", () => {
  if (currentStep > 0) {
    currentStep--;
    updateStepDisplay();
  }
});

function collectStepData(step) {
  switch (step) {
    case 1:
      formData.set("current", document.getElementById("current").value.trim());
      break;
    case 2: {
      formData.set("goal", document.getElementById("goal").value.trim());
      const focus = Array.from(document.querySelectorAll(".focus-option.active"))
        .map(btn => btn.dataset.value);
      formData.set("focus", JSON.stringify(focus));
      break;
    }
    case 3: {
      const steps = Array.from(document.querySelectorAll("#stepSelect input[type=checkbox]:checked"))
        .map(cb => cb.id);
      formData.set("steps", JSON.stringify(steps));
      formData.set("stepThoughts", document.getElementById("stepThoughts").value.trim());
      break;
    }
    case 4: {
      const tel = document.querySelector('input[type="tel"]').value.trim();
      const consent = document.getElementById("consent").checked;
      if (tel) formData.set("phone", tel);
      formData.set("consent", consent ? "1" : "0");
      break;
    }
  }
}

function sendReflectionData() {
  fetch("/initial-reflection", {
    method: "POST",
    body: formData,
  }).then(response => {
    if (!response.ok) {
      flash("Leider ist etwas schiefgelaufen. Bitte versuche es später nochmal.", 'warning');
      return;
    }
    closeModal(modalId);
    reflectionToggle.classList.remove('d-none');
    reflectionToggle.role = "link";
    reflectionToggle.href = "/foundation";
    reflectionToggle.dataset.bsToggle = null;
    reflectionToggle.dataset.bsTarget = null;
    reflectionToggle.textContent = "Mein Fundament";
  });
}

modalCloseBtn.addEventListener('click', async (e) => {
  closeModal(modalId);

  if (navigatedFurther) {
    const confirmed = await confirmDialoge("Bist du sicher, dass du dieses Fenster schließen möchtest?\n" +
        "Alle Eingaben gehen verloren, sobald du die Seite neu lädst.", 'warning');
    if (!confirmed) {
      showModal();
      return;
    }
  }

  if (!reflectionShown) {
    reflectionShown = true;
    reflectionToggle.classList.remove("d-none");
  }

  flash("In Ordnung, du kannst diesen Schritt jederzeit in der Navigation unter Account -> 'Fundament legen' nachholen.", 'info')
});

function showModal() {
  openModal(modalId);
}

updateStepDisplay();
if (!reflectionShown) setTimeout(showModal, 1000);

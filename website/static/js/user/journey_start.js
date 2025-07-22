import { closeModal, openModal } from "/static/js/shared/modal_control.js";

const modalId = "startJourneyModal"

const journeyToggle = document.getElementById('journeyToggle')

const steps = Array.from(document.querySelectorAll(".journey-step"))
const progressBar = document.getElementById("journeyProgress")
const backBtn = document.getElementById("journeyBackBtn")
const nextBtn = document.getElementById("journeyNextBtn")
const finishBtn = document.getElementById("journeyFinishBtn")
const modalCloseBtn = document.getElementById(modalId).querySelector('.btn-close')
modalCloseBtn.dataset.bsDismiss = null

let currentStep = 0
let navigatedFurther
const formData = new FormData()

updateStep()

backBtn.addEventListener("click", () => {
  if (currentStep > 0) {
    currentStep--
    updateStep()
  }
})

nextBtn.addEventListener("click", () => {
  if (currentStep < steps.length - 1) {
    collectInputs(currentStep)
    currentStep++
    updateStep()

    navigatedFurther = true
  }
})

finishBtn.addEventListener("click", () => {
  if (!validateStep(3)) return
  collectInputs(3)
  fetch("/journey/start", {
    method: "POST",
    body: formData
  })
    .then(res => {
      if (res.ok) {
        closeModal(modalId)

        journeyToggle.role = "link"
        journeyToggle.href = "/foundation"
        journeyToggle.dataset.bsToggle = null
        journeyToggle.dataset.bsTarget = null
        journeyToggle.textContent = "Meine Reise"

        return
      }
      flash("Beim Speichern der Daten ist ein Fehler aufgetreten!", 'danger');
    })
})

steps[1].querySelectorAll("textarea").forEach(el => {
  el.addEventListener("input", () => updateStep())
})

steps[3].querySelectorAll("textarea").forEach(el => {
  el.addEventListener("input", () => updateStep())
})

function updateStep() {
  steps.forEach((step, index) => {
    step.classList.toggle("d-none", index !== currentStep)
  })

  const progress = (currentStep / (steps.length - 1)) * 100
  progressBar.style.width = `${progress}%`

  backBtn.disabled = currentStep === 0
  nextBtn.classList.toggle("d-none", currentStep === steps.length - 1)
  finishBtn.classList.toggle("d-none", currentStep !== steps.length - 1)

  if (currentStep === 1) {
    const vision = steps[1].querySelectorAll("textarea")[0].value.trim()
    const intention = steps[1].querySelectorAll("textarea")[1].value.trim()
    nextBtn.disabled = vision.length < 100 || intention.length < 50
  } else {
    nextBtn.disabled = false
  }

  if (currentStep === 3) {
    const inputs = steps[3].querySelectorAll("textarea")
    const allFilled = Array.from(inputs).every(i => i.value.trim().length >= 50)
    finishBtn.disabled = !allFilled
  }
}

function collectInputs(step) {
  if (step === 1) {
    formData.set("vision", steps[1].querySelectorAll("textarea")[0].value.trim())
    formData.set("intention", steps[1].querySelectorAll("textarea")[1].value.trim())
  }
  if (step === 2) {
    formData.set("discipline", document.getElementById("disciplineRange").value)
    formData.set("energy", document.getElementById("energyRange").value)
    formData.set("focus", document.getElementById("focusRange").value)
  }
  if (step === 3) {
    const fields = steps[3].querySelectorAll("textarea")
    formData.set("goal_5y", fields[0].value.trim())
    formData.set("goal_1y", fields[1].value.trim())
    formData.set("goal_quarter", fields[2].value.trim())
    formData.set("goal_month", fields[3].value.trim())
    formData.set("goal_week", fields[4].value.trim())
    formData.set("auto_correct", steps[3].querySelector('#autoCorrect').checked ? '1' : '0')
  }
}

function validateStep(step) {
  if (step === 3) {
    const inputs = steps[3].querySelectorAll("textarea")
    return Array.from(inputs).every(i => i.value.trim().length >= 50)
  }
  return true
}

modalCloseBtn.addEventListener("click", async () => {
  closeModal(modalId);

  if (navigatedFurther) {
    const confirmed = await confirmDialoge("Bist du sicher, dass du dieses Fenster schließen möchtest?\n" +
        "Alle Eingaben gehen verloren, sobald du die Seite neu lädst.", 'warning')
    if (!confirmed) openModal(modalId)
  }
})
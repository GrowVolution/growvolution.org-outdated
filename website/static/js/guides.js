const onboarding = document.getElementById("onboardingModal")

let understood
if (onboarding) understood = onboarding.querySelector("#understood")

document.querySelectorAll(".modal").forEach(modal => {
  const steps = modal.querySelectorAll(".guide-step")
  if (!steps.length) return

  const backBtn = modal.querySelector("#guideBackBtn")
  const nextBtn = modal.querySelector("#guideNextBtn")
  const finishBtn = modal.querySelector("#guideFinishBtn")

  let currentStep = 0

  const updateStep = () => {
    steps.forEach((el, i) => {
      el.classList.toggle("d-none", i !== currentStep)
    })
    backBtn.disabled = currentStep === 0
    nextBtn.classList.toggle("d-none", currentStep === steps.length - 1)
    finishBtn.classList.toggle("d-none", currentStep !== steps.length - 1)
  }

  if (backBtn && nextBtn && finishBtn) {
    backBtn.addEventListener("click", () => {
      if (currentStep > 0) {
        currentStep--
        updateStep()
      }
    })

    nextBtn.addEventListener("click", () => {
      if (currentStep < steps.length - 1) {
        currentStep++
        updateStep()
      }
    })

    finishBtn.addEventListener("click", () => {
      if (onboarding && understood.checked) emit('onboarding_done')
    })

    modal.addEventListener("shown.bs.modal", () => {
      currentStep = 0
      updateStep()
    })
  }
})

if (onboarding) {
  const reflectionShownEl = document.getElementById('reflectionShown')
  const reflectionShown = !reflectionShownEl || reflectionShownEl && reflectionShownEl.textContent === 'true'

  if (reflectionShown) {
    const modal = new bootstrap.Modal(onboarding)
    modal.show()
  }
}

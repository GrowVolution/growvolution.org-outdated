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

    modal.addEventListener("shown.bs.modal", () => {
      currentStep = 0
      updateStep()
    })
  }
})

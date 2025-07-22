const motivationSelect = document.getElementById("motivationSelect")
const motivationAnswerWrapper = document.getElementById("motivationAnswerWrapper")
const motivationAnswer = document.getElementById("motivationAnswer")
const submitBtn = document.getElementById("submitTrack")

function updateMotivationVisibility() {
  const selected = motivationSelect.value
  const text = motivationAnswer.value.trim()

  if (selected) {
    motivationAnswerWrapper.classList.remove("d-none")
    submitBtn.disabled = text.length < 10
  } else {
    motivationAnswerWrapper.classList.add("d-none")
    submitBtn.disabled = false
  }
}

motivationSelect.addEventListener("change", updateMotivationVisibility)
motivationAnswer.addEventListener("input", updateMotivationVisibility)

updateMotivationVisibility()

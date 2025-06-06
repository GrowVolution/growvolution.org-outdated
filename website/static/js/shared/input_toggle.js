export function toggleInputs(disabled, ...elements) {
  elements.forEach(el => {
    if (el) el.disabled = disabled;
  });
}

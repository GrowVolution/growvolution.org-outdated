export function validatePasswordStrength(input, hint) {
  const strong = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$/.test(input.value);
  hint.classList.toggle('d-none', strong || !input.value);
  return strong;
}

export function validateMatch(inputA, inputB, hint) {
  const match = inputA.value === inputB.value;
  hint.classList.toggle('d-none', match || !inputB.value);
  return match;
}

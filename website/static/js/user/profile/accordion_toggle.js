const chevrons = document.querySelectorAll('.bi-chevron-down');

chevrons.forEach(chevron => {
  const container = chevron.closest('[data-bs-toggle="collapse"]');
  if (!container) return;

  const targetId = container.getAttribute('data-bs-target');
  const target = document.querySelector(targetId);
  if (!target) return;

  target.addEventListener('show.bs.collapse', () => {
    chevron.style.transform = 'rotate(180deg)';
  });

  target.addEventListener('hide.bs.collapse', () => {
    chevron.style.transform = 'rotate(0deg)';
  });

  chevron.style.transition = 'transform 0.3s';
});

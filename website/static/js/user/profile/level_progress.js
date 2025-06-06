const progressBar = document.querySelector('.progress-bar');

if (progressBar) {
  const target = parseFloat(progressBar.getAttribute('aria-valuenow'));
  let current = 0;
  const step = Math.max(1, target / 30);

  const interval = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(interval);
    }
    progressBar.style.width = current + '%';
  }, 15);
}

function resizeLevels() {
  document.querySelectorAll('.level').forEach(level => {
    const label = level.querySelector('.level-label');
    const status = level.querySelector('.level-status');

    if (label && status) {
      status.style.transform = 'none'; // reset before measuring
      const labelWidth = label.offsetWidth;
      const statusWidth = status.scrollWidth;
      const scale = labelWidth / statusWidth;

      status.style.transform = `scaleX(${scale})`;
      level.style.width = `${labelWidth}px`;
    }
  });
}

window.addEventListener('resize', resizeLevels);
resizeLevels();


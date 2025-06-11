const progressBar = document.querySelector('.progress-bar');
const currentLevelStatus = document.querySelector('.level.current').querySelector('.level-status').textContent;

function animateProgress(current = 0) {
  const target = parseFloat(progressBar.getAttribute('aria-valuenow'));
  const step = Math.max(1, (target - current) / 30);

  const interval = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(interval);
    }
    progressBar.style.width = current + '%';
  }, 20);
}

if (progressBar) animateProgress();

socket.on('score_update', (data) => {
  let levelChanged;

  document.querySelectorAll('.level').forEach(level => {
    const label = level.querySelector('.level-label');
    const status = level.querySelector('.level-status');

    if (level.classList.contains('current')) {
      const levelStatus = data.level_status

      label.textContent = `LEVEL ${data.level}`;
      status.textContent = levelStatus;

      levelChanged = currentLevelStatus !== levelStatus;
    } else {
      label.textContent = `LEVEL ${data.level + 1}`;
      status.textContent = data.next_level_status;
    }
  });
  resizeLevels();

  let current;
  if (levelChanged) current = 0;
  else current = parseFloat(progressBar.getAttribute('aria-valuenow'));

  progressBar.setAttribute('aria-valuenow', data.score);
  animateProgress(current);
});

function resizeLevels() {
  document.querySelectorAll('.level').forEach(level => {
    const label = level.querySelector('.level-label');
    const status = level.querySelector('.level-status');

    if (label && status) {
      status.style.transform = 'none';
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

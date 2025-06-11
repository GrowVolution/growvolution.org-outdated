const dashboardScript = document.getElementById('dashboardScript');
const score = parseFloat(dashboardScript.dataset.score) / 100;

const icon = document.getElementById('icon');
const level = document.getElementById('level');
const status = document.getElementById('status');

const bar = new ProgressBar.Path('#progressPath', {
  duration: 1000,
  easing: 'easeInOut'
});

if (score >= 0.01) bar.path.setAttribute('stroke', '#198754');
bar.animate(score);

socket.on('score_update', (data) => {
    bar.path.setAttribute('stroke', '#198754');
    bar.animate(data.score / 100);

    icon.className = `bi ${data.level_icon} fs-1`;
    level.textContent = data.level;
    status.textContent = data.level_status;
});
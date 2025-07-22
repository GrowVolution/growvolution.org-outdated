const navTitle = document.getElementById('navTitle');
let showsTimer = false;

function getRemainingMinutesToday() {
  const now = new Date();
  const endOfDay = new Date(now);
  endOfDay.setHours(23, 59, 59, 999);

  const diffMilliseconds = endOfDay - now;

  return Math.floor(diffMilliseconds / 60000);
}

function changeNavTitle() {
    if (showsTimer) {
        navTitle.textContent = "GrowVolution";
        showsTimer = false;
    } else {
        navTitle.textContent = `${getRemainingMinutesToday()} Minuten vom Tag übrig.`;
        showsTimer = true;
    }
}

setInterval(changeNavTitle, 5000);
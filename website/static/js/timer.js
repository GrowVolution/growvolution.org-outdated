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
    } else {
        navTitle.textContent = `Noch ${getRemainingMinutesToday()} vom Tag übrig.`;
    }
}

setInterval(changeNavTitle, 3000);
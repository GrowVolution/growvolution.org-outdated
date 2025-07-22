const flashContainer = document.getElementById('flashContainer');

const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
const confirmText = document.getElementById('dialogeConfirmText');
const confirmBtn = document.getElementById('dialogeConfirmBtn');
const dismissBtn = document.getElementById('dialogeDismissBtn');

const infoModal = new bootstrap.Modal(document.getElementById('infoModal'));
const infoTitle = document.getElementById('infoModalTitle');
const infoText = document.getElementById('infoModalText');
const infoBody = document.getElementById('infoModalBody');


function flash(message, category) {
    flashContainer.innerHTML = `
    <div class="alert alert-${category} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    `
}


async function confirmDialoge(message, category) {
    confirmText.innerHTML = message.replace(/\n/g, "<br>");
    confirmBtn.className = `btn btn-${category}`;

    return new Promise((resolve) => {
        function onConfirm() {
            cleanup();
            resolve(true);
        }

        function onDismiss() {
            cleanup();
            resolve(false);
        }

        function cleanup() {
            confirmBtn.removeEventListener('click', onConfirm);
            dismissBtn.removeEventListener('click', onDismiss);
            confirmModal.hide();
        }

        confirmBtn.addEventListener('click', onConfirm);
        dismissBtn.addEventListener('click', onDismiss);

        confirmModal.show();
    });
}


function showInfo(title, message, html) {
    infoTitle.textContent = title;
    if (message) {
        infoBody.classList.add('d-none');
        infoText.classList.remove('d-none')
        infoText.textContent = message;
    } else {
        infoText.classList.add('d-none');
        infoBody.classList.remove('d-none');
        infoBody.innerHTML = html;
    }
    infoModal.show();
}


function updateAnchorHighlightListeners() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(link => {
        if (link.dataset.hasAnchorListener === 'true') return;

        link.addEventListener("click", e => {
            const targetId = link.getAttribute("href").substring(1);
            const target = document.getElementById(targetId);
            if (target) {
              setTimeout(() => {
                target.classList.add("highlight-flash");
                setTimeout(() => target.classList.remove("highlight-flash"), 1500);
              }, 100);
            }
        });

        link.dataset.hasAnchorListener = 'true';
    });
}


function execute(fnName, ...args) {
    if (typeof window[fnName] === 'function') {
        window[fnName](...args)
    } else {
        flash("Beim Ausführen der Aktion ist ein Fehler aufgetreten. (Siehe Console)", 'warning')
        console.log("Given function not found: ", fnName)
    }
}


updateAnchorHighlightListeners();
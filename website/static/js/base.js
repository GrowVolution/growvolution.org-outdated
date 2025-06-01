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
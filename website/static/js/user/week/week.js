document.querySelectorAll('input[type="checkbox"][id^="done-"], button[id^="done-"]').forEach(el => {
    el.addEventListener('click', function () {
        const id = this.id.replace('done-', '')
        this.disabled = true
        emit('week_task_done', id)
    })
})

socket.on('reliability_score', score => {
    const bar = document.querySelector('.progress-bar')
    bar.style.width = `${score}%`
    bar.textContent = `${score}%`
})

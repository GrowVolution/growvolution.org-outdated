onCommentReply = onReply
initRepliesFn = initReplies


function onSendReply(commentID, replyID = null) {
    const text = commentText.value.trim()
    if (!text || text.length > 512) {
        flash("Die Antwort darf nicht leer oder länger als 512 Zeichen sein!", 'warning')
        return
    }

    emit('add_reply', {
        comment: commentID,
        mention: replyID,
        content: text
    })
}


function appendReplyToContainer(replyContainer, replyHTML) {
    const newReply = getHtmlAsChild(replyHTML)

    let action = replyContainer.querySelector('a.has-replies')
    if (!action) {
        action = replyContainer.querySelector('a')
        action.classList.remove('text-muted')
        action.classList.add('text-dark')
        action.classList.add('text-hover-muted')
        action.classList.add('has-replies')
        action.innerHTML = '<i>Antwort verbergen</i>'
        action.dataset.repliesLoaded = 'true'
    }
    const copy = action.cloneNode(true)

    replyContainer.removeChild(action)
    replyContainer.appendChild(newReply)
    replyContainer.appendChild(copy)
    initAction(copy)
    initReply(newReply)
}


function onReply(element) {
    const modal = openCommentModal(true)

    const replyContainer = element.closest('.comment').querySelector('.replies')
    htmlEventHandler = (html) => {
        appendReplyToContainer(replyContainer, html)
        modal.hide()
    }

    const comment = element.closest('.comment')
    onSendButtonClick = () => {
        onSendReply(comment.id.replace(`comment-`, ''))
    }
}


function onSubReply() {
    const reply = this.closest('div.reply')
    const to = reply.querySelector('.author').textContent
    const modal = openCommentModal(true, to)

    htmlEventHandler = (html) => {
        appendReplyToContainer(reply.closest('.replies'), html)
        modal.hide()
    }

    const comment = this.closest('.comment')
    onSendButtonClick = () => {
        onSendReply(comment.id.replace(`comment-`, ''), reply.id.replace(`reply-`, ''))
    }
}


function initReply(reply) {
    reply.querySelectorAll('a').forEach(action => {
        if (action.classList.contains('reply')) {
            action.addEventListener('click', onSubReply)
            return
        }
        initAction(action, 'reply')
    })
}


function initReplies(replyContainer) {
    replyContainer.querySelectorAll('.reply').forEach(reply => {
        initReply(reply)
        reply.querySelectorAll('.reaction-option').forEach(option => {
            option.addEventListener('click', () => onReactionChange(option))
        })
    })
}
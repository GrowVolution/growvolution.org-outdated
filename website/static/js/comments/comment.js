const commentContainer = document.getElementById('comments');
const comments = document.querySelectorAll('.comment');
const addComment = document.getElementById('addComment');
const blogID = document.getElementById('id').textContent;
let onCommentReply


function getHtmlAsChild(html) {
    const tmp = document.createElement('div')
    tmp.innerHTML = html
    return tmp.firstElementChild
}


function onAddComment() {
    const modal = openCommentModal()

    onSendButtonClick = () => {
        const text = commentText.value.trim()
        if (!text || text.length > 512) {
            flash("Der Kommentar darf nicht leer oder länger als 512 Zeichen sein!", 'warning')
            return
        }

        emit('add_comment', {
            ref: blogID,
            type: 'blog',
            text: text
        })
    }

    htmlEventHandler = (html) => {
        const newComment = getHtmlAsChild(html)
        commentContainer.appendChild(newComment)
        initComment(newComment)
        modal.hide()
    }
}


function updateLikeElement(element, leave = false) {
    const icon = element.querySelector('i')

    if (element.dataset.liked !== 'true') {
        const showFilled = !leave

        icon.classList.toggle('bi-heart-fill', showFilled)
        icon.classList.toggle('bi-heart', !showFilled)
        icon.classList.toggle('text-danger', showFilled)
    }
}


function onHover() {
    updateLikeElement(this)
}


function onLeave() {
    updateLikeElement(this, true)
}


function onLike(actionClass, trigger) {
    const icon = trigger.querySelector('i')
    const isLiked = trigger.dataset.liked === 'true'

    trigger.dataset.liked = (!isLiked).toString()

    icon.classList.toggle('bi-heart-fill', !isLiked)
    icon.classList.toggle('bi-heart', isLiked)
    icon.classList.toggle('text-danger', !isLiked)

    const referenceID = trigger.closest(`.${actionClass}`).id.replace(`${actionClass}-`, '');
    const data = {
        ref: referenceID,
        type: actionClass
    }

    const likeCounter = trigger.querySelector('.like-count')
    const likeCount = parseInt(likeCounter.textContent)
    if (isLiked) {
        likeCounter.textContent = `${likeCount - 1}`
        emit('remove_like', data)
    } else {
        likeCounter.textContent = `${likeCount + 1}`
        emit('add_like', data)
    }
}


function onCommentSystemEdit(actionClass, trigger) {
    if (trigger.classList.contains('save')) {
        const referenceID = trigger.closest(`.${actionClass}`).id.replace(`${actionClass}-`, '')
        onCommentSystemSave(referenceID, actionClass, trigger)
        return
    }

    trigger.classList.add('save')
    trigger.innerHTML = '<i class="bi bi-save"></i> Speichern'

    const contentBox = trigger.closest(`.${actionClass}`).querySelector('.text-content')
    if (contentBox.querySelector('textarea')) return

    const paragraph = contentBox.querySelector('p')
    const textEdit = document.createElement('textarea')
    const textContent = paragraph.textContent.trim()
    textEdit.setAttribute('rows', '3')
    textEdit.classList.add('form-control')
    textEdit.value = textContent
    localStorage.setItem('editText', textContent)

    const lengthInfo = document.createElement('small')
    lengthInfo.className = 'form-text text-muted mt-1'

    textEdit.addEventListener('input', () => {
        updateLengthInfo(lengthInfo, textEdit)
    })
    updateLengthInfo(lengthInfo, textEdit)

    contentBox.removeChild(paragraph)
    contentBox.appendChild(textEdit)
    contentBox.appendChild(lengthInfo)
}


function onCommentSystemSave(referenceID, actionClass, trigger) {
    const contentBox = trigger.closest(`.${actionClass}`).querySelector('.text-content')
    if (contentBox.querySelector('p')) return

    const textEdit = contentBox.querySelector('textarea')
    const text = textEdit.value.trim()
    if (!text || text.length > 512) {
        flash("Der Inhalt darf nicht leer sein oder länger als 512 Zeichen sein!", 'warning')
        return
    }

    const lengthInfo = contentBox.querySelector('small')
    const paragraph = document.createElement('p')
    paragraph.textContent = text

    contentBox.removeChild(textEdit)
    contentBox.removeChild(lengthInfo)
    contentBox.appendChild(paragraph)

    trigger.classList.remove('save')
    trigger.innerHTML = '<i class="bi bi-pencil"></i> Bearbeiten'

    const editText = localStorage.getItem('editText')
    localStorage.removeItem('editText')
    if (editText === text) return

    emit('comment_system_edit', {
        ref: referenceID,
        type: actionClass,
        text: text
    })
}


function onDelete(actionClass, trigger) {
    let typeText
    const isComment = actionClass === 'comment'
    if (isComment)
        typeText = 'deinen Kommentar'
    else typeText = 'deine Antwort'
    const confirmed = confirm(`Möchtest du ${typeText} wirklich entfernen?`)
    if (! confirmed) return

    const element = trigger.closest(`.${actionClass}`)
    emit('comment_system_delete', {
        ref: element.id.replace(`${actionClass}-`, ''),
        type: actionClass
    })

    if (isComment) commentContainer.removeChild(element)
    else element.closest('.replies').removeChild(element)
}


function loadReplies() {
    const replies = this.closest('.replies')
    const copy = this.cloneNode(true)

    if (this.dataset.repliesLoaded === 'true') {
        const replyCount = replies.querySelectorAll('.reply').length - 1
        copy.innerHTML = `<i>(${replyCount}) Antworten anzeigen</i>`
        copy.dataset.repliesLoaded = 'false'
        replies.innerHTML = ''
        replies.appendChild(copy)
        initAction(copy)
    } else {
        copy.innerHTML = '<i>Antworten verbergen</i>'

        htmlEventHandler = (html) => {
            replies.innerHTML = html
            execute('initReplies', replies)
            replies.appendChild(copy)
            initAction(copy)
            updateAnchorHighlightListeners()
        }
        emit('reply_request', replies.closest('.comment').id.replace(`comment-`, ''))

        copy.dataset.repliesLoaded = 'true'
    }
}


function initAction(action, actionClass = 'comment') {
    if (action.classList.contains('like')) {
        action.addEventListener('mouseover', onHover)
        action.addEventListener('mouseout', onLeave)
        action.addEventListener('click', () => { onLike(actionClass, action) })
    }
    else if (action.classList.contains('reply')) action.addEventListener('click', () => { onCommentReply(action) })
    else if (action.classList.contains('edit')) action.addEventListener('click', () => { onCommentSystemEdit(actionClass, action) })
    else if (action.classList.contains('delete')) action.addEventListener('click', () => { onDelete(actionClass, action) })
    else if (action.classList.contains('has-replies')) action.addEventListener('click', loadReplies)
}


function initComment(comment) {
    comment.querySelectorAll('a').forEach(action => {
        initAction(action)
    })
}


function initComments() {
    comments.forEach(comment => {
        initComment(comment)
    })
}


initComments()
addComment.addEventListener('click', onAddComment)
const modalLabel = document.getElementById('modalLabel');
const replyLabel = document.getElementById('replyLabel');
const commentText = document.getElementById('commentText');


const sendButton = document.getElementById('sendComment');
let onSendButtonClick
sendButton.addEventListener('click', () => {
    onSendButtonClick();
});


function openCommentModal(reply = false, replyTo = null) {
    if (reply) modalLabel.textContent = "Antwort schreiben";
    else modalLabel.textContent = "Kommentar schreiben";

    if (replyTo) {
      document.getElementById('replyInfo').textContent = `@${replyTo}`;
      replyLabel.classList.remove('d-none');
    } else {
      replyLabel.classList.add('d-none');
    }

    updateLengthInfo(document.getElementById('lengthInfo'), commentText);

    const commentModal = new bootstrap.Modal(document.getElementById('commentModal'));
    commentModal.show();
    return commentModal;
}


function updateLengthInfo(lengthInfo, textEdit) {
    const length = 512 - textEdit.value.length;
    lengthInfo.textContent = `${length}`;

    if (length < 0) {
        lengthInfo.classList.remove('text-muted');
        lengthInfo.classList.add('text-danger');
    } else {
        lengthInfo.classList.remove('text-danger');
        lengthInfo.classList.add('text-muted');
    }
}


commentText.addEventListener('input', () => {
    const lengthInfo = document.getElementById('lengthInfo');
    updateLengthInfo(lengthInfo, commentText);
});
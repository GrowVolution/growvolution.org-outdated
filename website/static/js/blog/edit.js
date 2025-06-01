const postID = document.getElementById('id').textContent;

const title = document.getElementById('title');
const titleEdit = document.getElementById('titleEdit');
const content = document.getElementById('content');
const contentEdit = document.getElementById('contentEdit');

const postContent = document.getElementById('postContent');
const summary = document.getElementById('summary');
const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');
const imageSource = content.querySelector('img').src;

const editBtn = document.getElementById('edit');
const resetBtn = document.getElementById('reset');

let editMode = false;


function onBlogEdit() {
    editBtn.innerHTML = '<i class="bi bi-save"></i> Speichern'
    resetBtn.classList.remove('d-none');
    editMode = true

    quill.clipboard.dangerouslyPasteHTML(postContent.innerHTML)

    const data = {
        summary: summary.value,
        content: quill.root.innerHTML
    }

    localStorage.setItem('blogData', JSON.stringify(data))
}


function onBlogSave() {
    const data = loadData()

    const titleEdited = titleEdit.value !== title.textContent
    const summaryEdited = summary.value !== data.summary
    const contentEdited = quill.root.innerHTML !== data.content
    const imageEdited = imageInput.files.length > 0

    if (!titleEdited && !summaryEdited && !contentEdited && !imageEdited) {
        editBtn.innerHTML = '<i class="bi bi-pencil"></i> Bearbeiten'
        resetBtn.classList.add('d-none')
        editMode = false
        return
    } else if (quill.getText().trim().length < 500) {
        flash('Der Beitragstext muss mindestens 500 Zeichen lang sein.', 'warning')
        return
    } else if (!titleEdit.value.trim() || !summary.value.trim()) {
        flash('Die Felder dürfen nicht leer sein.', 'warning')
        return
    }

    const formData = new FormData()

    if (titleEdited) formData.append('title', titleEdit.value)
    if (summaryEdited) formData.append('summary', summary.value)
    if (contentEdited) formData.append('content', quill.root.innerHTML)
    if (imageEdited) formData.append('image', imageInput.files[0])

    const xhr = new XMLHttpRequest();
    xhr.open('POST', `/blog/${postID}/edit`, true);

    editBtn.disabled = true;
    editBtn.innerHTML = `
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      <span class="ms-2" id="progressText">0%</span>
    `;

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            document.getElementById('progressText').textContent = `${percent}%`;
        }
    };

    xhr.onload = function () {
        if (xhr.status === 200) {
            window.location.reload();
        } else {
            flash('Beim Speichern ist ein Fehler aufgetreten: ' + xhr.statusText, 'danger');
            editBtn.disabled = false;
            editBtn.innerHTML = '<i class="bi bi-save"></i> Speichern';
        }
    };

    xhr.onerror = function () {
        flash('Netzwerkfehler beim Speichern.', 'danger');
        editBtn.disabled = false;
        editBtn.innerHTML = '<i class="bi bi-save"></i> Speichern';
    };

    xhr.send(formData);
}


function updateDisplayClass(element, showInEditMode = false) {
    if (editMode && showInEditMode || !editMode && !showInEditMode)
        element.classList.remove('d-none')
    else element.classList.add('d-none')
}


function loadData() {
    return JSON.parse(localStorage.getItem('blogData'))
}


editBtn.addEventListener('click', () => {
    if (editMode) onBlogSave()
    else onBlogEdit()

    updateDisplayClass(title)
    updateDisplayClass(titleEdit, true)
    updateDisplayClass(content)
    updateDisplayClass(contentEdit, true)
})


resetBtn.addEventListener('click', () => {
    const data = loadData()
    titleEdit.value = title.textContent
    summary.value = data.summary
    quill.clipboard.dangerouslyPasteHTML(data.content)
    preview.src = imageSource
})
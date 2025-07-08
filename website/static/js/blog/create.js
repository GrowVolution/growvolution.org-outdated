document.getElementById('reset').addEventListener('click', () => {
    document.getElementById('title').value = '';
    document.getElementById('image_file').value = '';
    document.getElementById('summary').value = '';
    quill.setText('');
    document.getElementById('imagePreview').innerHTML = '<i class="bi bi-image" style="font-size: 2rem;"></i>';
    localStorage.removeItem('blogEntryData');
});


function saveEntryLocal() {
    const title = document.getElementById('title').value;
    const summary = document.getElementById('summary').value;
    const content = quill.root.innerHTML;

    const imageInput = document.getElementById('image_file');
    const file = imageInput.files[0];

    const saveData = (imageDataUrl = null) => {
      const entry = {
        title,
        summary,
        content,
        image: imageDataUrl
      };
      localStorage.setItem('blogEntryData', JSON.stringify(entry));
    };

    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        saveData(e.target.result);
      };
      reader.readAsDataURL(file);
    } else {
      saveData(null);
    }
}


document.getElementById('save').addEventListener('click', () => {
    saveEntryLocal();
    flash("Beitrag lokal gespeichert!", 'info');
});

document.getElementById('image_file').addEventListener('change', function () {
    const file = this.files[0];
    const preview = document.getElementById('imagePreview');
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.innerHTML = `<img src="${e.target.result}" alt="Vorschau" class="img-fluid rounded">`;
      }
      reader.readAsDataURL(file);
    } else {
      preview.innerHTML = '<i class="bi bi-image" style="font-size: 2rem;"></i>';
    }
});


function loadEntry() {
  const saved = localStorage.getItem('blogEntryData');
  if (saved) return JSON.parse(saved);
  return null
}


const entry = loadEntry();
if (entry) {
    document.getElementById('title').value = entry.title || '';
    document.getElementById('summary').value = entry.summary || '';
    quill.root.innerHTML = entry.content || '';
    document.getElementById('content').value = entry.content || '';

    if (entry.image) {
      const preview = document.getElementById('imagePreview');
      preview.innerHTML = `<img src="${entry.image}" alt="Vorschau" class="img-fluid rounded">`;
    }
}


document.getElementById('submit').addEventListener('click', function () {
    const fileInput = document.getElementById('image_file');
    const title = document.getElementById('title').value.trim();
    const summary = document.getElementById('summary').value.trim();
    const contentHtml = quill.root.innerHTML.trim();
    const contentText = quill.getText().trim();

    if (contentText.length < 500) {
      flash('Der Beitragstext muss mindestens 500 Zeichen lang sein.', 'warning');
      return;
    }

    if (!title || !summary) {
      flash('Die Felder dürfen nicht leer sein.', 'warning');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('summary', summary.replace(/\n/g, '<br>'));
    formData.append('content', contentHtml);

    if (fileInput.files.length > 0) {
      formData.append('image_file', fileInput.files[0]);
    } else {
      const entry = loadEntry();
      if (entry?.image) {
        formData.append('base64_image', entry.image);
      } else {
        flash('Keine Bilddatei ausgewählt.', 'warning');
        return;
      }
    }

    const icon = document.getElementById('submitIcon');
    const text = document.getElementById('submitText');
    icon.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    text.textContent = 'Wird hochgeladen... 0%';

    const xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.href, true);

    xhr.upload.onprogress = function (e) {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        text.textContent = `Wird hochgeladen... ${percent}%`;
      }
    };

    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        text.textContent = 'Erfolgreich!';
        localStorage.removeItem('blogEntryData');
        setTimeout(() => window.location.href = '/blog', 800);
      } else {
        flash('Fehler beim Hochladen: ' + xhr.statusText, 'danger');
        icon.innerHTML = '<i class="bi bi-upload"></i>';
        text.textContent = 'Veröffentlichen';
      }
    };

    xhr.onerror = function () {
      flash('Netzwerkfehler beim Upload.', 'danger');
      icon.innerHTML = '<i class="bi bi-upload"></i>';
      text.textContent = 'Veröffentlichen';
    };

    xhr.send(formData);
});

setInterval(() => {
    saveEntryLocal();
    flash("Beitrag automatisch lokal zwischengespeichert!", 'info');
}, 600000);
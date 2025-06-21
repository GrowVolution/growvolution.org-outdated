const input = document.getElementById('profilePictureInput');
const preview = document.getElementById('profilePicturePreview');
const saveBtn = document.getElementById('saveProfilePicture');
const modal = document.getElementById('profilePictureModal');
const progressWrapper = document.getElementById('pictureUploadProgress');
const progressBar = document.getElementById('pictureUploadBar');

let selectedFile = null;

if (input && preview && saveBtn) {
  input.addEventListener('change', () => {
    const file = input.files[0];
    if (!file) {
      preview.src = preview.dataset.original;
      saveBtn.disabled = true;
      return;
    }

    selectedFile = file;
    const reader = new FileReader();
    reader.onload = e => preview.src = e.target.result;
    reader.readAsDataURL(file);
    saveBtn.disabled = false;
  });

  saveBtn.addEventListener('click', () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('image', selectedFile);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/profile/upload_picture', true);

    xhr.upload.addEventListener('progress', e => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        progressWrapper.classList.remove('d-none');
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
      }
    });

    xhr.onload = () => {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        document.querySelector('#profilePictureContainer img').src = response.new_picture_url;
        bootstrap.Modal.getInstance(modal).hide();
        input.value = '';
        preview.src = preview.dataset.original;
        progressBar.style.width = '0%';
        progressBar.textContent = '';
        progressWrapper.classList.add('d-none');
        saveBtn.disabled = true;
      } else {
        showInfo("Fehler", "Fehler beim Hochladen: " + xhr.statusText);
      }
    };

    xhr.send(formData);
  });
}

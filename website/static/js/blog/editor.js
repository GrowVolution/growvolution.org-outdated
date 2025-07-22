const quill = new Quill('#editor', {
    theme: 'snow',
    placeholder: 'Schreib los ...',
    modules: {
      toolbar: [
        [{ 'font': [] }, { 'size': [] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'script': 'super' }, { 'script': 'sub' }],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'align': [] }],
        [{ 'list': 'ordered' }, { 'list': 'bullet' }],
        [{ 'indent': '-1' }, { 'indent': '+1' }],
        ['link', 'image']
      ]
    }
});
from website.utils.rendering import render
from website.data import blog as blog_db, cloudinary
from website.logic.auth import get_user
from shared.data import add_model
from flask import request
from werkzeug.datastructures import FileStorage
from binascii import Error as BinasciiError
from io import BytesIO
import base64


def handle_request():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '').strip()

        image_file = request.files.get('image_file')
        base64_image = request.form.get('base64_image')

        if image_file and image_file.filename:
            image = image_file
        elif base64_image:
            try:
                image_data = base64.b64decode(base64_image.split(',')[-1])
                image = FileStorage(
                    stream=BytesIO(image_data),
                    filename='uploaded_image.png',
                    content_type='image/png'
                )
            except (BinasciiError, TypeError, ValueError) as e:
                return str(e), 500
        else:
            return 'Dem Upload hängt kein Bild an!', 500

        result = cloudinary.upload_asset(image)
        user = get_user()
        blog_entry = blog_db.Blog(title, result['public_id'], summary, content, user.username)
        add_model(blog_entry)

        return '', 200

    return render('blog/create.html')
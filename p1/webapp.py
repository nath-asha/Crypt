from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# A dictionary to store user attributes for the demo
users = {
    'alice': ['manager', 'HR'],
    'bob': ['researcher', 'PhD']
}

master_public_key, master_key = setup()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        attributes = request.form['attributes'].split(',')
        # Register the user and generate a key for them
        users[username] = attributes
        user_secret_key = keygen(master_key, attributes)
        # Save the user secret key to a file (for demo purposes)
        with open(f'{username}_secret_key.key', 'wb') as f:
            f.write(user_secret_key)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        username = request.form['username']
        access_policy = request.form['access_policy']
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        enc_file_path, enc_key_path = encrypt_file(file_path, access_policy, master_public_key)
        return f'File encrypted and saved as {enc_file_path} with key {enc_key_path}'
    return render_template('upload.html')

@app.route('/download', methods=['GET', 'POST'])
def download_file():
    if request.method == 'POST':
        username = request.form['username']
        enc_file_name = request.form['enc_file_name']
        enc_key_name = request.form['enc_key_name']
        user_secret_key_path = f'{username}_secret_key.key'
        with open(user_secret_key_path, 'rb') as f:
            user_secret_key = f.read()
        enc_file_path = os.path.join(app.config['UPLOAD_FOLDER'], enc_file_name)
        enc_key_path = os.path.join(app.config['UPLOAD_FOLDER'], enc_key_name)
        dec_file_path = decrypt_file(enc_file_path, enc_key_path, user_secret_key)
        return f'File decrypted and saved as {dec_file_path}'
    return render_template('download.html')

@app.route('/files/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

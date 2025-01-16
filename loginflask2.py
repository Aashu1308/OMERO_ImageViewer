from flask import Flask, redirect, request, render_template_string, session, url_for
import requests
import certifi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

my_omero_instance_url = "https://cerviai-omero.duckdns.org"


# Function to list projects
def list_projects(sess_cookies):
    print(" > Listing projects")
    url = my_omero_instance_url + "/api/v0/m/projects/"
    res = requests.get(url, cookies=sess_cookies, verify=False)
    if res.status_code == 200:
        projects = res.json().get("data", [])
        return projects
    else:
        print("Failed to list projects:", res.text)
        return []


# Function to list datasets
def list_datasets(sess_cookies):
    print(" > Listing datasets")
    url = my_omero_instance_url + "/api/v0/m/datasets/"
    res = requests.get(url, cookies=sess_cookies, verify=False)
    if res.status_code == 200:
        datasets = res.json().get("data", [])
        return datasets
    else:
        print("Failed to list datasets:", res.text)
        return []


# Function to list images
def list_images(sess_cookies):
    print(" > Listing images")
    url = my_omero_instance_url + "/api/v0/m/images/"
    res = requests.get(url, cookies=sess_cookies, verify=False)
    if res.status_code == 200:
        images = res.json().get("data", [])
        return images
    else:
        print("Failed to list images:", res.text)
        return []


@app.route('/')
def home():
    return render_template_string(
        '''
        <h1>Login to OMERO</h1>
        <form action="/login" method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <br>
            <input type="submit" value="Login">
        </form>
        '''
    )


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    sess = requests.session()

    # Step 1: Get the server ID
    url = my_omero_instance_url + "/api/v0/servers/"
    server_request = sess.get(url, verify=False)
    data = server_request.json()
    id_server = int(data["data"][0]["id"])

    # Step 2: Get the CSRF token
    url = my_omero_instance_url + "/api/v0/token/"
    res = sess.get(url, verify=False)
    data = res.json()
    token = data["data"]

    # Step 3: Prepare login payload
    url = my_omero_instance_url + "/api/v0/login/"
    login_payload = {
        "server": id_server,
        "username": username,
        "password": password,
        "csrfmiddlewaretoken": token,
    }

    # Step 4: Set headers including Referer
    headers = {
        "referer": my_omero_instance_url,
        "X-CSRFToken": token,
    }

    # Step 5: Attempt to log in
    res_log = sess.post(url, data=login_payload, headers=headers, verify=False)

    # Step 6: Check if login was successful
    if res_log.status_code == 200 and res_log.json().get("success"):
        session['authenticated'] = True
        session['sess_cookies'] = sess.cookies.get_dict()  # Save cookies
        return redirect(url_for('dashboard'))
    else:
        return "Login failed", 400


@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('home'))

    sess_cookies = session.get('sess_cookies')
    projects = list_projects(sess_cookies)
    datasets = list_datasets(sess_cookies)
    images = list_images(sess_cookies)
    return render_template_string(
        '''
        <h1>Projects, Datasets, and Images</h1>
        <h2>Projects</h2>
        <ul>
            {% for project in projects %}
                <li>Project ID: {{ project['@id'] }}, Name: {{ project['Name'] }}</li>
            {% else %}
                <li>No projects found.</li>
            {% endfor %}
        </ul>
        <h2>Datasets</h2>
        <ul>
            {% for dataset in datasets %}
                <li>Dataset ID: {{ dataset['@id'] }}, Name: {{ dataset['Name'] }}</li>
            {% else %}
                <li>No datasets found.</li>
            {% endfor %}
        </ul>
        <h2>Images</h2>
        <ul>
            {% for image in images %}
                <li>Image ID: {{ image['@id'] }}, Name: {{ image['Name'] }}</li>
            {% else %}
                <li>No images found.</li>
            {% endfor %}
        </ul>
        <h2>Enter Image ID</h2>
        <form action="/redirect_image" method="post">
            <label for="image_id">Image ID:</label>
            <input type="text" id="image_id" name="image_id" required>
            <input type="submit" value="View Image">
        </form>
        ''',
        projects=projects,
        datasets=datasets,
        images=images,
    )


@app.route('/redirect_image', methods=['POST'])
def redirect_image():
    if not session.get('authenticated'):
        return redirect(url_for('home'))

    image_id = request.form['image_id']
    redirect_url = f"{my_omero_instance_url}/webgateway/render_image/{image_id}/"

    return render_template_string(
        '''
        <html>
            <head>
                <script type="text/javascript">
                    window.open("{{ redirect_url }}", "_blank");
                    window.location.href = "/dashboard";
                </script>
            </head>
            <body>
                <p>Redirecting to the image viewer...</p>
            </body>
        </html>
        ''',
        redirect_url=redirect_url,
    )


if __name__ == '__main__':
    app.run(debug=True)

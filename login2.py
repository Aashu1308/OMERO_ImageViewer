import requests
from dotenv import load_dotenv
import os

load_dotenv()

login = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
my_omero_instance_url = "https://demo.openmicroscopy.org"

sess = requests.session()

# Step 1: Get the server ID
print(" > Listing server")
url = my_omero_instance_url + "/api/v0/servers/"
server_request = sess.get(url, verify=False)  # Ensure SSL verification
data = server_request.json()
id_server = int(data["data"][0]["id"])
print("     > using server : " + str(id_server))

# Step 2: Get the CSRF token
print(" > Getting token")
url = my_omero_instance_url + "/api/v0/token/"
res = sess.get(url, verify=False)  # Ensure SSL verification
data = res.json()
token = data["data"]
print("     > using token : " + str(token))

# Step 3: Prepare login payload
url = my_omero_instance_url + "/api/v0/login/"
login_payload = {
    "server": id_server,
    "username": login,
    "password": password,
    "csrfmiddlewaretoken": token,  # Include CSRF token
}

# Step 4: Set headers including Referer
headers = {
    "referer": "https://demo.openmicroscopy.org",
    "X-CSRFToken": token,  # Optionally include CSRF token in headers
}

# Step 5: Attempt to log in
print(" > Attempting to log in")
res_log = sess.post(
    url, data=login_payload, headers=headers, verify=False
)  # Ensure SSL verification
print("Response:", res_log.text)

# Step 6: Check if login was successful
if res_log.status_code == 200 and res_log.json().get("success"):
    print("Login successful!")
    event_context = res_log.json().get("eventContext")
    print("Event Context:", event_context)
else:
    print("Login failed:", res_log.text)
    exit()  # Exit if login fails


# Function to list projects and return the first project ID
def list_projects():
    print(" > Listing projects")
    url = my_omero_instance_url + "/api/v0/m/projects/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        projects = res.json().get("data", [])
        if projects:
            first_project = projects[0]
            print(
                f"First Project ID: {first_project['@id']}, Name: {first_project['Name']}"
            )
            return first_project['@id']
        else:
            print("No projects found.")
            return None
    else:
        print("Failed to list projects:", res.text)
        return None


# Function to list datasets and return the first dataset ID
def list_datasets():
    print(" > Listing datasets")
    url = my_omero_instance_url + "/api/v0/m/datasets/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        datasets = res.json().get("data", [])
        if datasets:
            first_dataset = datasets[0]
            print(
                f"First Dataset ID: {first_dataset['@id']}, Name: {first_dataset['Name']}"
            )
            return first_dataset['@id']
        else:
            print("No datasets found.")
            return None
    else:
        print("Failed to list datasets:", res.text)
        return None


# Function to list images and return the first image ID
def list_images():
    print(" > Listing images")
    url = my_omero_instance_url + "/api/v0/m/images/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        images = res.json().get("data", [])
        if images:
            first_image = images[0]
            print(f"First Image ID: {first_image['@id']}, Name: {first_image['Name']}")
            return first_image['@id']
        else:
            print("No images found.")
            return None
    else:
        print("Failed to list images:", res.text)
        return None


# Function to get a single project by ID
def get_project(project_id):
    if project_id is None:
        return
    print(f" > Getting project with ID: {project_id}")
    url = my_omero_instance_url + f"/api/v0/m/projects/{project_id}/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        project = res.json().get("data", {})
        print(
            f"Project ID: {project['@id']}, Name: {project['Name']}, Description: {project['Description']}"
        )
    else:
        print("Failed to get project:", res.text)


# Function to get a single dataset by ID
def get_dataset(dataset_id):
    if dataset_id is None:
        return
    print(f" > Getting dataset with ID: {dataset_id}")
    url = my_omero_instance_url + f"/api/v0/m/datasets/{dataset_id}/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        dataset = res.json().get("data", {})
        dataset_id = dataset.get('@id', 'N/A')
        name = dataset.get('Name', 'N/A')
        description = dataset.get('Description', 'No description available')
        print(f"Dataset ID: {dataset_id}, Name: {name}, Description: {description}")
        print(f"  URL to Images: {dataset.get('url:images', 'N/A')}")
        print(f"  URL to Projects: {dataset.get('url:projects', 'N/A')}")
    else:
        print("Failed to get dataset:", res.text)


import numpy as np
import matplotlib.pyplot as plt


# Function to get a single image by ID and render it using pixel data from the API
def get_image(image_id):
    if image_id is None:
        return
    print(f" > Getting image with ID: {image_id}")
    url = my_omero_instance_url + f"/api/v0/m/images/{image_id}/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        data = res.json().get("data", [])
        if not data:
            print("No image data found.")
            return

        image = data[0]  # Access the first item in the data list
        image_id = image.get('@id', 'N/A')
        name = image.get('Name', 'N/A')
        acquisition_date = image.get('AcquisitionDate', 'No acquisition date available')
        pixels = image.get('Pixels', {})

        # Extract pixel dimensions
        size_x = pixels.get('SizeX', 1)
        size_y = pixels.get('SizeY', 1)
        size_z = pixels.get('SizeZ', 1)
        size_c = pixels.get('SizeC', 1)

        # Assuming you want to render the middle slice of the first channel
        z = size_z / 2  # Middle slice
        t = 0  # Time point (assuming single time point)

        # Get the pixel data (this assumes the pixel data is available in the response)
        pixel_data = pixels.get(
            'data', None
        )  # Adjust this line based on actual pixel data structure

        if pixel_data is not None:
            # Convert pixel data to a numpy array for rendering
            image_array = np.array(pixel_data).reshape(
                (size_y, size_x)
            )  # Reshape based on dimensions

            # Render the image
            plt.imshow(image_array, cmap='gray')
            plt.title(f"Image ID: {image_id}, Name: {name}")
            plt.axis('off')  # Hide axes
            plt.show()
        else:
            print("No pixel data found in the image response.")
    else:
        print("Failed to get image:", res.text)


# Example usage
if __name__ == "__main__":
    first_project_id = list_projects()  # List all projects and get the first ID
    get_project(first_project_id)  # Get the first project by ID
    first_dataset_id = list_datasets()  # List all datasets and get the first ID
    get_dataset(first_dataset_id)  # Get the first dataset by ID
    first_image_id = list_images()  # List all images and get the first ID
    get_image(first_image_id)  # Get the first image by ID

import requests
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO
import ssl
import urllib.request

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


# Function to list projects
def list_projects():
    print(" > Listing projects")
    url = my_omero_instance_url + "/api/v0/m/projects/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        projects = res.json().get("data", [])
        for project in projects:
            print(
                f"Project ID: {project['@id']}, Name: {project['Name']}, Description: {project['Description']}"
            )
    else:
        print("Failed to list projects:", res.text)


# Function to get a single project by ID
def get_project(project_id):
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


# Function to list datasets
def list_datasets():
    print(" > Listing datasets")
    url = my_omero_instance_url + "/api/v0/m/datasets/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        datasets = res.json().get("data", [])
        for dataset in datasets:
            dataset_id = dataset.get('@id', 'N/A')
            name = dataset.get('Name', 'N/A')
            description = dataset.get('Description', 'No description available')
            print(f"Dataset ID: {dataset_id}, Name: {name}, Description: {description}")
            print(f"  URL: {dataset.get('url:dataset', 'N/A')}")
            print(f"  URL to Images: {dataset.get('url:images', 'N/A')}")
            print(f"  URL to Projects: {dataset.get('url:projects', 'N/A')}")
    else:
        print("Failed to list datasets:", res.text)


# Function to get a single dataset by ID
def get_dataset(dataset_id):
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


# Function to list images
def list_images():
    print(" > Listing images")
    url = my_omero_instance_url + "/api/v0/m/images/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        images = res.json().get("data", [])
        for image in images:
            image_id = image.get('@id', 'N/A')
            name = image.get('Name', 'N/A')
            acquisition_date = image.get(
                'AcquisitionDate', 'No acquisition date available'
            )
            image_url = image.get('url:image', 'N/A')
            pixels = image.get('Pixels', {})
            size_x = pixels.get('SizeX', 'N/A')
            size_y = pixels.get('SizeY', 'N/A')
            size_z = pixels.get('SizeZ', 'N/A')
            size_c = pixels.get('SizeC', 'N/A')
            size_t = pixels.get('SizeT', 'N/A')

            print(
                f"Image ID: {image_id}, Name: {name}, Acquisition Date: {acquisition_date}"
            )
            print(f"  URL: {image_url}")
            print(
                f"  Pixel Dimensions: SizeX={size_x}, SizeY={size_y}, SizeZ={size_z}, SizeC={size_c}, SizeT={size_t}"
            )
    else:
        print("Failed to list images:", res.text)


# Function to get a single image by ID
def get_image(image_id):
    print(f" > Getting image with ID: {image_id}")
    url = my_omero_instance_url + f"/api/v0/m/images/{image_id}/"
    res = sess.get(url, verify=False)
    if res.status_code == 200:
        data = res.json().get("data", [])
        if not data:
            print("No image data found.")
            return

        image = data  # Access the first item in the data list
        image_id = image.get('@id', 'N/A')
        name = image.get('Name', 'N/A')
        acquisition_date = image.get('AcquisitionDate', 'No acquisition date available')
        image_url = image.get('url:image', 'N/A')
        pixels = image.get('Pixels', {})
        channels = pixels.get('Channels', [])

        print(
            f"Image ID: {image_id}, Name: {name}, Acquisition Date: {acquisition_date}"
        )
        print(f"  URL: {image_url}")
        print(
            f"  Pixel Dimensions: SizeX={pixels.get('SizeX', 'N/A')}, SizeY={pixels.get('SizeY', 'N/A')}, SizeZ={pixels.get('SizeZ', 'N/A')}, SizeC={pixels.get('SizeC', 'N/A')}, SizeT={pixels.get('SizeT', 'N/A')}"
        )

        # Print channel details
        for channel in channels:
            channel_name = channel.get('Name', 'N/A')
            emission_wavelength = channel.get('EmissionWavelength', {}).get(
                'Value', 'N/A'
            )
            excitation_wavelength = channel.get('ExcitationWavelength', {}).get(
                'Value', 'N/A'
            )
            print(
                f"  Channel Name: {channel_name}, Emission Wavelength: {emission_wavelength} nm, Excitation Wavelength: {excitation_wavelength} nm"
            )
    else:
        print("Failed to get image:", res.text)


# # Function to render a single tile of an image
# def render_image_tile(image_id, tile_x, tile_y, tile_width, tile_height, channel=1):
#     # Construct the URL for the tile
#     url = f"https://demo.openmicroscopy.org/webgateway/render_image_region/{image_id}/0/0/?tile={tile_x},{tile_y},0,{tile_width},{tile_height}&c={channel}|0:255$808080&m=g&p=normal&q=0.9"

#     print(f"Fetching image tile from: {url}")

#     # Fetch the image data
#     response = requests.get(url)

#     if response.status_code == 200:
#         # Open the image using PIL
#         image = Image.open(BytesIO(response.content))
#         image.show()  # Display the image
#     else:
#         print(f"Failed to fetch image tile: {response.status_code} - {response.text}")


# Function to render a single tile of an image
def render_image_tile(image_id, tile_x, tile_y, tile_width, tile_height, channel=1):
    # Construct the URL for the tile
    url = f"{my_omero_instance_url}/webgateway/render_image_region/{image_id}/0/0/?tile={tile_x},{tile_y},0,{tile_width},{tile_height}&c={channel}|0:255$808080&maps=[{{%22inverted%22:{{%22enabled%22:false}}}}]&m=g&p=normal&q=0.9"

    print(f"Fetching image tile from: {url}")

    # Fetch the image data
    # response = requests.get(url, verify=False)
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context) as response:

        # Open the image using PIL
        img_d = response.read()
        # img = Image.open("gfg.png")
        if img_d:
            img = Image.open(BytesIO(img_d))
            img.show()
        else:
            print("Failed to fetch image tile")


# Example usage
if __name__ == "__main__":
    list_projects()  # List all projects
    get_project(2257)  # Get a specific project by ID
    list_datasets()  # List all datasets
    get_dataset(2558)  # Get a specific dataset by ID
    list_images()  # List all images
    get_image(28725)  # Get a specific image by ID
    render_image_tile(28725, 3, 2, 512, 512)  # render a tile

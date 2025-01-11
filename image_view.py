# import ezomero
from omero.gateway import BlitzGateway
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")


def print_obj(obj, indent=0):
    """
    Helper method to display info about OMERO objects.
    Not all objects will have a "name" or owner field.
    """
    print(
        """%s%s:%s  Name:"%s" (owner=%s)"""
        % (
            " " * indent,
            obj.OMERO_CLASS,
            obj.getId(),
            obj.getName(),
            obj.getOwnerOmeName(),
        )
    )


with BlitzGateway(USERNAME, PASSWORD, host=HOST, port=PORT, secure=True) as conn:
    print("Connected to server")
    for project in conn.getObjects("Project", opts={"name": 'imagetest'}):
        print_obj(project)
        # We can get Datasets with listChildren, since we have the Project already.
        # Or conn.getObjects("Dataset", opts={'project', id}) if we have Project ID
        for dataset in project.listChildren():
            print_obj(dataset, 2)
            for image in dataset.listChildren():
                # my_exp_id = conn.getUser().getId()
                # images = conn.getObjects("Image", attributes={"name":"row2_col1.tiff"})
                # for image in images:
                print_obj(image)
                print(" X:", image.getSizeX())
                print(" Y:", image.getSizeY())
                print(" Z:", image.getSizeZ())
                print(" C:", image.getSizeC())
                print(" T:", image.getSizeT())
                # List Channels (loads the Rendering settings to get channel colors)
                for channel in image.getChannels():
                    print('Channel:', channel.getLabel())
                    print('Color:', channel.getColor().getRGB())
                    print('Lookup table:', channel.getLut())
                    print('Is reverse intensity?', channel.isReverseIntensity())
                pixels = image.getPrimaryPixels()
                plane = pixels.getPlane(0, 0, 0)
                plt.imshow(plane, cmap='gray')
                plt.title(f"Image ID: {image.getId()}, Name: {image.getName()}")
                plt.axis('off')  # Hide axes
                plt.show()

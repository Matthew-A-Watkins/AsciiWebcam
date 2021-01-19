import PIL.Image
from PIL import ImageDraw
from os import system, name
from time import sleep
import cv2
import pyvirtualcam
import numpy
import numba


ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

# rezise image with new width
def rezise_image(image, new_width=150, ):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

# convert to greyscale
def grayimage(image):
    grayscale_image = image.convert("L")
    return grayscale_image

# convert pixels to a string of Ascii characters
def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel//25] for pixel in pixels])
    return characters

def save_text_to_image(text_to_convert, image, new_width=150):

    # make an image with the same dimensions
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)

    # multiply by pixel of character with added room for error
    new_width = (new_width*6)+20
    new_height *= 15

    # set back ground color to black
    black = (0, 0, 0)
    img = PIL.Image.new('RGB', (new_width, new_height), color = black)

    # text color at white and full opacity
    white = (255, 255, 255, 255)

    draw = ImageDraw.Draw(img)
    draw.text((10,60), str(text_to_convert), fill=(white))

    # remove pesky black at the top of the screen and borders a tad
    x = 20
    y = 60
    w = new_width-x
    h = new_height-y
    im = img.crop((x,y,w,h))

    # makes the image webcam friendly
    final_image = im.resize((1280,720))
    return(numpy.array(final_image))

def main(new_width=150, count=0):
    with pyvirtualcam.Camera(width=1280, height=720, fps=30) as cam:
        vidcap = cv2.VideoCapture(0)
        success,image = vidcap.read()
        while success:
            image = PIL.Image.fromarray(image)
            
            # convert image to ascii
            new_image_data = pixels_to_ascii(grayimage(rezise_image(image)))

            # format
            pixel_count = len(new_image_data)
            ascii_image = "\n".join(new_image_data[i:(i+new_width)] for i in range(0, pixel_count, new_width))

            # draw new image and send it to obs for camera
            rgba = cv2.cvtColor(save_text_to_image(ascii_image, image), cv2.COLOR_BGR2RGBA)
            cam.send(rgba)

            # retrieve image info
            success,image = vidcap.read()
            count+=1

    


if __name__ == "__main__":
    main()

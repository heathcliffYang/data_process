"""
Some operation to produce background images
"""
import random

def random_crop_rectangle(image):
    h, w, c = image.shape
    if w < 192*2 or h < 96*2:
        return None

    x1 = random.randint(0, w-192)
    x2 = random.randint(x1+20, w-1)

    y1 = random.randint(0, h-96)
    y2 = random.randint(y1+10, h-1)

    return image[y1:y2, x1:x2, :]

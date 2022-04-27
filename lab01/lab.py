#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!

def get_width(image):
    """
    Extracts the width from the given image

    Parameters:
      * image (dict) : contains the height, width, and a 1D
            list of pixels of an image
    Returns:
      An integer representing the width of the image in pixels
    """
    return image['width']

def get_height(image):
    """
    Extracts the height from the given image

    Parameters:
      * image (dict) : contains the height, width, and a 1D
            list of pixels of an image
    Returns:
      An integer representing the height of the image in pixels
    """
    return image['height']

def get_pixel(image, x, y):
    """
    Retrieves the value of a pixel at location (x,y) in the image

    Parameters:
      * image (dict) : contains the height, width, and a 1D
            list of pixels of an image
      * x (int) : the x value of the desired pixel
      * y (int) : the y value of the desired pixel
    Returns:
      An integer or float representing the value of the pixel at the specified
      index
    """
    index = y*get_width(image) + x
    return image['pixels'][index]


def set_pixel(image, x, y, c):
    """
    Modifies the value of a pixel at location (x,y) in the image in place

    Parameters:
      * image (dict) : contains the height, width, and a 1D
            list of pixels of an image
      * x (int) : the x value of the desired pixel
      * y (int) : the y value of the desired pixel
      * c (int) : the color value to set the pixel to
    """
    index = y*get_width(image) + x
    image['pixels'][index] = c


def apply_per_pixel(image, func):
    """
    Applies some function to the value of each pixel in the image

    Parameters:
      * image (dict) : contains the height, width, and a 1D
            list of pixels of an image
      * func (func) : the function to be applied over each pixel
    Returns:
      A new image with the function applied
    """
    result = {'height': image['height'],
            'width': image['width'],
            'pixels': image['pixels'][:]
    }
    for y in range(image['height']):
        for x in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    """
    Reverses the grayscale value of each pixel
    """
    return apply_per_pixel(image, lambda c: 255-c)

def scaled(image, n):
    """
    Multiplies the grayscale value of each pixel by n
    """
    return apply_per_pixel(image, lambda c: c*n)

def get_pixel_new(image, x, y, boundary_behavior=None):
    """
    Modified version of get_pixel that includes settings for various boundary
    behaviors

    Parameters:
      * image (dict) : contains the height, width, and a 1D
            list of pixels of an image
      * x (int) : the x value of the desired pixel
      * y (int) : the y value of the desired pixel
      * boundary_behavior (string) : the boundary behavior setting
          * 'zero' : treats all out-of-bounds pixels as 0
          * 'extend' : uses value of in-bounds pixel on edge or corner along
                same row or column
          * 'wrap': uses the value of tiled image

    Returns:
      An integer or float representing the value of the pixel at the specified
      index
    """
    width = get_width(image)
    height = get_height(image)

    if boundary_behavior == "zero":
        if not ((0 <= x < width) and (0 <= y < height)):
            return 0
    elif boundary_behavior == "extend": # if x or y out of bounds, clip
        if x < 0:
            x = 0
        elif x >= width:
            x = width-1

        if y < 0:
            y = 0
        elif y >= height:
            y = height-1
    elif boundary_behavior == "wrap":
        x = x % width
        y = y % height

    return image['pixels'][y*width + x]

def pixel_list_to_img(image, pix_lst):
    """
    Converts list of pixels to image dictionary
    """
    return {'height': image['height'], 'width': image['width'], 'pixels': pix_lst}

# HELPER FUNCTIONS

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    kernel is represented as a 2D list, e.g. [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    where each nested list is a row.
    """

    if boundary_behavior not in ("zero", "extend", "wrap"):
        return None

    img_width = image['width']
    img_height = image['height']

    kernel_size = len(kernel) # kernel is square so true for height and width
    k_range = int(kernel_size / 2) # distance from center of kernel to edge

    new_img = []

    for y in range(img_height):
        for x in range(img_width):
            pixel_sum = 0

            # gets values of pixels around pixel (x,y) moving from
            # the top left corner (x-k_range, y-k_range) ->
            # bottom right corner (x+kernel_size-k_range) == (x+k_range)

            for kern_y in range(kernel_size):
                for kern_x in range(kernel_size):
                    pix = get_pixel_new(image, x+kern_x-k_range,
                        y+kern_y-k_range, boundary_behavior)
                    scale_factor = kernel[kern_y][kern_x]
                    pixel_sum += pix*scale_factor
            new_img.append(pixel_sum)

    return pixel_list_to_img(image, new_img)
    # return {'height': img_height, 'width': img_width, 'pixels': new_img}



def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """

    rounded = []
    for pixel in image['pixels']:
        pixel = round(pixel)
        if pixel < 0:
            pixel = 0
        if pixel > 255:
            pixel = 255
        rounded.append(pixel)
    return pixel_list_to_img(image, rounded)
    # return {'height': image['height'], 'width': image['width'], 'pixels': rounded}

# FILTERS

def create_blur_kernel(n):
    """
    Creates an nxn kernel with items summing to 1

    Parameters:
      * n (int) : the size of the kernel
    Returns:
      An nxn normalized 2D list
    """
    kernel = []
    for y in range(n):
        row = [1/n**2]*n
        kernel.append(row)
    return kernel

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    Uses 'extend' boundary behavior.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = create_blur_kernel(n)

    # then compute the correlation of the input image with that kernel using
    # the 'extend' behavior for out-of-bounds pixels
    output = correlate(image, kernel, 'extend')

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    rounded = round_and_clip_image(output)

    return rounded

def sharpened(image, n):
    """
    Return a new image representing the result of applying an unsharp filter (with
    kernel size n) to the given input image.

    Scales the image by 2 and subtracts a box blur. Uses 'extend' boundary
    behavior.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    blur_kernel = create_blur_kernel(n)
    blurred = correlate(image, blur_kernel, 'extend')

    scaled_img = scaled(image, 2)

    sharpened = []
    for i, b in zip(scaled_img['pixels'], blurred['pixels']):
        sharpened.append(i-b)

    sharp_img = pixel_list_to_img(image, sharpened)
    rounded = round_and_clip_image(sharp_img)

    return rounded

def edges(image):
    """
    Return a new image representing the result of applying an edge detection filter
    to the given input image.

    Uses 'extend' boundary behavior.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    Kx = [[-1, 0, 1],
          [-2, 0, 2],
          [-1, 0, 1]]
    Ky = [[-1, -2, -1],
          [0,  0,  0],
          [1,  2,  1]]

    Ox = correlate(image, Kx, 'extend')
    Oy = correlate(image, Ky, 'extend')

    Oxy = []

    # Applies edge detection equation sqrt(x^2+y^2)
    for x, y in zip(Ox['pixels'], Oy['pixels']):
        Oxy.append(round(math.sqrt(x**2 + y**2)))

    Oxy_img = pixel_list_to_img(image, Oxy)
    rounded = round_and_clip_image(Oxy_img)

    return rounded


# COLOR FILTERS

def split_to_grayscale(image):
    """
    Takes an RGB image and returns 3 grayscale images

    Parameters:
      * image (dict) : the RGB image
    Returns:
      3 grayscale images, each representing a color layer
    """
    red_layer = []
    green_layer = []
    blue_layer = []

    for r, g, b in image['pixels']:
        red_layer.append(r)
        green_layer.append(g)
        blue_layer.append(b)
    return pixel_list_to_img(image, red_layer), \
        pixel_list_to_img(image, green_layer), \
        pixel_list_to_img(image, blue_layer)

def merge_to_color(red_layer, green_layer, blue_layer):
    """
    Merges 3 grayscale images into one RGB image
    """
    combined = zip(red_layer['pixels'], green_layer['pixels'], blue_layer['pixels'])
    return pixel_list_to_img(red_layer, list(combined))

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_filt(image):
        red, green, blue = split_to_grayscale(image)
        r_processed = filt(red)
        g_processed = filt(green)
        b_processed = filt(blue)
        return merge_to_color(r_processed, g_processed, b_processed)
    return color_filt


def make_blur_filter(n):
    """
    Given a kernel size n, returns a function that takes a grayscale image
    as input and produces a blurred image blurred with kernel size n.
    """
    def blur(image):
        return blurred(image, n)
    return blur


def make_sharpen_filter(n):
    """
    Given a kernel size n, returns a function that takes a grayscale image
    as input and produces a sharpened image blurred with kernel size n.
    """
    def sharp(image):
        return sharpened(image, n)
    return sharp

def color_scale_filter(r=1, g=1, b=1):
    """
    Given three color values, returns a function that takes an RGB image
    as input and returns an RGB image with its layers scaled by the parameters
    """
    def scale(image):
        assert type(image['pixels'][0]) == tuple
        red, green, blue = split_to_grayscale(image)

        scaled_red = round_and_clip_image(scaled(red, r))
        scaled_green = round_and_clip_image(scaled(green, g))
        scaled_blue = round_and_clip_image(scaled(blue, b))

        return merge_to_color(scaled_red, scaled_green, scaled_blue)
    return scale


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def all_filter(image):
        nested_filters = image
        for filt in filters:
            nested_filters = filt(nested_filters)
        return nested_filters
    return all_filter



# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    kernel = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    # img = load_greyscale_image('test_images/construct.png')
    # save_greyscale_image(blurred(img, 13, 'extend'), 'cat_blurred_extend.png')
    # save_greyscale_image(blurred(img, 13, 'wrap'), 'cat_blurred_wrap.png')
    # save_greyscale_image(blurred(img, 13, 'zero'), 'cat_blurred_zero.png')
    # save_greyscale_image(sharpened(img, 11), 'python_sharpened.png')
    #save_greyscale_image(edges(img), 'construct_edges.png')

    # img = load_color_image('test_images/frog.png')

    # color_inverted = color_filter_from_greyscale_filter(inverted)
    # color_blur = color_filter_from_greyscale_filter(make_blur_filter(9))
    # color_sharpen = make_sharpen_filter(7)

    # save_color_image(color_blur(img), 'python_blurred_color.png')

    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # #
    # img = load_color_image('test_images/frog.png')
    # #
    # save_color_image(filt(img), 'frog_cascade.png')

    color_filter = color_scale_filter(2,0.3,2)
    img = load_color_image('test_images/frog.png')
    save_color_image(color_filter(img), 'frog_red.png')

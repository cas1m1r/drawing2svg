import matplotlib.pyplot as plt
import scipy.ndimage as ndi
import drawsvg as draw
import numpy as np
import sys
import os

TEST_IMG = 'test.png'
BIT_MAX = np.power(2, 8)


def load_image(filename: str):
    if not os.path.isfile(filename):
        print(f'[!] Cannot find {filename}')
        exit()
    return np.array(plt.imread(filename))


def im2svg(filename: str):
    # load image file in as array of number
    img = load_image(filename)
    # figure out array data type
    pxl_style = img.dtype
    # if floats convert to int16
    if pxl_style in [np.float32, np.float16]:
        img = img * BIT_MAX

    # TODO: detect lines
    rch = img[:, :, 0]
    gch = img[:, :, 1]
    bch = img[:, :, 2]
    rmean = rch.mean()
    gmean = gch.mean()
    bmean = bch.mean()
    rmax = rch.max()
    gmax = gch.max()
    bmax = bch.max()

    rdiff = rmax - rmean
    gdiff = gmax - gmean
    bdiff = bmax - bmean
    means = {0: rdiff, 1: gdiff, 2: bdiff}
    diffs = [rdiff, gdiff, bdiff]
    inds = {0: 'red', 1: 'green', 2: 'blue'}
    channel_max_i = int(np.where(np.max(diffs) == diffs)[0][0])
    best_channel = inds[channel_max_i]
    print(f'[+] Using {best_channel} for image processing. Appears to have best Signal to noise')
    # find coordinates of lines
    arr = img[:, :, channel_max_i]
    glap = ndi.gaussian_laplace(arr - means[channel_max_i], 3.3)
    [x,y] = np.where(glap > glap.max()*0.11)
    # create svg
    return make_svg(x,y, arr)


def make_svg(lx,ly, img):
    hex_color = '014532'
    dims = img.shape
    d = draw.Drawing(dims[1], dims[0], origin=(0,0))
    d.set_pixel_scale(2)
    command_end = f"fill='#{hex_color}',stroke_width='1',stroke='black'))"
    # dynamically build the command for drawing the line
    n_points = len(lx)
    for i in range(n_points):
        x = lx[i]
        y = ly[i]
        command_head = 'd.append(draw.Circle(' + f'{y},{x},1,'
        exec(command_head+command_end)
    return d


def usage():
    print('Incorrect Usage')
    print(f'Usage: {sys.argv[0]} <image-file>')
    exit()


def main():
    real_image = ''
    if len(sys.argv) > 1:
        real_image = sys.argv[1]
    elif TEST_IMG != '':
        real_image = TEST_IMG
    else:
        usage()
    # Convert it
    svg = im2svg(real_image)
    svg.save_svg('result.svg')


if __name__ == '__main__':
    main()

from PIL import Image
import numpy as np
import colorsys
import math, cmath

MOD_BRIGHTNESS_BY_POWERS_OF_TWO = True

height = 500
width = 500

xMin = -5
xMax = 5
yMin = -5
yMax = 5

def func_to_test(z: complex):
    # return z
    # return (3*z+5)/(-4*z+1)
    # return z ** 2
    # return 0 if z == 0 else 1/z
    return cmath.cos(complex(z.imag, z.real)) + cmath.sin(z)
    # return 0 if z == 0 else cmath.log(z)
    # return cmath.cosh(z) + cmath.tanh(z)

def write_to_file(filename: str):
    angles = np.empty((height, width), dtype=np.float32)
    magnitudes = np.empty((height, width), dtype=np.float32)

    # For each pixel,
    for x in range(height):
        for y in range(width):
            xVal = xMin + (x/height)*(xMax-xMin)
            yVal = yMin + (y/width)*(yMax-yMin)

            function_output = func_to_test(complex(xVal, yVal))

            # Convert to polar
            r, theta = cmath.polar(function_output)
            theta += cmath.pi # add pi to make all values positive
            # r = math.sqrt(function_output.real ** 2 + function_output.imag ** 2)
            # theta = math.atan2(function_output.imag, function_output.real) + math.pi # add pi to make all values positive

            angles[x][y] = theta
            magnitudes[x][y] = r

    maxMagnitude = np.max(magnitudes)

    imageData = np.empty((height, width, 3), dtype=np.uint8)

    for x in range(height):
        for y in range(width):
            hue = angles[x][y] / (2*math.pi)
            lightness = magnitudes[x][y] / maxMagnitude

            if MOD_BRIGHTNESS_BY_POWERS_OF_TWO and lightness != 0:
                lb = 2 ** math.floor(math.log2(lightness))
                ub = 2 ** (math.ceil(math.log2(lightness)))
                if lb != ub: frac = (lightness-lb)/(ub-lb)
                else: frac = 1

                # We don't actually want brightness to go from 0 to 1, because it's ugly, so we have the fraction determine 0.7 of the color, with 0.3 always on
                lightness = (frac * 0.7) + 0.3

            saturation = 1

            # TODO: normalize input so it's in the right domain
            # https://docs.python.org/3/library/colorsys.html
            # Ex: atan is -pi/2 to pi/2, we change it to 0 to pi, but needs to be 0 to 1?

            # might need to be hls_to_rgb?
            r,g,b = colorsys.hsv_to_rgb(hue, saturation, lightness)

            imageData[x][y][0] = int(r * 255)
            imageData[x][y][1] = int(g * 255)
            imageData[x][y][2] = int(b * 255)

    img_arr = np.array(imageData, dtype=np.uint8)
    new_img = Image.fromarray(img_arr)
    new_img.save(filename)
    print(f"Saved as {filename}")

if __name__ == '__main__':
    fname = input("Input filename:\n>>> ")
    write_to_file(fname)
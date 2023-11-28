from PIL import Image
import numpy as np
import colorsys
import math, cmath
import time

MOD_BRIGHTNESS_BY_POWERS_OF_TWO = True
CHECKERBOARD = False
CHECKERBOARD_WIDTH = 0.1

height = 900
width = 1600

xMin = -1
xMax = 1
yMin = -1.7777777
yMax = 1.7777777

def func_to_test(z: complex):
    # z = z * complex(0,1) # Rotate 90°
    # return z
    # return (3*z+5)/(-4*z+1)
    # return (3*z+1)/(3*z-1)
    # return z ** 2
    # return 0 if z == 0 else 1/z
    return cmath.cos(complex(z.imag, z.real)) + cmath.sin(z)
    # return 0 if z == 0 else cmath.log(z)
    # return cmath.cosh(z) + cmath.tanh(z)

def write_to_file(filename: str):
    angles = np.empty((height, width), dtype=np.float32)
    magnitudes = np.empty((height, width), dtype=np.float32)

    if CHECKERBOARD: gridLines = np.zeros((height, width), dtype=np.bool_)

    math_total_time = 0

    # For each pixel,
    for x in range(width):
        for y in range(height):
            xVal = xMin + (x/width)*(xMax-xMin)
            yVal = yMin + (y/height)*(yMax-yMin)

            start = time.time()
            function_output = func_to_test(complex(xVal, yVal))
            end = time.time()

            math_total_time += end - start

            if CHECKERBOARD and (function_output.real % (2*CHECKERBOARD_WIDTH) < CHECKERBOARD_WIDTH) != (function_output.imag % (2*CHECKERBOARD_WIDTH) < CHECKERBOARD_WIDTH):
                gridLines[x][y] = True

            # Convert to polar
            r, theta = cmath.polar(function_output)
            theta += cmath.pi # add pi to make all values positive
            # r = math.sqrt(function_output.real ** 2 + function_output.imag ** 2)
            # theta = math.atan2(function_output.imag, function_output.real) + math.pi # add pi to make all values positive

            angles[x][y] = theta
            magnitudes[x][y] = r

    maxMagnitude = np.max(magnitudes)

    print(f"Computation complete, total function time: {math_total_time}s")

    imageData = np.empty((height, width, 3), dtype=np.uint8)

    rendering_start = time.time()

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

            if CHECKERBOARD and gridLines[x][y]:
                lightness *= 0.7

            saturation = 1

            imageData[x][y][0] = int(hue * 255)
            imageData[x][y][1] = int(saturation * 255) # always 255
            imageData[x][y][2] = int(lightness * 255)

    rendering_end = time.time()
    print(f"Rendered in {rendering_end - rendering_start}s")

    img_arr = np.array(imageData, dtype=np.uint8)
    new_img = Image.fromarray(img_arr, mode="HSV")

    convert_start = time.time()
    new_img = new_img.convert("RGB")
    convert_end = time.time()
    print(f"HSV to RGB conversion in {convert_end - convert_start}s")


    new_img.save(filename)
    print(f"Saved as {filename}")

if __name__ == '__main__':
    fname = input("Input filename:\n>>> ")
    if "." not in fname:
        fname += ".png"

    write_to_file(fname)
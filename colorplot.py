import argparse
from PIL import Image
import numpy as np
from numpy import sin, cos, tan, sinh, cosh, tanh, log, exp
from math import pi as PI
import time
from test_funcs.funcs import *

DEFAULT_WINDOW = (-1, 1, -1, 1)

argParse = argparse.ArgumentParser()

argParse.add_argument("-dim", "--dimensions", type=int, nargs=2, default=(400, 400), help="Set the image dimensions. Default=%(default)s")

argParse.add_argument("-xMin", "--xMin", type=float, default=-1, help="Set one viewing window dimension. Default=%(default)s")
argParse.add_argument("-xMax", "--xMax", type=float, default=1, help="Set one viewing window dimension. Default=%(default)s")
argParse.add_argument("-yMin", "--yMin", type=float, default=-1, help="Set one viewing window dimension. Default=%(default)s")
argParse.add_argument("-yMax", "--yMax", type=float, default=1, help="Set one viewing window dimension. Default=%(default)s")

argParse.add_argument("-w", "--window", type=float, nargs=4, dest='window', metavar=('xMin', 'xMax', 'yMin', 'yMax'), help=f"Set the viewing window dimensions. Overrides -xMin, -xMax, -yMin, -yMax if they are set. Default={DEFAULT_WINDOW}")

function = argParse.add_mutually_exclusive_group()
function.add_argument("-f1", "--func:test1", dest='function', action='store_const', const='test1', help="Test function 1: f(z)=z (identity)")
function.add_argument("-f2", "--func:test2", dest='function', action='store_const', const='test2', help="Test function 2: f(z)=z^2")
function.add_argument("-f3", "--func:test3", dest='function', action='store_const', const='test3', help="Test function 3: f(z)=(3z+5)/(-4z+1)")
function.add_argument("-f4", "--func:test4", dest='function', action='store_const', const='test4', help="Test function 4: f(z)=(3z+1)/(3z-1)")
function.add_argument("-f5", "--func:test5", dest='function', action='store_const', const='test5', help="Test function 5: f(z)=1/z if z!=0, 0 otherwise")
function.add_argument("-f6", "--func:test6", dest='function', action='store_const', const='test6', help="Test function 6: f(z)=cos(1j * conj(z)) + sin(z)")
function.add_argument("-f7", "--func:test7", dest='function', action='store_const', const='test7', help="Test function 7: f(z)=log(z) if z!=0, 0 otherwise")
function.add_argument("-f8", "--func:test8", dest='function', action='store_const', const='test8', help="Test function 8: f(z)=cosh(z) + tanh(z)")

function.add_argument("-fs", "--func:specify", dest='function', action='store_const', const='SPECIFY', default="SPECIFY", help="You will be prompted to enter a function. The variable is 'z'. Select NumPy functions (sin(), log(), etc) are available with no namespace required.")

checkerboard = argParse.add_mutually_exclusive_group()
checkerboard.add_argument("-c", "--checkerboard-width", type=float, default=0.1, help="Set the width of the checkerboard pattern. Default=%(default)s")
checkerboard.add_argument("-x", "--checkerboard-off", action='store_true', default=False, help="Turn off the checkerboard pattern.")

brightness = argParse.add_mutually_exclusive_group()
brightness.add_argument("-b", "--brightness-log-modulus", action='store_true', dest='mod_brightness', default=True, help="Use the base-2 log of the complex number as the brightness. On by default.")
brightness.add_argument("-s", "--simple", action='store_false', default=False, dest='mod_brightness', help="Use the modulus of the complex number, as a fraction of the maximum modulus in the viewing window, as the brightness. Off by default.")

argParse.add_argument("-o", "--output", type=str, default="", help="Name of output file.")
argParse.add_argument("-p", "--preview", action='store_true', help="Show the image in a window.")

args = argParse.parse_args()

MOD_BRIGHTNESS_BY_POWERS_OF_TWO = args.mod_brightness
CHECKERBOARD = not args.checkerboard_off
CHECKERBOARD_WIDTH = args.checkerboard_width

height = args.dimensions[1]
width = args.dimensions[0]

if args.window: xMin, xMax, yMin, yMax = args.window
else:
    if args.xMin: xMin = args.xMin
    else: xMin = DEFAULT_WINDOW[0]

    if args.xMax: xMax = args.xMax
    else: xMax = DEFAULT_WINDOW[1]

    if args.yMin: yMin = args.yMin
    else: yMin = DEFAULT_WINDOW[2]

    if args.yMax: yMax = args.yMax
    else: yMax = DEFAULT_WINDOW[3]

def make_func(func: str):
    match func:
        case 'test1':
            return func_to_test1
        case 'test2':
            return func_to_test2
        case 'test3':
            return func_to_test3
        case 'test4':
            return func_to_test4
        case 'test5':
            return func_to_test5
        case 'test6':
            return func_to_test6
        case 'test7':
            return func_to_test7
        case 'test8':
            return func_to_test8
        case 'SPECIFY' | _:
            f = input("Enter function:\n>>> ")
            return lambda z: eval(f)

def create_img(func_to_test) -> Image:
    math_start = time.time()

    x_in = np.linspace(xMin, xMax, num=width)
    y_in = np.linspace(yMin, yMax, num=height)
    x_grid, y_grid = np.meshgrid(x_in, y_in)

    inputs = x_grid + 1j * y_grid

    function_output = func_to_test(inputs)

    angles = np.angle(function_output)
    magnitudes = np.abs(function_output)

    if CHECKERBOARD: gridDarkened = np.where(
        (function_output.real % (2*CHECKERBOARD_WIDTH) < CHECKERBOARD_WIDTH) != (function_output.imag % (2*CHECKERBOARD_WIDTH) < CHECKERBOARD_WIDTH),
        True, False
    )
        
    math_end = time.time()

    print(f"Computation complete in {math_end - math_start}s")

    # Note that PIL images have shape transposed! (height,width) rather than (width,height), as you would expect from an x,y array
    imageData = np.empty((height, width, 3), dtype=np.uint8)

    rendering_start = time.time()

    hues = (255 * angles / (2*PI)).astype(np.uint8)
    lightnesses = magnitudes

    if MOD_BRIGHTNESS_BY_POWERS_OF_TWO:
        lb = 2 ** np.floor(np.log2(lightnesses))
        ub = 2 ** (np.ceil(np.log2(lightnesses)))

        frac = np.where(
            lightnesses != 0,
            (lightnesses - lb) / (ub - lb),
            1
        )

        # We don't actually want brightness to go from 0 to 1, because it's ugly, so we have the fraction determine 0.7 of the color, with 0.3 always on
        lightnesses = (frac * 0.7) + 0.3
    else:
        # If *not* scaling by log of modulus, scale so that maximum modulus is maximum brightness (1)
        max_mod = np.max(lightnesses)
        print(max_mod)
        lightnesses = lightnesses / max_mod

    if CHECKERBOARD: lightnesses = np.where(gridDarkened, lightnesses * 0.7, lightnesses)

    lightnesses = (lightnesses * 255).astype(np.uint8)

    saturations = np.full((height, width), 255, dtype=np.uint8)

    imageData = np.stack((hues, saturations, lightnesses), axis=-1)

    rendering_end = time.time()
    print(f"Rendered in {rendering_end - rendering_start}s")

    img_arr = np.array(imageData, dtype=np.uint8)
    new_img = Image.fromarray(img_arr, mode="HSV")

    convert_start = time.time()
    new_img = new_img.convert("RGB")
    convert_end = time.time()
    print(f"HSV to RGB conversion in {convert_end - convert_start}s")

    # new_img.save(filename)
    # print(f"Saved as {filename}")
    new_img.show()

if __name__ == '__main__':
    func_to_test = make_func(args.function)

    img = create_img(func_to_test)

    if args.preview:
        img.show()
    if args.output != "":
        img.save(args.output)
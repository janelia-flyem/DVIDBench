#!/usr/bin/env python

# Idea cribbed from this stackoverflow post:
# http://stackoverflow.com/questions/15261851/100x100-image-with-random-pixel-colour

from PIL import Image, ImageDraw, ImageFont
import numpy
import io

def generate_tiles(outfile, num=1, dimensions=512):
    # create the random noise that will be used as the seed for the image.
    imarray = numpy.random.rand(dimensions,dimensions,3) * 255

    # create the image from the above array.
    im = Image.fromarray(imarray.astype('uint8')).convert('L') # L (8-bit pixels, black and white)

    # get a drawing context
    draw = ImageDraw.Draw(im)

    # get the font
    fnt = ImageFont.truetype('SourceCodePro-Bold.otf', 40)

    # add a number to the image.
    draw.text([x / 2 for x in im.size], "%s" % num, font=fnt, fill=(1,1,1))

    if outfile:
        im.save(outfile)
    else:
        b = io.BytesIO()
        im.save(b, 'PNG')
        return b.getvalue()


if __name__ == "__main__":
    import argparse
    import sys

    # get options from the command line
    parser = argparse.ArgumentParser(description='Generate random tiles.')

    parser.add_argument('-o', '--out', metavar='filename.png')
    parser.add_argument('-n', '--num', metavar='n', default=1, type=int)
    parser.add_argument('-d', '--dim', metavar='n', default=512, type=int)

    args = parser.parse_args()

    data = generate_tiles(args.out, args.num, args.dim)

    if data:
        sys.stdout.write(data)




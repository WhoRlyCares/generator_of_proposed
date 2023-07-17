import png
#from PIL import Image
import svgwrite
from svgwrite import cm,mm
#import pyvips

class PngStatics:
    pallete =[]
    @staticmethod
    def cname_to_l(cname=str):
        pass

class PngExamples:
    @staticmethod
    def cells(fpath="./output/cells.png", w=320, h=320):
        fh = open(fpath, 'wb')
        fh.close()

    @staticmethod
    def gradient(fpath="./output/gradient.png", width = 255,height = 255):
        img = []
        for y in range(height):
            row = ()
            for x in range(width):
                row = row + (x, max(0, 255 - x - y), y)
            img.append(row)
        with open(fpath, 'wb') as f:
            w = png.Writer(width, height, greyscale=False)
            w.write(f, img)

    @staticmethod
    def from_binary(fpath="./output/fromb.png"):
        s = ['110010010011',
             '101011010100',
             '110010110101',
             '100010010011']
        s = [[int(c) for c in row] for row in s]

        w = png.Writer(len(s[0]), len(s), greyscale=True, bitdepth=1)
        f = open(fpath, 'wb')
        w.write(f, s)
        f.close()

    @staticmethod
    def swatch(fpath="./output/swatch.png"):
        p = [(255, 0, 0, 0, 255, 0, 0, 0, 255),
             (128, 0, 0, 0, 128, 0, 0, 0, 128)]
        f = open(fpath, 'wb')
        w = png.Writer(3, 2, greyscale=False)
        w.write(f, p)
        f.close()

class SvgWrEx:
    def __init__(self):
        dwg = svgwrite.Drawing('test.svg', profile='tiny')
        dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
        dwg.add(dwg.text('Test', insert=(0, 0.2), fill='red'))
        dwg.save()
    def rect_ex(self):
        dwg = svgwrite.Drawing('square.svg')
        red = dwg.add(dwg.rect((10, 10), (10, 10), fill='red'))
        square = dwg.add(dwg.rect((30, 30), (10, 10), fill='blue'))
        dwg.save()

    def basic_shapes(self,name, pos={'x':5,'y':5}, rsize={'w':40, 'h':25}, fill_color='purple'):
        dwg = svgwrite.Drawing(filename=name, debug=True)
        hlines = dwg.add(dwg.g(id='hlines', stroke='green'))
        for y in range(20):
            hlines.add(dwg.line(start=(0 * cm, (0 + y) * cm), end=(20 * cm, (0 + y) * cm)))

        vlines = dwg.add(dwg.g(id='vline', stroke='blue'))
        for x in range(20):
            vlines.add(dwg.line(start=((0 + x) * cm, 0 * cm), end=((0 + x) * cm, 20 * cm)))

        shapes = dwg.add(dwg.g(id='shapes', fill='red'))
        # override the 'fill' attribute of the parent group 'shapes'
        shapes.add(dwg.rect(insert=(pos['x'] * cm, pos['y'] * cm), size=(rsize['w'] * mm, rsize['h'] * mm),
                            fill=fill_color, stroke='black', stroke_width=3))
        dwg.save()





if __name__=="__main__":
    pass
    #PngExamples.gradient()
    #PngExamples.from_binary()
    #PngExamples.swatch()
    #pilex = PilExamples()
    #pilex.save()
    #swe = SvgWrEx()
    #swe.rect_ex()
    #swe.basic_shapes("shapes.svg")
    #swe.basic_shapes("t1.svg", {'x':7,'y':10},{'w':20, 'h':65})
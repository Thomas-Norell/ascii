import PIL.Image
import PIL.ImageFont
import PIL.ImageOps
import PIL.ImageDraw
import imageio
from numpy import array
class art:
    def __init__(self, source, dest, size = None, catalog = """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. """):
        self.source = source
        self.dest = dest
        self.size = size
        self.catalog_to_dict(catalog)
        if source.endswith('.gif'):
            self.type = 'gif'
        elif source.endswith('.jpg') or source.endswith('.jpeg') or source.endswith('.png'):
            self.type = 'image'
        else:
            raise Exception("Incompatible media type. Please ensure extension is .gif, .jpeg, .jpg, or .png")

    #Takes in (ordered) list of ASCII characters and sets up dictionary
    def catalog_to_dict(self, cat):
        self.data_dict = {}
        count = 0
        for char in cat:
            self.data_dict[count] = char
            count += 1

    #Given RGB tuple, return appropriate ASCII character
    def get_char(self, pixel_rgb):
        intensity = pixel_rgb[0] + pixel_rgb[1] + pixel_rgb[2]
        #765 = 255 * 3
        intensity = int(intensity / 765 * (len(self.data_dict)-1))
        return self.data_dict[intensity]

    #Write ASCII text to destination
    def write_image(self, dir = None):
        if dir == None:
            dir = self.source
        if (dir == self.source and self.type == 'gif'):
            print("This method is meant for images. Using make_gif...")
            self.make_gif()
            return
        try:
            im = PIL.Image.open(dir)
            out = open(self.dest, "w")
        except FileNotFoundError:
            raise Exception("Directory not found! Did you specify the correct path?")


        while im.size[0] * im.size[1] > 500000: #this is thie biggest image we'll allow
            im = im.resize((int(im.size[0] * .9), int(im.size[1] * .9))) #reduce until we hit target

        for column in range(im.size[1]):
            for row in range(im.size[0]):
                char = self.get_char(im.getpixel((row, column)))
                out.write(char)
            out.write("\n")
        #Now have a text file. Need to convert to Image.
        out.close()

        # some of the following is adapted from https://gist.github.com/Mego/802d33a14a33964b24dd


        # parse the file into lines
        with open(self.dest) as text_file:  # can throw FileNotFoundError
            lines = tuple(l.rstrip() for l in text_file.readlines())

        # choose a font (you can see more detail in my library on github)
        font = PIL.ImageFont.load_default()

        # make the background image based on the combination of font and lines
        pt2px = lambda pt: int(round(pt * 96.0 / 72))  # convert points to pixels
        max_width_line = max(lines, key=lambda s: font.getsize(s)[0])
        # max height is adjusted down because it's too large visually for spacing
        test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        max_height = pt2px(font.getsize(test_string)[1])
        max_width = pt2px(font.getsize(max_width_line)[0])
        height = max_height * len(lines)  # perfect or a little oversized
        width = int(round(max_width + 40))  # a little oversized
        image = PIL.Image.new("L", (width, height), color=255)
        draw = PIL.ImageDraw.Draw(image)

        # draw each line of text
        vertical_position = 5
        horizontal_position = 5
        line_spacing = int(round(max_height * 0.8))  # reduced spacing seems better
        for line in lines:
            draw.text((horizontal_position, vertical_position),
                      line, fill=0, font=font)
            vertical_position += line_spacing
        # crop the text
        c_box = PIL.ImageOps.invert(image).getbbox()
        image = image.crop(c_box)

        #need to resize image to original aspect ratio
        correct_ratio = im.size[0]/im.size[1] # with/height
        if im.size[0] >= im.size[1]: #with > height, so we turn down width
            image = image.resize((int(image.size[1] * correct_ratio), image.size[1]))
        else: #height > width, so we turn down the height

            image = image.resize((int((correct_ratio * image.size[0])),image.size[0]))

        if self.size:
            image = image.resize(self.size)
        image.save(self.dest)




        return image

    def make_gif(self):
        images = []
        im = PIL.Image.open(self.source)
        try:
            while True:
                new_frame = im.convert('RGB')
                new_frame.save(self.dest, 'PNG')
                asciiframe = self.write_image(self.dest)
                images.append(array(asciiframe))
                im.seek(im.tell()+1)
        except EOFError:
            pass
        imageio.mimsave(self.dest, images)

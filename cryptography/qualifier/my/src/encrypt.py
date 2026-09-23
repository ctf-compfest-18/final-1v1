from PIL import Image


ROUNDS = 7
KEY = [[1280137, 1024046], [1536091, 1228873]]
IV = [73, 201]


def shuffle(img):
    shuffled = img.copy()

    for _ in range(ROUNDS):
        next_img = Image.new("L", img.size)
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                x_new = (x + 67 * y) % img.size[0]
                y_new = (76 * x + 5093 * y) % img.size[1]
                next_img.putpixel((x_new, y_new), shuffled.getpixel((x, y)))
        shuffled = next_img

    return shuffled


def encrypt(input_path, output_path):
    img = Image.open(input_path).convert("L")
    pixel = list(shuffle(img).getdata())
    enc_pixel = []
    prev = IV

    for i in range(0, len(pixel), 2):
        a = (pixel[i] + prev[0]) % 256
        b = (pixel[i + 1] + prev[1]) % 256

        c = (KEY[0][0] * a + KEY[0][1] * b) % 256
        d = (KEY[1][0] * a + KEY[1][1] * b) % 256

        enc_pixel.append(c)
        enc_pixel.append(d)
        prev = [c, d]

    enc_img = Image.new("L", img.size)
    enc_img.putdata(enc_pixel)
    enc_img.save(output_path)


encrypt("my.png", "my.enc.png")
encrypt("flag.png", "flag.enc.png")

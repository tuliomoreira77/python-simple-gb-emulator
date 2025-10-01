


def test_pixel():
    least_byte_addr = 0b11001011
    most_byte_addr = 0b10010001
    pixels = [0x0] * 8
    mask = 0b10000000
    for i in range(8):
        most_bit = (most_byte_addr & mask) >> 7-i
        least_bit = (least_byte_addr & mask) >> 7-i
        pixel = most_bit << 1 | least_bit
        pixels[i] = pixel
        mask = mask >> 1
    return pixels


print(test_pixel())
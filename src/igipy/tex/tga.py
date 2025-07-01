import struct
from io import BytesIO


def rgba_to_bmp(width, height, bitmap):
    row_padding = (4 - (width * 3) % 4) % 4
    row_size = width * 3 + row_padding
    pixel_data = bytearray()

    for y in reversed(range(height)):
        for x in range(width):
            i = (y * width + x) * 4
            r, g, b, a = bitmap[i : i + 4]
            pixel_data.extend([b, g, r])  # BMP uses BGR format
        pixel_data.extend(b"\x00" * row_padding)

    file_size = 14 + 40 + len(pixel_data)

    bmp_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54)
    dib_header = struct.pack("<IIIHHIIIIII", 40, width, height, 1, 24, 0, len(pixel_data), 2835, 2835, 0, 0)

    return bmp_header + dib_header + pixel_data


def rgba_to_tga(width, height, bitmap):
    """
    Convert RGBA bitmap (bytes or bytearray) to a TGA file as bytes.
    Pixel format must be RGBA (4 bytes per pixel).
    """
    if len(bitmap) != width * height * 4:
        raise ValueError("Bitmap size does not match width*height*4")

    # TGA Header: 18 bytes
    header = bytearray(18)
    header[2] = 2  # uncompressed true-color image
    header[12] = width & 0xFF
    header[13] = (width >> 8) & 0xFF
    header[14] = height & 0xFF
    header[15] = (height >> 8) & 0xFF
    header[16] = 32  # bits per pixel
    header[17] = 0x20  # origin at top-left; set to 0x00 for bottom-left

    # Convert RGBA to BGRA
    bgra = bytearray()
    for i in range(0, len(bitmap), 4):
        r, g, b, a = bitmap[i], bitmap[i + 1], bitmap[i + 2], bitmap[i + 3]
        bgra.extend([b, g, r, a])

    return bytes(header + bgra)


def bitmap_to_tga(width, height, data, stream: BytesIO = None):
    """
    Saves raw ARGB1555 image data as a 16-bit TGA file.

    The TGA format expects a 16-bit layout of ARRRRRGGGGGBBBBB, but with
    little-endian byte order. This function handles the creation of the
    TGA header and ensures the pixel data is correctly formatted.

    Args:
        width (int): The width of the image in pixels.
        height (int): The height of the image in pixels.
        data (bytes): A byte string containing the raw ARGB1555 pixel data.
                      The length should be width * height * 2.
        output_filename (str): The path to save the resulting .tga file.
    """
    stream = stream or BytesIO()

    if len(data) != width * height * 2:
        raise ValueError("Data size does not match width and height.")

    # 1. Construct the 18-byte TGA header.
    # The TGA header structure is well-defined. We are creating an
    # uncompressed, true-color image.
    # '<' specifies little-endian byte order for the multi-byte fields.
    header = struct.pack(
        "<B"  # id_length (1 byte)
        "B"  # color_map_type (1 byte)
        "B"  # image_type (1 byte)
        "H"  # color_map_origin (2 bytes) - Not used
        "H"  # color_map_length (2 bytes) - Not used
        "B"  # color_map_depth (1 byte) - Not used
        "H"  # x_origin (2 bytes)
        "H"  # y_origin (2 bytes)
        "H"  # width (2 bytes)
        "H"  # height (2 bytes)
        "B"  # bits_per_pixel (1 byte)
        "B",  # image_descriptor (1 byte)
        0,  # id_length: No ID field
        0,  # color_map_type: No color map
        2,  # image_type: Uncompressed, true-color
        0,  # color_map_origin
        0,  # color_map_length
        0,  # color_map_depth
        0,  # x_origin
        0,  # y_origin
        width,
        height,
        16,  # bits_per_pixel: 16-bit
        1,  # image_descriptor: 1 bit of alpha, origin at lower-left
    )

    stream.write(header)
    stream.write(data)
    stream.seek(0)

    return stream

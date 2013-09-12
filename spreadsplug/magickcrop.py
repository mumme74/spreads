import logging
import os
import tempfile
from subprocess import check_output

import wand.image
from concurrent import futures

import spreads
from spreads.plugin import HookPlugin

logger = logging.getLogger('spreadsplug.magickcrop')

# Factor to reduce by for determining crop boundaries, lower values are faster
# but more inaccurate
REDUCE_FACTOR = 4


def autocrop_image(in_path, out_path, gutter_distance=0, extra_crop=0,
                   even=None):
    # Save a scaled version of the image to save space
    with wand.image.Image(filename=in_path) as img:
        img.resize(img.width/REDUCE_FACTOR, img.height/REDUCE_FACTOR)
        tmp_fp, tmp_path = tempfile.mkstemp(suffix=".jpg")
        img.save(filename=tmp_path)

    # Obtain crop parameters
    crop_params = check_output(["convert", tmp_path, "-colorspace", "gray",
                                "-colors", "2", "-normalize",
                                "-virtual-pixel", "edge", "-blur", "0x15",
                                "-fuzz", "25%", "-trim",
                                "-format", "%[fx:page.x],%[fx:page.y],"
                                "%[fx:w],%[fx:h]",
                                "info:"]).strip().split(',')

    # Apply crop parameters
    with wand.image.Image(filename=in_path) as img:
        left, top, width, height = [int(x)*REDUCE_FACTOR for x in crop_params]

        if gutter_distance:
            width -= gutter_distance
        if extra_crop:
            width -= extra_crop
            height -= extra_crop*2
            top += extra_crop

        if not even:
            left += gutter_distance
        else:
            left += extra_crop

        img.crop(left, top, width=width, height=height)
        img.save(filename=out_path)

    # Remove temporary files
    os.remove(tmp_path)


class MagickCropPlugin(HookPlugin):
    def process(self, path):
        path = os.path.join(path, 'raw')
        gutter_odd = spreads.config['magickcrop']['gutter_odd'].get(int)
        gutter_even = spreads.config['magickcrop']['gutter_even'].get(int)
        extra_crop = spreads.config['magickcrop']['extra_crop'].get(int)

        logger.debug("Cropping images with ImageMagick")
        images = sorted([os.path.join(path, x) for x in os.listdir(path)])
        with futures.ProcessPoolExecutor() as executor:
            for idx, img in enumerate(images):
                even = not idx % 2
                if even:
                    gutter = gutter_even
                else:
                    gutter = gutter_odd
                out_img = os.path.join(path, 'done', os.path.basename(img))
                executor.submit(autocrop_image, img, out_img,
                                gutter, extra_crop, even)

import os

import numpy as np
from PIL import Image as PILImage

from dl.util import visualize_boxes_and_labels_on_image_array_for_shelf
import logging
logger = logging.getLogger("django")


def wrap_ret(ret):
    standard_ret = {
        'status': 200,
        'message': '成功',
        'attachment': ret,
    }
    return standard_ret


def shelf_visualize(boxes, image_path):
    image = PILImage.open(image_path)
    text_infos = []
    color_infos = []
    for one in boxes:
        text_infos.append('{}-{}'.format(one['level'], one['upc']))
        color = 'black'
        if one['result'] == 0:
            color = 'blue'
        elif one['result'] == 1 or one['result'] == 2:
            color = 'red'
        color_infos.append(color)
    logger.info('visualize:{}'.format(boxes))
    visualize_boxes_and_labels_on_image_array_for_shelf(
        np.array(image),
        boxes,
        text_infos,
        color_infos
    )
    image_dir = os.path.dirname(image_path)
    result_image_name = 'visual_' + os.path.split(image_path)[-1]
    result_image_path = os.path.join(image_dir, result_image_name)
    (im_width, im_height) = image.size
    image.thumbnail((int(im_width), int(im_height)), PILImage.ANTIALIAS)
    image.save(result_image_path)
    return result_image_name
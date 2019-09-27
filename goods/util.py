import os

import numpy as np
from PIL import Image as PILImage

from dl.util import visualize_boxes_and_labels_on_image_array_for_shelf

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
    image_np = np.array(image)
    visualize_boxes_and_labels_on_image_array_for_shelf(
        image_np,
        boxes,
        text_infos,
        color_infos
    )
    output_image = PILImage.fromarray(image_np)
    image_dir = os.path.dirname(image_path)
    result_image_name = 'visual_' + os.path.split(image_path)[-1]
    result_image_path = os.path.join(image_dir, result_image_name)
    # (im_width, im_height) = image.size
    # output_image.thumbnail((int(im_width), int(im_height)), PILImage.ANTIALIAS)
    output_image.save(result_image_path)
    return result_image_name

if __name__ == '__main__':
    """Test code: Uses the two specified"""

    boxes = [{'level': 1, 'xmin': 200, 'ymin': 200, 'xmax': 400, 'ymax': 400, 'result': 1, 'upc':''}]
    image_path = 'c:/fastbox/1.jpg'

    shelf_visualize(boxes,image_path)
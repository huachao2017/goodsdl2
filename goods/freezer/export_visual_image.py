import os, tarfile
import shutil
import sys
import argparse
import main.import_django_settings
from django.conf import settings

from goods.models import FreezerImage

def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    return parser.parse_args(argv)

def make_targz(output_filename, source_dir):
  with tarfile.open(output_filename, "w:gz") as tar:
    tar.add(source_dir, arcname=os.path.basename(source_dir))

if __name__ == "__main__":
    # args = parse_arguments(sys.argv[1:])
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    freezerimages_dir = os.path.join(cur_dir,'freezerimages')
    if not os.path.isdir(freezerimages_dir):
        os.mkdir(freezerimages_dir)
    else:
        os.removedirs(freezerimages_dir)
        os.mkdir(freezerimages_dir)

    print(settings.MEDIA_ROOT)
    freezer_images = FreezerImage.objects.exclude(visual='')
    for freezer_image in freezer_images:
        print(settings.MEDIA_ROOT)
        print(freezer_image.visual)
        visual_path = os.path.join(settings.MEDIA_ROOT, freezer_image.visual)
        print(visual_path)
        shutil.copy(visual_path,freezerimages_dir)

    make_targz('{}/freezerimages.tar.gz'.format(cur_dir),freezerimages_dir)





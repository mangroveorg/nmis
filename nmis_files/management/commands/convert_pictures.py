#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

""" RELIES ON imagemagick `convert` command line utility """

import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

RAW_FOLDER_NAME = 'raw'
RAW_FILE_PREFIX = 'raw'

def smakedirs(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


class Command(BaseCommand):
    help = "convert all pictures to defined format"
    args = "<photos_folder> [<json_format>]"

    def handle(self, *args, **options):
        try:
            photos_folder = settings.PICTURES_FOLDER
            formats = settings.PICTURES_FORMATS
        except:
            photos_folder = None
            formats = None

        if len(args) >= 2:
            formats = json.load(args[1])
        if len(args) >= 1:
            photos_folder = args[0]

        if not photos_folder or not formats:
            raise CommandError("Wrong number of arguments. Run " \
                               "'python manage.py help convert_pictures' " \
                               "for usage.")
        self._convert_pictures(photos_folder, formats)

    def _convert_pictures(self, photos_folder, formats, overwrite=False):

        # check path existence
        if not os.path.isdir(photos_folder):
            raise CommandError("photos folder is wrong.")

        for picture in os.listdir(photos_folder):
            picture_folder = os.path.join(photos_folder, picture)
            raw_folder = os.path.join(picture_folder, RAW_FOLDER_NAME)
            try:
                raw_file = os.listdir(raw_folder)[0]
            except OSError, IndexError:
                # raw file is missing. skipping.
                print("FAILED: original (raw) file not present.")
            raw_path = os.path.join(raw_folder, raw_file)
            canon_path, file_ext = raw_file.rsplit('.', 1)
            canon_path = canon_path.split('%s_' % RAW_FILE_PREFIX, 1)[1]

            for format in formats:
                format_folder = os.path.join(picture_folder, format)
                smakedirs(format_folder)
                format_file = os.path.join(format_folder, '%s_%s.%s' % (format, canon_path, file_ext))

                # skip if file exist
                if os.path.exists(format_file) and not overwrite:
                    print("File %s already exist." % format_file)
                    continue

                command = ['convert', '-thumbnail', format, raw_path, format_file]

                if subprocess.call(command) != 0:
                    # something went wrong. who cares?
                    print("FAILED to convert %s to %s." % (canon_path, format))
                else:
                    print("SUCESSFULY converted %s to %s." % (canon_path, format))

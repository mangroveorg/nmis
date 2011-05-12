#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import os
import re
import shutil
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

CSV_SEP = ','
RAW_FOLDER_NAME = 'raw'
RAW_FILE_PREFIX = 'raw'


def smakedirs(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


class Command(BaseCommand):
    help = "import pictures from CSV exports and photos dump"
    args = "<csv_folder> <photos_folder>"

    def handle(self, *args, **options):
        dst_folder = settings.PICTURES_FOLDER
        if len(args) == 2:
            csv_folder = args[0]
            photos_folder = args[1]
        else:
            raise CommandError("Wrong number of arguments. Run " \
                               "'python manage.py help import_pictures' " \
                               "for usage.")
        self._import_pictures(csv_folder, photos_folder, dst_folder)

    def _import_pictures(self, csv_folder, photos_folder, \
                         dst_folder, overwrite=False):

        # check path existence
        if not os.path.isdir(csv_folder) or not os.path.isdir(photos_folder):
            raise CommandError("CSV folder or photos folder is wrong.")

        # loop on excel files
        for csv_file in os.listdir(csv_folder):
            if not csv_file.endswith('.csv'):
                continue
            print("Opening %s..." % csv_file)
            attachments = self._attachments_for_file(os.path.join(csv_folder, \
                                                                  csv_file))
            print("\t%d attachments!" % attachments.__len__())

            # loop on attachments
            for attachment in attachments:
                attach_path = os.path.join(photos_folder, attachment)
                canon_path, file_ext = attachment.rsplit('.', 1)
                dst_path = os.path.join(dst_folder, canon_path)
                raw_folder = os.path.join(dst_path, RAW_FOLDER_NAME)
                raw_file = os.path.join(raw_folder, '%s_%s' \
                                               % (RAW_FILE_PREFIX, attachment))

                # original file exist
                # let's create a folder for the picture
                # then copy file in sub ~raw folder
                if os.path.isfile(attach_path):
                    if os.path.exists(raw_file) and not overwrite:
                        break
                    smakedirs(dst_path)
                    smakedirs(raw_folder)
                    print("\tcopying %s" % attachment)
                    shutil.copy(attach_path, raw_file)
                else:
                    print("missing original file: %s" % attach_path)

    def _attachments_for_file(self, filepath):
        f = open(filepath)
        first_line = f.readline()
        try:
            col_num = [column.strip() for column in \
                       first_line.split(CSV_SEP)].index('_attachments')
        except ValueError:
            return []

        attachments = []

        line = f.readline()
        while line:
            l_attachments = re.findall(\
                               r'u\'attachments\/([a-zA-Z0-9\_\-\.]+)\'', line)
            if l_attachments.__len__() > 0:
                attachment = l_attachments[0]
                attachments.append(attachment)
                #print("ATTACHMENT: %s" % attachment)
            line = f.readline()
        return attachments

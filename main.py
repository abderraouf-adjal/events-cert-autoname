#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: ISC
# 
# Copyright (c) 2020 Abderraouf Adjal
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# events-cert-autoname
# 
# Version: v0.1.3
# Date: 2020-02-14

# Tool to write names on a list to an image.
# This is used to save time when generate attendance certificates for events.
#
# For usage help:
#   % python3 main.py --help
#
# Usage examples:
#   % python3 main.py "list.csv" "cert.png" "et-book-bold-line-figures.ttf" "certs_output/"
#   % python3 main.py "list.csv" "cert.png" "et-book-bold-line-figures.ttf" "certs_output/" -s 42 -k "#000000" -y 200
#   % python3 main.py "list.csv" "cert.png" "et-book-bold-line-figures.ttf" "certs_output/" --fontsize 42 -k "#000000" -y 200 --replace
#
# Install requirements:
#   % pip3 install --user -r requirements.txt
#
# NOTE: - For Arabic names, try to use the font <DejaVuSans.ttf>
#       - For the CSV file, Use comma to separate values (NAME, EMAIL).
#       - This script tested for GNU/Linux OS.

import os
import argparse
from sys import stderr as sys_stderr
from csv import reader as csv_reader
from arabic_reshaper import reshape as arabic_reshaper_reshape
from PIL import Image, ImageFont, ImageDraw
from bidi.algorithm import get_display as bidi_algorithm_get_display

def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_list', type=str,
                        help = 'Path to names list CSV file (NAME, EMAIL).')
    parser.add_argument('cert_img', type=str,
                        help = 'Path to certificate image file.')
    parser.add_argument('font_file', type=str,
                        help = 'Font file (truetype).')
    parser.add_argument('output_dir', type=str,
                        help = 'Path to the export folder.')
    parser.add_argument('-s', '--fontsize', type=int, default=48, 
                        help = 'Font size.')
    parser.add_argument('-k', '--colorhex', type=str, default='000000', 
                        help = 'RGB font color in HEX.')
    parser.add_argument('-x', type=int, default=None,
                        help = 'Text position X, In center by default.')
    parser.add_argument('-y', type=int, default=None,
                        help = 'Text position Y, In center by default.')
    parser.add_argument('-r', '--replace', action='store_true',
                        help = 'Force replace/overwrite the list outputs.')
    return parser.parse_args()


def csv_to_dict(ppl, namesfile):
    with open(namesfile, 'r') as fd:
        read_csv = csv_reader(fd, delimiter=',')
        for row in read_csv:
            row[0] = row[0].strip().title() # The person name
            row[1] = row[1].strip() # The e-mail
            ppl.append(tuple((row[0], row[1])))


def make_person_cert(name, email, cert_img, out_cert, fontfile, fontsize, color_tuple, x, y):
    img = Image.open(cert_img).convert('RGB')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font=fontfile, size=fontsize)
    name_reshaped = arabic_reshaper_reshape(name) # Correct shape
    name_reshaped_directed = bidi_algorithm_get_display(name_reshaped) # Correct direction
    # Text in center as default option
    if (x is None):
        x = int((img.size[0] - font.getsize(name_reshaped_directed)[0]) / 2)
    if (y is None):
        y = int((img.size[1] - font.getsize(name_reshaped_directed)[1]) / 2)
    draw.text((x, y), name_reshaped_directed, fill=color_tuple, font=font, align='center') # ((x, y),"Text",(r,g,b))
    img.save(out_cert, format='PDF')
    return True


def main():
    in_arg = get_input_args()

    if (os.path.exists(in_arg.output_dir) == False):
        try:
            os.makedirs(in_arg.output_dir)
        except:
            print('  ** ERROR: Can NOT make the output folder. Exit.', file=sys_stderr)
            exit(1)
        
    if (os.path.isdir(in_arg.output_dir) == False):
        print('  ** ERROR: "{0}" is not a folder. Exit.'.format(in_arg.output_dir), file=sys_stderr)
        exit(1)

    colorhex = in_arg.colorhex.lstrip('#')
    color_tuple = tuple(int(colorhex[i:i+2], 16) for i in (0, 2, 4))
    ppl = list() # [('name', 'email'), ('name', 'email')]
    csv_to_dict(ppl, in_arg.csv_list)
    count = 0
    print('Processing...')
    for person in ppl:
        try:
            out_cert = os.path.join(in_arg.output_dir, '{0}+{1}+{2}.pdf'.format(os.path.splitext(in_arg.cert_img)[0].split('/')[-1], person[0], person[1]))
            if ((in_arg.replace == False) and (os.path.exists(out_cert) == True)):
                print('\n  ** WARNING: The path for output "{0}" exists.'.format(out_cert), file=sys_stderr)
                q = str(input('  >> Replace the file? [Y or N] (N): ')).strip().lower()
                if (q != 'y'):
                    continue
            
            r = make_person_cert(person[0], person[1],
                                in_arg.cert_img, out_cert,
                                in_arg.font_file, in_arg.fontsize,
                                color_tuple, in_arg.x, in_arg.y)
            if (r == True):
                print('{0}  -  {1}'.format(person[0], person[1]))
                count += 1
        except:
            print('  ** ERROR: With [{0}, {1}]. Exit.'.format(person[0], person[1]), file=sys_stderr)
            exit(1)
        
    print('\nTotal of "{0}" files made in "{1}".'.format(count, in_arg.output_dir))


if __name__ == "__main__":
    main()

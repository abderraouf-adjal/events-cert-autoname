#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# events-cert-autoname
# 
# Version: v0.1.1
# Date: 2020-02-14

# Copyright (c) 2020 Abderraouf Adjal <abderraouf.adjal@gmail.com>
# 
# Permission to use, copy, modify, and distribute this software for any
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

# Tool to write names on a list to an image.
# This is used to save time when generate attendance certificates for events.
#
# For help:
#   % python3 main.py --help
#
# Usage example:
#   % python3 main.py --list "list.csv" --cert "cert.png" --outdir "certs_output" --y 200 --fontfile "et-book-bold-line-figures.ttf" --colorhex "#000000"
# Install requirements (PIL/Pillow for py3):
#   % pip3 install --user -r requirements.txt
#
# This script tested for GNU/Linux OS.

import os
import sys
import csv
import argparse
from PIL import Image, ImageFont, ImageDraw


def get_input_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--cert', type=str, default='cert.png', 
                        help = 'Path to certificate image file.')
    parser.add_argument('--list', type=str, default='list.csv', 
                        help = 'Path to names list CSV file (NAME, EMAIL).')
    parser.add_argument('--outdir', type=str, default='certs_output/', 
                        help = 'Path to the export folder.')
    parser.add_argument('--fontfile', type=str, default='et-book-bold-line-figures.ttf', 
                        help = 'Font file (truetype).')
    parser.add_argument('--fontsize', type=int, default=48, 
                        help = 'Font size.')
    parser.add_argument('--colorhex', type=str, default='000000', 
                        help = 'RGB font color in HEX.')
    parser.add_argument('--x', type=int, default=None, 
                        help = 'Text position X, In center by default.')
    parser.add_argument('--y', type=int, default=None, 
                        help = 'Text position Y, In center by default.')

    return parser.parse_args()


def csv_to_dict(ppl, namesfile):
    with open(namesfile, 'r') as fd:
        read_csv = csv.reader(fd, delimiter=',')
        for row in read_csv:
            row[0] = row[0].strip().title() # The person name
            row[1] = row[1].strip() # The e-mail
            ppl.append(tuple((row[0], row[1])))


def make_person_cert(name, email, empty_cert_img, outdir, fontfile, fontsize, color_tuple, x, y):
    out_img = os.path.join(outdir, '{0}+{1}+{2}.pdf'.format(os.path.splitext(empty_cert_img)[0].split('/')[-1], name, email))
    if (os.path.exists(out_img) == True):
        print('\n  ** WARNING: The path for output "{0}" exists.'.format(out_img), file=sys.stderr)
        q = str(input('  >> Replace the file? [Y or N] (N): ')).lower().strip()
        if (q != 'y'):
            return False
    
    img = Image.open(empty_cert_img).convert('RGB')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font=fontfile, size=fontsize)
    
    # Text in center as default option
    if (x is None):
        x = int((img.size[0] - font.getsize(name)[0]) / 2)
    if (y is None):
        y = int((img.size[1] - font.getsize(name)[1]) / 2)
    
    draw.text((x, y), name, fill=color_tuple, font=font, align='center') # ((x, y),"Text",(r,g,b))
    img.save(out_img, format='PDF')
    return True


def main():
    in_arg = get_input_args()

    if (os.path.exists(in_arg.outdir) == False):
        try:
            os.makedirs(in_arg.outdir)
        except:
            print('  ** ERROR: Can NOT make the output folder. Exit.', file=sys.stderr)
            exit(1)
        
    if (os.path.isdir(in_arg.outdir) == False):
        print('  ** ERROR: "{0}" is not a folder. Exit.'.format(in_arg.outdir), file=sys.stderr)
        exit(1)

    colorhex = in_arg.colorhex.lstrip('#')
    color_tuple = tuple(int(colorhex[i:i+2], 16) for i in (0, 2, 4))

    ppl = list() # [('name', 'email'), ('name', 'email')]
    csv_to_dict(ppl, in_arg.list)

    print('Processing...')
    count = 0
    for person in ppl:
        try:
            r = make_person_cert(person[0], person[1],
                                in_arg.cert, in_arg.outdir,
                                in_arg.fontfile, in_arg.fontsize,
                                color_tuple, in_arg.x, in_arg.y)
            if (r == True):
                print('{0}  -  {1}'.format(person[0], person[1]))
                count += 1
        except:
            print('  ** ERROR: With [{0}, {1}]. Exit.'.format(person[0], person[1]), file=sys.stderr)
            exit(1)
        
    print('\nTotal of "{0}" files made in "{1}".'.format(count, in_arg.outdir))


if __name__ == "__main__":
    main()

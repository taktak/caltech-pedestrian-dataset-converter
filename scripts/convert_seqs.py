#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import cv2 as cv
import struct

def save_img(dname, fn, i, frame):
    cv.imwrite('{}/{}_{}_{}.png'.format(
        out_dir, os.path.basename(dname),
        os.path.basename(fn).split('.')[0], i), frame)

def read_header(ifile):
    feed = ifile.read(4)
    norpix = ifile.read(24)
    version = struct.unpack('@i', ifile.read(4))
    length = struct.unpack('@i', ifile.read(4))
    assert(length != 1024)
    descr = ifile.read(512)
    params = [struct.unpack('@i', ifile.read(4))[0] for i in range(0,9)]
    fps = struct.unpack('@d', ifile.read(8))
    # skipping the rest
    ifile.read(432)
    image_ext = {100:'raw', 102:'jpg',201:'jpg',1:'png',2:'png'}
    return {'w':params[0],'h':params[1],
            'bdepth':params[2],
            'ext':image_ext[params[5]],
            'format':params[5],
            'size':params[4],
            'true_size':params[8],
            'num_frames':params[6]}

out_dir = 'data/images'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
for dname in sorted(glob.glob('data/set*')):
    print "{} is being extracted. ".format(dname)
    for fn in sorted(glob.glob('{}/*.seq'.format(dname))):
        print "  {} is being extracted. ".format(fn)
        # https://gist.github.com/psycharo/7e6422a491d93e1e3219/
        ifile = open(fn, 'rb')
        params = read_header(ifile)
        bytes = open(fn, 'rb').read()
        
        # this is freaking magic, but it works
        extra = 8
        s = 1024
        seek = [0]*(params['num_frames']+1)
        seek[0] = 1024
        for i in range(0, params['num_frames']):
            tmp = struct.unpack_from('@I', bytes[s:s+4])[0]
            I = bytes[s+4:s+tmp]
            s += tmp + extra
            if i == 0:
                val = struct.unpack_from('@B', bytes[s:s+1])[0]
                if val != 0:
                    s -= 4
                else:
                    extra += 8
                    s += 8
            
            tmp_file = '/tmp/img%d.jpg' % i
            open(tmp_file, 'wb+').write(I)
            
            img = cv.imread(tmp_file)
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            save_img(dname, fn, i, img)

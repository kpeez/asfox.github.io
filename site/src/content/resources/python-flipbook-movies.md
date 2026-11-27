---
title: "Python Flipbook Movies"
date: 2013-04-01
kind: "tutorial"
summary: "A short python script that writes out a flipbook movie of one slice from many subjects, used to check registration."
legacy:
  - "/python-flipbook-movies.html"
  - "/2013/04/01/python-flipbook-movies"
---

In my [Looking at Co-registered Brain Data](/resources/looking-at-co-registered-brain-data/) post, I showed a movie of different subjects' brain data. Here is how I created that movie.

I wrote a quick bit of python code that will show slice `136` of dimension `2` (in this case sagittal) and write out a movie named `t1.mp4` at `5` frames a second, from the subjects listed in `t1*.nii`.

```bash
drawASlice.py 136 2 t1.mp4 5 t1*.nii
```

This code was used to create this movie.

*(The original video for this tutorial is no longer available.)*

Here is the full bit of code.

**Make a flipbook to check data in python** — `drawASlice.py` ([download](/downloads/code/drawASlice.py))

```python
#!/usr/bin/env python

# import alot of libraries...
# If these aren't installed, you will have to install them. :-/
import sys
import os
import nibabel as nib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import subprocess

def main(argv):
    sliceNum = argv[1]
    dim = int(argv[2])
    outf = argv[3]
    rate = int(argv[4])
    in_files = argv[5:]

    # Prepare to pipe to ffmpeg
    cmdstring = ('ffmpeg',
        '-y',
        '-f','image2pipe',
        '-r', '%d' % rate,
        '-vcodec', 'png',
        '-s', '320x280',
        '-i', 'pipe:', outf
        )
    # setup a ffmpeg pipe...
    p = subprocess.Popen(cmdstring, stdin=subprocess.PIPE)

    # setup a the fig and main axis to plot on
    fig = plt.figure(facecolor='black', figsize=(4, 3), dpi=80)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)

    # for each image in the input list
    for i, f in enumerate(in_files):
        # read the image
        img = nib.load(f)
        img_data = img.get_data()
        # find the right slice to draw
        if dim==1:
            toDraw = img_data[:,sliceNum,:];
        elif dim==2:
            toDraw = img_data[sliceNum,:,:];
        elif dim==3:
            toDraw = img_data[:,:,sliceNum];
        # orient appropriately?
        toDraw=np.rot90(toDraw)

        # show the image
        im = ax.imshow(toDraw, cmap = cm.Greys_r, interpolation='nearest')
        plt.show()
        # write to the pipe...
        plt.savefig(p.stdin, format='png', facecolor=fig.get_facecolor(), edgecolor='none', dpi=(80) )

if __name__ == '__main__':
    main(sys.argv)
```

I also use this technique to verify that my clusters are *where* I claim they are in each participant. :-D

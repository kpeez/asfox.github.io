---
title: "Read NIFTI in fmriStat."
date: 2013-05-30
kind: "tutorial"
summary: "Modified fmriStat files that use the SurfStat libraries so fmriStat can read and write NIFTI files."
legacy:
  - "/read-nifti-in-fmristat.html"
  - "/2013/05/30/read-nifti-in-fmristat"
---

*If* you have a need to run fmristat these days, it can be frustrating that it can't read Nifti files. Using the libraries in surfStat, I added this functionality to fmriStat.

First, you will need to install [fmriStat](http://www.math.mcgill.ca/keith/fmristat/) and [surfStat](http://www.math.mcgill.ca/keith/surfstat/) from Keith Worsley's website. Otherwise, updating fmristat wouldn't be that useful… ;-)

I overwrote a few files to call on the code from fmristat to read and write nifti files. You can download these files by clicking the download links above each file, and simply replace the existing fmristat files. Sadly, it is that kludgy.

**Read Nifti** — `fmris_read_image.m` ([download](/downloads/code/fmristat/fmris_read_image.m))

```matlab
function [d] = fmris_read_image(file,Z,T)

% (c) John Aston & Roger Gunn

file = deblank(file);
if ~(file(1)=='/' | file(2)==':')
   if file(1:2)=='./'
      file=[pwd file(3:length(file))];
   else
      file=[pwd '/' file];
   end
end

[path,name,ext]=fileparts(file);
if strcmp(ext,'.gz')
   if isunix
      unix(['gunzip ' file]);
   else
      ['Can''t gunzip on non-unix system']
      return
   end
   [path,name,ext]=fileparts(name)
end

switch lower(ext)
case '.mnc'
   if nargin == 3
      d = fmris_read_minc(file,Z,T);
   else
      d = fmris_read_minc(file);
   end
case '.img'
   if nargin == 3
      d = fmris_read_analyze(file,Z,T);
   else
      d = fmris_read_analyze(file);
   end
case '.brik'
   if nargin == 3
      d = fmris_read_afni(file,Z,T);
   else
      d = fmris_read_afni(file);
   end
case '.nii'
   if nargin == 3
      d = SurfStatReadVol1(file,Z,T);
   else
      d = SurfStatReadVol1(file);
   end

otherwise
   ['Unknown file extension']
end

d.parent_file=file;

return
```

**Write Nifti** — `fmris_write_image.m` ([download](/downloads/code/fmristat/fmris_write_image.m))

```matlab
function [d]=fmris_write_image(d,Z,T)

% (c) John Aston & Roger Gunn

file = deblank(d.file_name);
if ~(file(1)=='/' | file(2)==':')
   if file(1:2)=='./'
      file=[pwd file(3:length(file))];
   else
      file=[pwd '/' file];
   end
end

[base,ext]=fileparts2(file);
d.file_name=[base ext];

switch lower(ext)
case '.mnc'
   if nargin == 3
      fmris_write_minc(d,Z,T);
   else
      fmris_write_minc(d);
   end
case '.img'
   if nargin == 3
      fmris_write_analyze(d,Z,T);
   else
      fmris_write_analyze(d);
   end
case '.brik'
   if nargin == 3
      fmris_write_afni(d,Z,T);
   else
      fmris_write_afni(d);
   end
case '.nii'
   if nargin == 3
      SurfStatWriteVol1(d,Z,T);
   else
      SurfStatWriteVol1(d);
   end
otherwise
   ['Unknown file extension']
end

return
```

Feel free to contact me if you have any questions! :-Drew

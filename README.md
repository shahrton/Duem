# Duem

**duem**: du emulator. (*pronounced Do 'em*) Emulates the Unix **du** command (*disk usage*), which is commonly used to go down directory (folder) trees and report back on disk usage below each directory.<br>
http://www.twentypede.com
* Runs from command line, simple (<300 lines) Python script</li>
* No additional Python Std Lib modules required, it only imports: sys, os, optparse, glob</li>
* Links are not followed, and their disk space used is ignored</li>
* Pre-compiled executable for Windows users who don't have Python installed (see below)</li>

Basically does something similar to **du**, but in addition:
1. has an option, -d or --depth, to only report back for a specifed depth down the tree. Actual disk usage below a point is calculated all the way down the tree; --depth only limits what is actually displayed. Also, if depth requested was larger than the actual depth of the tree, informs that only X levels were necessary.
1. In addition to reporting how much disk usage in and below a directory, reports how many
regular files are within the directory, and how much total disk space they use. (If there are no
  other sub-directories below, then only the number of regular files is reported, not their disk usage.)
1. The unit for disk space reporting is chosen automatically to be human-readable, depending on the size, however command line options -b, -k, -m, -g can be used to override and report in bytes, kilobytes, etc...

### Example
**duem** operating on a directory called `Lookup` containing:
```
AMR/ CPP/ Cprism/ Dyssa/ Figs/ Hydrogen11/ Laminar/ Manual/ Methane22/
Methane32/ Parallel/ Preuse/ Simsim/ Turbjet/ Zerod/
```
will give, with `duem -d 10 Lookup`:
```
256.2M Lookup   [no regular files]
   |->10.6M Lookup/Dyssa   [25 files: 3.6M]
      |->7.0M Lookup/Dyssa/Figs   [85 files: 7.0M]
         |->14.5K Lookup/Dyssa/Figs/.xvpics   [5 files]
   |->1.2M Lookup/Hydrogen11   [4 files]
   |->2.5M Lookup/Methane32   [32 files: 2.2M]
      |->347.2K Lookup/Methane32/src   [42 files]
      |->3.6K Lookup/Methane32/.xvpics   [1 files]
   |->26.6M Lookup/Laminar   [19 files]
   |->20.3K Lookup/Zerod   [23 files]
   |->29.0M Lookup/Methane22   [35 files]
   |->919.9K Lookup/Cprism   [55 files: 840.5K]
      |->55.1K Lookup/Cprism/NGOZI   [16 files]
      |->10.3K Lookup/Cprism/Monte   [10 files: 5.9K]
         |->400b Lookup/Cprism/Monte/CVS   [3 files]
      |->2.1K Lookup/Cprism/CVS   [3 files]
   |->177.5M Lookup/AMR   [no regular files]
      |->1.3M Lookup/AMR/FnlPrism   [61 files]
      |->176.2M Lookup/AMR/Dimen   [115 files]
   |->38.9K Lookup/Turbjet   [32 files]
   |->96.2K Lookup/Manual   [8 files]
   |->15.2K Lookup/Parallel   [2 files]
   |->34.2K Lookup/Simsim   [23 files]
   |->5.5M Lookup/Figs   [48 files]
   |->348.7K Lookup/CPP   [35 files: 323.8K]
      |->20.9K Lookup/CPP/Monte   [5 files]
   |->1.7M Lookup/Preuse   [10 files]
Was only necessary to go down 3 levels. --depth 10 was requested.
```

### MS Windows Users who lack Python
The zip file `duem_1.4.1.zip` (or later version) contains a pre-compiled executable (made with pyinstaller). Download the zip and extract the contents. A directory/folder `duem` will contain `duem.exe` and several other files *which are important as they contain and use a Python interpreter so do not delete them*. Either add this folder to your PATH environment variable, or choose a folder already in your PATH, and add a file named `duem.bat` which will consist of something like the following lines:
```
  @echo off 
  REM This is to run duem, the du emulator
  C:\Users\YOURUSERNAME\PLACE_YOU_DOWNLOADED_TO\duem\duem.exe %*
  REM python C:\Users\YOURUSERNAME\workspace\Du\duem.py %*
```
i.e. it points to the location to which you extracted the zip file contents. Hopefully then, typing `duem` at a DOS prompt will work: Open a DOS window using `cmd`, test by typing `duem --version` or `duem --help`.

#!/usr/local/bin/python
#Leave line above for Unix/Linux/Apple users. Perhaps run dos2unix on the script?
"""A Python-based utility to do in Windows what du does in Unix
   SRTonse, Created: 21st Dec 2015. starting point
   more or less Lifted from the O'Reilly Python Cookbook
"""

""" Modifications:
Version_Number = ("1.1.1", "(12/21/2015)")
Lifted from the Python Cookbook, then modified:
Final display has indentation for sub-dirs. Lists parent dirs
first then indented sub-dirs next
Default is automatic, similar to -h for Unix du.
Added a class PathItem to hold the folder/size/list of PathItems for subirs
Version_Number = ("1.1.2", "(12/21/2015)")
Minor changes
Version_Number = ("1.2.1", "(12/22/2015)")
Use glob to decode wildcards in command line args
Version_Number = ("1.3.1", "(3/27/2018)") Also write out the disk usage from regular files in each folder itself.
Version_Number = ("1.3.2", "(4/9/2018)")  Refinement on writing out the disk usage from regular files in each folder itself.
Version_Number = ("1.3.5", "(4/25/2018)") Improvement on help. Improved handling of listing and stat errors. Use of
DirSizeError exception discontinued. If dialled depth > required max depth, then informs so.
Removed option to follow links, just report them optionally at end.
Version_Number = ("1.4.1", "(4/27/2018)"): Replace getopt with optparse.
Version_Number = ("1.5.1", "(2/14/2020)"): Converted from Py2 to Py 3 simply running 2to3.py.

-----------------End of Modifications-----------------
"""
Version_Number = ("1.5.2", "(7/11/2020)")
"""Updated help
"""

"""ToDo:
logging?
How to handle Shortcuts?
Threads? say 3 or 4?
None of the above seem necessary at the present

"""
import sys
import os
from os.path import join, isdir, isfile
import optparse

#used for formatting of output
INDENT_INCREMENT = "   "
INDENT_ARROW = "|->"

max_depth_reached = -1

L_staterrors = list()    #to contain names of any directories/files that could not be stat'ed
L_listerrors = list()    #to contain names of any directories that could not be list'ed


class PathItem(object):
    """Container: Hold a dir name, path,
    bytes in it+all contained files/directories,
    local_bytes = only bytes from regular files in the dir,
    and a list L (of all contained directories as instances of this
    same PathItem class). The list only contains dirs down to level
    max_depth and is used for display. For calculating bytes used, the
    list is not used.
    """
    def __init__(self, p):
        self.path = p
        self.bytes = 0
        self.local_bytes = 0       #bytes in regular files
        self.local_regfiles = 0    # number of regular files
        self.L = []

    def __str__(self):
        S = "%s %i" % (self.path, self.bytes)
        return S


USAGE_MESSAGE = """
python duem.py [-bkmg] [-d depth] [dir1, dir2, dir3...]
Shows (in tree-like format) the disk file usage of dir1, dir2, dir3,... and
goes down the directory (i.e. folder) tree. If no path specified then
uses current working dir, i.e. \".\"
"""

def DefineInputOptsnArgs(Version_Number_Date):
    """Define the command line options and arguments here
    """
    CLOP = optparse.OptionParser(version=Version_Number_Date,usage=USAGE_MESSAGE)     #command line options
    CLOP.add_option("-d", "--depth", action="store", type="int", dest = "depth", default=0,
                    help="# of directories down for print display (default=0)")
    CLOP.add_option("-b", action="store_true", default=False, help="Display in Bytes")
    CLOP.add_option("-k", action="store_true", default=False, help="Display in Kiloytes")
    CLOP.add_option("-m", action="store_true", default=False, help="Display in Megaytes")
    CLOP.add_option("-g", action="store_true", default=False, help="Display in Gigabytes")
    #CLOP.add_option("--log", action="store", dest="loglevel", type="string", default="INFO",
    #                help="Specify logging verbosity level (DEBUG/ INFO(default)/ WARNING/ ERROR/ FATAL) on command line")
    return CLOP
#----------------------------------------------------------------------------

def ProcessInputOptsnArgs(clop):
    """Process the input command line opts and args
    """
    opts,args = clop.parse_args()

    units = "automatic"           #decide on unit based on size in bytes, append a b,K,M or G
    #unitname = ""                 #used for display at very end
    if opts.b: units = 'b'
    if opts.k: units = 'k'
    if opts.m: units = 'm'
    if opts.g: units = 'g'     #if multiple opts were added, last one decides
    D_units = {"b": "bytes", "k": "Kilobytes", "m": "Megabytes", "g": "Gigabytes", "automatic":""}
    unitname = D_units[units]

    try:
        depth = int(opts.depth)
    except:
        print("-d arg not a valid integer: (%s)" % opts.depth)
        raise

    return depth, units, unitname, args
#--------------------------------------------------------------------------

def dir_size(start, start_depth=0, max_depth=0):
    """ Get a list and size of all names of files and subdirectories in directory start
        Recursively go down
    """
    global max_depth_reached
    max_depth_reached = max(start_depth, max_depth_reached)
    PI1 = PathItem(start)
    try:
        dir_list = os.listdir(start)
    except:
        # If start is a directory, we probably had permission problems
        if os.path.isdir(start):
            #the dir contents could not be list'ed. Store for possible display at end of running
            L_listerrors.append(start)
            return None
        else: # otherwise, just re-raise the error so that it propagates, as could be serious
            raise

    total = 0
    for item in dir_list:
        # Get statistics on each item--file and subdirectory--of start
        path = join(start, item)
        try:
            stats = os.stat(path)       #EGOF getting file details (size etc) with os.stat
        except:
            #the item could not be stat'ed. Store for possible display at end of running
            #print "exception  ", path,"   ", islink(path)
            L_staterrors.append(path)
        else:
            # The size in bytes is in the seventh item of the stats tuple, so:
            if isfile(path):
                PI1.local_regfiles += 1
                PI1.local_bytes += stats[6]

            total += stats[6]

            """recursive descent if warranted. The recursive descent goes down all the way, since a correct calculation of
                size depends on that. However, for display purposes later in print_path(),
                depth is tested against max_depth
            """
            #if isdir(path) and (follow_links or not islink(path)):
            if isdir(path):
                PI2 = dir_size(path, start_depth+1, max_depth)
                try:
                    total += PI2.bytes
                except AttributeError:    #because a None could have been returned by dir_size
                    pass
                else:
                    if max_depth and (start_depth < max_depth):
                        PI1.L.append(PI2)
    PI1.bytes = total
    return PI1
#-------------------------------------------------------------------------------

def print_path(pathitem, indent, units):
    """Print info of the PathItem then recursively call itself for
       PathItems contained within, with addl indentation.
    """
    if not pathitem: return     #dir_size returns None if there was an error, so ignore
    def Auto_unit(units, x):
        """Decide what unit (b,K,M,G) to output, either from command line option or 
        automatically, based on file size  
        """
        if (units == "automatic" and x > 1024**3) or units =='g':
            return "%.1fG" % (float(x)/1024.0**3)
        elif (units == "automatic" and x > 1024**2) or units =='m':
                return "%.1fM" % (float(x)/1024.0**2)
        elif (units == "automatic" and x > 1024) or units =='k':
            return "%.1fK" % (float(x)/1024.0)
        elif units =='b':
            return "%ib" % x
        else:
            return "%ib" % x
    #--------------------------------------------------
    
    #no indentation arrow for uppermost level
    if bool(indent):
        indent_arrow = INDENT_ARROW
    else:
        indent_arrow = ""
    if pathitem.local_regfiles == 0:
        print('%s%s%s %s   [no regular files]' % (indent, indent_arrow, Auto_unit(units, pathitem.bytes),
                                        pathitem.path))
    else:
        if pathitem.bytes == pathitem.local_bytes:
            #don't bother to write size a 2nd time
            print('%s%s%s %s   [%i files]' % (indent, indent_arrow, Auto_unit(units, pathitem.bytes),
                                              pathitem.path, pathitem.local_regfiles))
        else: 
            print('%s%s%s %s   [%i files: %s]' % (indent, indent_arrow, Auto_unit(units, pathitem.bytes),
                                                  pathitem.path, pathitem.local_regfiles,
                                                  Auto_unit(units, pathitem.local_bytes)))

    for p in pathitem.L:          #recursive call
        print_path(p, indent+INDENT_INCREMENT, units)
    
#--------------------------------------- main -----------------------------------
if __name__=='__main__':
    # When used as a script:
    import glob
    CLOP = DefineInputOptsnArgs(Version_Number[0]+Version_Number[1])  #Define the input command line opts and args. 
    depth, units, unitname, args = ProcessInputOptsnArgs(CLOP)

    if len(args) < 1:
        paths = ["."]
    else:
        #Use set() to avoid something getting put on the list twice, as it is possible that
        #a file matches >1 wildcard pattern on the command line
        SoFiles = set()

        for l in args:
            #since some of the file names in args might contain wildcards, glob each item, and iterate that
            #too, therefore have double for's in l and l2
            args_globbed = glob.glob(l)               #EGOF un globbing
            for l2 in args_globbed:
                SoFiles.add(l2)

        paths = list(SoFiles)
        if not len(paths):
            print("No recognizable paths supplied on command line: ", args)
            sys.exit(1)

    #main work done here
    indent = ""
    #EGOFGo thru all command line files/folders and recursively down their dir trees without using os.walk
    for path in paths:
        pi1 = dir_size(path, 0, depth)      #finally return a single PathItem that contains other PathItems
        print_path(pi1, indent, units)

    #Done. Some final informative messages:
    if unitname: print(unitname)        #if unit of memory was explicitly requested
    if max_depth_reached < depth: print("Was only necessary to go down %i levels. --depth %i was requested." % (max_depth_reached, depth))
    #If there were dirs that could not be examined, print those out here if desired
    len_errors = len(L_staterrors)+len(L_listerrors)
    if len_errors:     #EGOF handling a raw_input yesno in one line, testing for uppercase Y
        if (input("Warning: Unable to list or \"stat\" %i directories. Show?(Y/y)" % len_errors)).upper() =="Y":
            if len(L_staterrors):
                print("The following directories/files/links were not processed due to Stat Errors")
                for d in L_staterrors:
                    print(d)
            if len(L_listerrors):
                print("The following directories were not processed due to dir listing Errors")
                for d in L_listerrors:
                    print(d)

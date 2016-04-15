
import os
import re
import sys
import struct
import mimetypes
import subprocess
import argparse
import time


if sys.version_info >= (3,0):
    import shutil
    import urllib.request
    from xmlrpc.client import ServerProxy, Error
else: # python2
    import urllib2
    from xmlrpclib import ServerProxy, Error

# ==== Opensubtitles.org server settings =======================================
# XML-RPC server domain for opensubtitles.org:
osd_server = ServerProxy('http://api.opensubtitles.org/xml-rpc')

# You can use your opensubtitles.org account to avoid "in-subtitles" advertisment and bypass download limits
# Be careful about your password security, it will be stored right here in plain text...
# You can also change opensubtitles.org language, it will be used for error codes and stuff
osd_username = 'Mediaplayer975'
osd_password = '12345678'
osd_language = 'en'

# ==== Language settings =======================================================
# Supported ISO codes: http://www.opensubtitles.org/addons/export_languages.php
#
# 1/ You can change the search language here by using either 2-letter (ISO 639-1)
# or 3-letter (ISO 639-2) language codes.
#
# - opt_languages = ['eng','fre'] to search for subtitles in multiple languages. Highly recommended.
# - opt_languages = ['eng,fre'] to download the first language available only
opt_languages = ['eng']

# Write 2-letter language code (ex: _en) at the end of the subtitles file. 'on', 'off' or 'auto'.
# If you are regularly searching for several language at once, you sould use 'on'.
opt_language_suffix = 'off'

# ==== GUI settings ============================================================

# Select your GUI. Can be overridden at run time with '--gui=xxx' argument.
# - auto (autodetection, fallback on CLI)
# - gnome (GNOME/GTK based environments, using 'zenity' backend)
# - kde (KDE/Qt based environments, using 'kdialog' backend)
# - cli (Command Line Interface)
opt_gui = 'auto'

# Change the subtitles selection GUI size:
opt_gui_width  = 720
opt_gui_height = 320

# If the search by movie hash fails, search by file name will be used as backup
opt_backup_searchbyname = 'on'

# Subtitles selection mode. Can be overridden at run time with '-a' argument.
# - manual (in case of multiple results, let you choose the subtitles you want)
# - auto (automatically select the most downloaded subtitles)
opt_selection_mode     = 'manual'

# Various GUI options. You can set them to 'on', 'off' or 'auto'.
opt_selection_language = 'off'
opt_selection_hi       = 'auto'
opt_selection_rating   = 'off'
opt_selection_count    = 'off'

# Enables extra output. Can be overridden at run time with '-v' argument.
opt_verbose            = 'off'

# ==== Super Print =============================================================
# priority: info, warning, error
# title: only for zenity messages
# message: full text, with tags and breaks (tag cleanup for terminal)
# verbose: is this message important?

def superPrint(priority, title, message):
    """Print messages through terminal, zenity or kdialog"""
    if opt_gui == 'gnome':
        if title:
            subprocess.call(['zenity', '--' + priority, '--title=' + title, '--text=' + message])
        else:
            subprocess.call(['zenity', '--' + priority, '--text=' + message])
    else:
        # Clean up formating tags from the zenity messages
        message = message.replace("\n\n", "\n")
        message = message.replace("<i>", "")
        message = message.replace("</i>", "")
        message = message.replace("<b>", "")
        message = message.replace("</b>", "")
        message = message.replace('\\"', '"')

        # Print message
        if opt_gui == 'kde':
            if priority == 'warning':
                priority = 'sorry'
            elif priority == 'info':
                priority = 'msgbox'

            if title:
                subprocess.call(['kdialog', '--' + priority, '--title=' + title, '--text=' + message])
            else:
                subprocess.call(['kdialog', '--' + priority, '--text=' + message])

        else: # CLI
            print(">> " + message)

# ==== Check file path & file ==================================================

def checkFile(path):
    """Check mimetype and/or file extension to detect valid video file"""
    if os.path.isfile(path) == False:
        superPrint("error", "File type error!", "This is not a file:\n<i>" + path + "</i>")
        return False

    fileMimeType, encoding = mimetypes.guess_type(path)
    if fileMimeType == None:
        fileExtension = path.rsplit('.', 1)
        if fileExtension[1] not in ['avi', 'mp4', 'mov','avi', 'mkv', 'mk3d', 'webm', \
        'ts', 'mts', 'm2ts', 'ps', 'vob', 'evo', 'mpeg', 'mpg', \
        'm1v', 'm2p', 'm2v', 'm4v', 'movhd', 'movx', 'qt', \
        'mxf', 'ogg', 'ogm', 'ogv', 'rm', 'rmvb', 'flv', 'swf', \
        'asf', 'wm', 'wmv', 'wmx', 'divx', 'x264', 'xvid']:
            superPrint("error", "File type error!", "This file is not a video (unknown mimetype AND invalid file extension):\n<i>" + path + "</i>")
            return False
    else:
        fileMimeType = fileMimeType.split('/', 1)
        if fileMimeType[0] != 'video':
            superPrint("error", "File type error!", "This file is not a video (unknown mimetype):\n<i>" + path + "</i>")
            return False

    return True

# ==== Hashing algorithm =======================================================
# Infos: http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
# This particular implementation is coming from SubDownloader: http://subdownloader.net/

def hashFile(path):
    """Produce a hash for a video file: size + 64bit chksum of the first and
    last 64k (even if they overlap because the file is smaller than 128k)"""
    try:
        longlongformat = 'Q' # unsigned long long little endian
        bytesize = struct.calcsize(longlongformat)
        format = "<%d%s" % (65536//bytesize, longlongformat)

        f = open(path, "rb")

        filesize = os.fstat(f.fileno()).st_size
        hash = filesize

        if filesize < 65536 * 2:
            superPrint("error", "File size error!", "File size error while generating hash for this file:\n<i>" + path + "</i>")
            return "SizeError"

        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)

        f.seek(-65536, os.SEEK_END) # size is always > 131072
        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)
        hash &= 0xFFFFFFFFFFFFFFFF

        f.close()
        returnedhash = "%016x" % hash
        return returnedhash

    except IOError:
        superPrint("error", "I/O error!", "Input/Output error while generating hash for this file:\n<i>" + path + "</i>")
        return "IOError"

# ==== Gnome selection window ==================================================

def selectionGnome(subtitlesList):
    """Gnome subtitles selection window using zenity"""
    searchMode = 'moviehash'
    subtitlesSelected = ''
    subtitlesItems = ''
    columnLn = ''
    columnHi = ''
    columnRate = ''
    columnCount = ''

    # Generate selection window content
    for item in subtitlesList['data']:
        if item['MatchedBy'] != 'moviehash':
            searchMode = item['MatchedBy']
        subtitlesItems += '"' + item['SubFileName'] + '" '

        if opt_selection_language == 'on':
            columnLn = '--column="Language" '
            subtitlesItems += '"' + item['LanguageName'] + '" '
        if opt_selection_rating == 'on':
            columnRate = '--column="Rating" '
            subtitlesItems += '"' + item['SubRating'] + '" '
        if opt_selection_count == 'on':
            columnCount = '--column="Downloads" '
            subtitlesItems += '"' + item['SubDownloadsCnt'] + '" '

    # Spawn zenity "list" dialog
    if searchMode == 'moviehash':
        process_subtitlesSelection = subprocess.Popen('zenity --width=' + str(opt_gui_width) + ' --height=' + str(opt_gui_height) + \
            ' --list --title="Synchronized subtitles for: ' + videoTitle + '"' + \
            ' --text="<b>Title:</b> ' + videoTitle + '\n<b>Filename:</b> ' + videoFileName + '"' + \
            ' --column="Available subtitles (synchronized)" ' + columnHi + columnLn + columnRate + columnCount + subtitlesItems,
            shell=True, stdout=subprocess.PIPE)
    else:
        process_subtitlesSelection = subprocess.Popen('zenity --width=' + str(opt_gui_width) + ' --height=' + str(opt_gui_height) + \
            ' --list --title="Subtitles found!"' + \
            ' --text="<b>Filename:</b> ' + videoFileName + '\n<b>>> These results comes from search by file name (not using movie hash) and may be unreliable...</b>"' + \
            ' --column="Available subtitles" ' + columnHi + columnLn + columnRate + columnCount + subtitlesItems,
            shell=True, stdout=subprocess.PIPE)

    # Get back the result
    result_subtitlesSelection = process_subtitlesSelection.communicate()

    # The results contain a subtitles?
    if result_subtitlesSelection[0]:
        if sys.version_info >= (3,0):
            subtitlesSelected = str(result_subtitlesSelection[0], 'utf-8').strip("\n")
        else: # python2
            subtitlesSelected = str(result_subtitlesSelection[0]).strip("\n")

        # Hack against recent zenity version?
        if len(subtitlesSelected.split("|")) > 1:
            if subtitlesSelected.split("|")[0] == subtitlesSelected.split("|")[1]:
                subtitlesSelected = subtitlesSelected.split("|")[0]
    else:
        if process_subtitlesSelection.returncode == 0:
            subtitlesSelected = subtitlesList['data'][0]['SubFileName']

    # Return the result
    return subtitlesSelected

# ==== KDE selection window ====================================================

def selectionKde(subtitlesList):
    """KDE subtitles selection window using kdialog"""
    return selectionAuto(subtitlesList)

# ==== CLI selection mode ======================================================

def selectionCLI(subtitlesList):
    """Command Line Interface, subtitles selection inside your current terminal"""
    subtitlesIndex = 0
    subtitlesItem = ''

    # Print video infos
    print("\n>> Title: " + videoTitle)
    print(">> Filename: " + videoFileName)

    # Print subtitles list on the terminal
    print(">> Available subtitles:")
    for item in subtitlesList['data']:
        subtitlesIndex += 1
        subtitlesItem = '"' + item['SubFileName'] + '" '
        if opt_selection_hi == 'on':
            if item['SubHearingImpaired'] == '1':
                subtitlesItem += '> "HI" '
        if opt_selection_language == 'on':
            subtitlesItem += '> "LanguageName: ' + item['LanguageName'] + '" '
        if opt_selection_rating == 'on':
            subtitlesItem += '> "SubRating: ' + item['SubRating'] + '" '
        if opt_selection_count == 'on':
            subtitlesItem += '> "SubDownloadsCnt: ' + item['SubDownloadsCnt'] + '" '
        print("\033[93m[" + str(subtitlesIndex) + "]\033[0m " + subtitlesItem)

    # Ask user selection
    print("\033[91m[0]\033[0m Cancel search")
    sub_selection = -1
    while( sub_selection < 0 or sub_selection > subtitlesIndex ):
        try:
            sub_selection = int(input(">> Enter your choice (0-" + str(subtitlesIndex) + "): "))
        except:
            sub_selection = -1

    # Return the result
    if sub_selection == 0:
        print("Cancelling search...")
        return
    else:
        return subtitlesList['data'][sub_selection-1]['SubFileName']

# ==== Automatic selection mode ================================================

def selectionAuto(subtitlesList,videoFileName):
    """Automatic subtitles selection using filename match"""

    print("function")

    videoFileParts = videoFileName.replace('-','.').replace(' ','.').replace('_','.').lower().split('.')
    maxScore = -1

    print("kjsbksdj")

    for subtitle in subtitlesList['data']:
        subFileParts = subtitle['SubFileName'].replace('-','.').replace(' ','.').replace('_','.').lower().split('.');
        score = 0
        if subtitle['MatchedBy'] == 'moviehash':
            score = score + 1 # extra point if the sub is found by hash, which is the preferred way to find subs
        for subPart in subFileParts:
            for filePart in videoFileParts:
                if subPart == filePart:
                    score = score + 1
        if score > maxScore:
            maxScore = score
            subtitlesSelected = subtitle['SubFileName']
            print(subtitlesSelected)

    return subtitlesSelected

# ==== Check dependencies ======================================================

def dependencyChecker():
    """Check the availability of tools used as dependencies"""

    if sys.version_info >= (3,3):
        for tool in ['gunzip', 'wget']:
            path = shutil.which(tool)
            if path is None:
                superPrint("error", "Missing dependency!", "The <b>'" + tool + "'</b> tool is not available, please install it!")
                return False

    return True

# ==== Main program (execution starts here) ====================================
# ==============================================================================

# ==== Argument parsing

# Get OpenSubtitlesDownload.py script path
def amit(path):
    opt_selection_mode = 'auto'
    result=path


# ==== Get valid video paths

    videoPathList = []

    if 'result' in locals():
        # Go through the paths taken from arguments, and extract only valid video paths
        for i in result:
            if checkFile(os.path.abspath(i)):
                videoPathList.append(os.path.abspath(i))

    # ==== Instances dispatcher

    # If videoPathList is empty, abort!
    if len(videoPathList) == 0:
        sys.exit(1)

    # The first video file will be processed by this instance
    videoPath = videoPathList[0]
    videoPathList.pop(0)

    # The remaining file(s) are dispatched to new instance(s) of this script
    for videoPathDispatch in videoPathList:

        # Handle current options
        command = execPath + " -g " + opt_gui
        if opt_selection_mode == 'auto':
            command += " -a "
        if opt_verbose == 'on':
            command += " -v "
        if not (len(opt_languages) == 1 and opt_languages[0] == 'eng'):
            for resultlangs in opt_languages:
                command += " -l " + resultlangs

        # Split command string
        command_splitted = command.split()
        # The videoPath filename can contain spaces, but we do not want to split that, so add it right after the split
        command_splitted.append(videoPathDispatch)

        if opt_gui == 'cli' and opt_selection_mode == 'manual':
            # Synchronous call
            process_videoDispatched = subprocess.call(command_splitted)
        else:
            # Asynchronous call
            process_videoDispatched = subprocess.Popen(command_splitted)

        # Do not spawn too many instances at the same time
        time.sleep(0.33)

    # ==== Search and download subtitles

    try:
        try:
            # Connection to opensubtitles.org server
            session = osd_server.LogIn(osd_username, osd_password, osd_language, 'opensubtitles-download 3.5')
        except Exception:
            # Retry once, it could be a momentary overloaded server?
            time.sleep(3)
            try:
                # Connection to opensubtitles.org server
                session = osd_server.LogIn(osd_username, osd_password, osd_language, 'opensubtitles-download 3.5')
            except Exception:
                # Failed connection attempts?
                superPrint("error", "Connection error!", "Unable to reach opensubtitles.org servers!\n\nPlease check:\n- Your Internet connection status\n- www.opensubtitles.org availability\n- Your downloads limit (200 subtitles per 24h)\nThe subtitles search and download service is powered by opensubtitles.org. Be sure to donate if you appreciate the service provided!")
                sys.exit(1)

        # Connection refused?
        if session['status'] != '200 OK':
            superPrint("error", "Connection error!", "Opensubtitles.org servers refused the connection: " + session['status'] + ".\n\nPlease check:\n- Your Internet connection status\n- www.opensubtitles.org availability\n- Your 200 downloads per 24h limit")
            sys.exit(1)

        searchLanguage = 0
        searchLanguageResult = 0
        videoTitle = 'Unknown video title'
        videoHash = hashFile(videoPath)
        videoSize = os.path.getsize(videoPath)
        videoFileName = os.path.basename(videoPath)

        print(videoFileName)

        # Count languages marked for this search
        for SubLanguageID in opt_languages:
            searchLanguage += len(SubLanguageID.split(','))


        # Search for available subtitles using file hash and size
        for SubLanguageID in opt_languages:
            print("in for")
            searchList = []
            searchList.append({'sublanguageid':SubLanguageID, 'moviehash':videoHash, 'moviebytesize':str(videoSize)})
            try:
                subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
            except Exception:
                # Retry once, we are already connected, the server is probably momentary overloaded
                time.sleep(3)
                try:
                    subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
                except Exception:
                    superPrint("error", "Search error!", "Unable to reach opensubtitles.org servers!\n<b>Search error</b>")

            # No results using search by hash? Retry with filename
            if (not subtitlesList['data']) and (opt_backup_searchbyname == 'on'):
                searchList = []
                searchList.append({'sublanguageid':SubLanguageID, 'query':videoFileName})
                try:
                    subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
                except Exception:
                    # Retry once, we are already connected, the server is probably momentary overloaded
                    time.sleep(3)
                    try:
                        subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
                    except Exception:
                        superPrint("error", "Search error!", "Unable to reach opensubtitles.org servers!\n<b>Search error</b>")
            else:
                opt_backup_searchbyname = 'off'

            # Parse the results of the XML-RPC query

            if subtitlesList['data']:

                # Mark search as successful
                searchLanguageResult += 1
                subtitlesSelected = ''

                # If there is only one subtitles, which wasn't found by filename, auto-select it
                if (len(subtitlesList['data']) == 1) and (opt_backup_searchbyname == 'off'):
                    subtitlesSelected = subtitlesList['data'][0]['SubFileName']

                # Get video title
                videoTitle = subtitlesList['data'][0]['MovieName']

                # Title and filename may need string sanitizing to avoid zenity/kdialog handling errors
                if opt_gui != 'cli':
                    videoTitle = videoTitle.replace('"', '\\"')
                    videoTitle = videoTitle.replace("'", "\'")
                    videoTitle = videoTitle.replace('`', '\`')
                    videoTitle = videoTitle.replace("&", "&amp;")
                    videoFileName = videoFileName.replace('"', '\\"')
                    videoFileName = videoFileName.replace("'", "\'")
                    videoFileName = videoFileName.replace('`', '\`')
                    videoFileName = videoFileName.replace("&", "&amp;")

                # If there is more than one subtitles and opt_selection_mode != 'auto',
                # then let the user decide which one will be downloaded
                if subtitlesSelected == '':
                    # Automatic subtitles selection?
                    if opt_selection_mode == 'auto':
                        print("10000")
                        subtitlesSelected = selectionAuto(subtitlesList,videoFileName)
                        print("1")
                    else:
                        # Go through the list of subtitles and handle 'auto' settings activation
                        for item in subtitlesList['data']:
                            if opt_selection_language == 'auto':
                                if searchLanguage > 1:
                                    opt_selection_language = 'on'
                            if opt_selection_hi == 'auto':
                                if item['SubHearingImpaired'] == '1':
                                    opt_selection_hi = 'on'
                            if opt_selection_rating == 'auto':
                                if item['SubRating'] != '0.0':
                                    opt_selection_rating = 'on'
                            if opt_selection_count == 'auto':
                                opt_selection_count = 'on'

                        # Spaw selection window
                        if opt_gui == 'gnome':
                            subtitlesSelected = selectionGnome(subtitlesList)
                        elif opt_gui == 'kde':
                            subtitlesSelected = selectionKde(subtitlesList)
                        else: # CLI
                            subtitlesSelected = selectionCLI(subtitlesList)

                # If a subtitles has been selected at this point, download it!
                if subtitlesSelected:
                    print("2")
                    subIndex = 0
                    subIndexTemp = 0

                    # Select the subtitles file to download
                    for item in subtitlesList['data']:
                        if item['SubFileName'] == subtitlesSelected:
                            subIndex = subIndexTemp
                            break
                        else:
                            subIndexTemp += 1

                    subLangId = '_' + subtitlesList['data'][subIndex]['ISO639']
                    subLangName = subtitlesList['data'][subIndex]['LanguageName']
                    subURL = subtitlesList['data'][subIndex]['SubDownloadLink']
                    subPath = videoPath.rsplit('.', 1)[0] + '.' + subtitlesList['data'][subIndex]['SubFormat']

                    # Write language code into the filename?
                    if ((opt_language_suffix == 'on') or
                        (opt_language_suffix == 'auto' and searchLanguageResult > 1)):
                        subPath = videoPath.rsplit('.', 1)[0] + subLangId + '.' + subtitlesList['data'][subIndex]['SubFormat']

                    # Escape non-alphanumeric characters from the subtitles path
                    subPath = re.escape(subPath)

                    # Download and unzip the selected subtitles (with progressbar)
                    if opt_gui == 'gnome':
                        process_subtitlesDownload = subprocess.call("(wget -q -O - " + subURL + " | gunzip > " + subPath + ") 2>&1" + ' | (zenity --auto-close --progress --pulsate --title="Downloading subtitles, please wait..." --text="Downloading <b>' + subtitlesList['data'][subIndex]['LanguageName'] + '</b> subtitles for <b>' + videoTitle + '</b>...")', shell=True)
                    elif opt_gui == 'kde':
                        process_subtitlesDownload = subprocess.call("(wget -q -O - " + subURL + " | gunzip > " + subPath + ") 2>&1", shell=True)
                    else: # CLI
                        print("wget -nv -O - " + subURL + " | gunzip > " + subPath)
                    
                        print(">> Downloading '" + subtitlesList['data'][subIndex]['LanguageName'] + "' subtitles for '" + videoTitle + "'")
                        process_subtitlesDownload = subprocess.call("wget -nv -O - " + subURL + " | gunzip > " + subPath, shell=True)

                    # If an error occur, say so
                    if process_subtitlesDownload != 0:
                        superPrint("error", "Subtitling error!", "An error occurred while downloading or writing <b>" + subtitlesList['data'][subIndex]['LanguageName'] + "</b> subtitles for <b>" + videoTitle + "</b>.")
                        osd_server.LogOut(session['token'])
                        return 

        # Print a message if no subtitles have been found, for any of the languages
        if searchLanguageResult == 0:
            superPrint("info", "No subtitles found for: " + videoFileName, '<b>No subtitles found</b> for this video:\n<i>' + videoFileName + '</i>')

        # Disconnect from opensubtitles.org server, then exit
        if session['token']: osd_server.LogOut(session['token'])
        return

    except (RuntimeError, TypeError, NameError, IOError, OSError):

        # An unknown error occur, let's apologize before exiting
        superPrint("error", "Unknown error!", "OpenSubtitlesDownload encountered an <b>unknown error</b>, sorry about that...\n\n" + \
                   "Error: <b>" + str(sys.exc_info()[0]).replace('<', '[').replace('>', ']') + "</b>\n\n" + \
                   "Just to be safe, please check:\n- www.opensubtitles.org availability\n- Your downloads limit (200 subtitles per 24h)\n- Your Internet connection status\n- That are using the latest version of this software ;-)")

        # Disconnect from opensubtitles.org server, then exit
        if session['token']: osd_server.LogOut(session['token'])
        return 
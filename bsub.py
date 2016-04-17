
# To download subtitle for the video

import mimetypes
import subprocess
import argparse
import time
import os
import re
import sys
import struct


if sys.version_info >= (3,0):
    import shutil
    import urllib.request
    from xmlrpc.client import ServerProxy, Error
else: # python2
    import urllib2
    from xmlrpclib import ServerProxy, Error


# To Print Error
def superPrint(priority, title, message):
    print(">> " + message)

# Check file path & file 
def checkFile(path):
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

#Hashing algorithm 
#Refered from  http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
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


# Selecting Best Matching Subtitle
# Automatic subtitles selection using filename match

def selectionAuto(subtitlesList,videoFileName):
    
    videoFileParts = videoFileName.replace('-','.').replace(' ','.').replace('_','.').lower().split('.')
    maxScore = -1

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

#Check dependencies
def dependencyChecker():
    if sys.version_info >= (3,3):
        for tool in ['gunzip', 'wget']:
            path = shutil.which(tool)
            if path is None:
                superPrint("error", "Missing dependency!", "The <b>'" + tool + "'</b> tool is not available, please install it!")
                return False

    return True


# Entry point to download subtitle
def getSubtitle(path):

    # Opensubtitles.org server settings 
    osd_server = ServerProxy('http://api.opensubtitles.org/xml-rpc')
    osd_username = 'Mediaplayer975'
    osd_password = '12345678'
    osd_language = 'en'

    # Language settings
    opt_languages = ['eng']
    opt_language_suffix = 'off'

    opt_gui = 'cli'
    opt_gui_width  = 720
    opt_gui_height = 320
    opt_backup_searchbyname = 'on'
    opt_selection_mode     = 'manual'
    opt_selection_language = 'off'
    opt_selection_hi       = 'auto'
    opt_selection_rating   = 'off'
    opt_selection_count    = 'off'
    opt_verbose            = 'off'

    execPath = str(sys.argv[0])
    opt_selection_mode = 'auto'
    result=path


    #Get valid video paths
    videoPathList = []

    if 'result' in locals():
        # Go through the paths taken from arguments, and extract only valid video paths
        for i in result:
            check=os.path.splitext(i)[0]
            if os.path.exists(check + ".srt"):
                print("found already "+i)
                continue
            if checkFile(os.path.abspath(i)):
                videoPathList.append(os.path.abspath(i))


    # If videoPathList is empty, abort!
    if len(videoPathList) == 0:
        return

    for videoPath in videoPathList:
    #For each file Search and download subtitles
 
        try:
            try:
                # Connection to opensubtitles.org server
                session = osd_server.LogIn(osd_username, osd_password, osd_language, 'opensubtitles-download 3.5')
            except Exception:
                superPrint("error", "Connection error!", "Unable to reach opensubtitles.org servers!\n\nPlease check:\n- Your Internet connection status\n- www.opensubtitles.org availability\n- Your downloads limit (200 subtitles per 24h)\nThe subtitles search and download service is powered by opensubtitles.org. Be sure to donate if you appreciate the service provided!")
                return

            # Connection refused?
            if session['status'] != '200 OK':
                superPrint("error", "Connection error!", "Opensubtitles.org servers refused the connection: " + session['status'] + ".\n\nPlease check:\n- Your Internet connection status\n- www.opensubtitles.org availability\n- Your 200 downloads per 24h limit")
                return

            searchLanguage = 0
            searchLanguageResult = 0
            videoTitle = 'Unknown video title'
            videoHash = hashFile(videoPath)
            videoSize = os.path.getsize(videoPath)
            videoFileName = os.path.basename(videoPath)

            # Count languages marked for this search
            for SubLanguageID in opt_languages:
                searchLanguage += len(SubLanguageID.split(','))


            # Search for available subtitles using file hash and size
            for SubLanguageID in opt_languages:

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

                            subtitlesSelected = selectionAuto(subtitlesList,videoFileName)
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
                        print(">> Downloading '" + subtitlesList['data'][subIndex]['LanguageName'] + "' subtitles for '" + videoTitle + "'")
                        process_subtitlesDownload = subprocess.call("(wget -q -O - " + subURL + " | gunzip > " + subPath + ")" ,shell=True)

                        # If an error occur, say so
                        if process_subtitlesDownload != 0:
                            superPrint("error", "Subtitling error!", "An error occurred while downloading or writing <b>" + subtitlesList['data'][subIndex]['LanguageName'] + "</b> subtitles for <b>" + videoTitle + "</b>.")
                            osd_server.LogOut(session['token'])
                            continue 

            # Print a message if no subtitles have been found, for any of the languages
            if searchLanguageResult == 0:
                superPrint("info", "No subtitles found for: " + videoFileName, 'No subtitles found for this video:\n' + videoFileName )

            # Disconnect from opensubtitles.org server, then exit
            if session['token']: osd_server.LogOut(session['token'])
            continue

        except (RuntimeError, TypeError, NameError, IOError, OSError):

            # An unknown error occur, let's apologize before exiting
            superPrint("error", "Unknown error!", "OpenSubtitlesDownload encountered an <b>unknown error</b>, sorry about that...\n\n" + \
                       "Error: <b>" + str(sys.exc_info()[0]).replace('<', '[').replace('>', ']') + "</b>\n\n" + \
                       "Just to be safe, please check:\n- www.opensubtitles.org availability\n- Your downloads limit (200 subtitles per 24h)\n- Your Internet connection status\n- That are using the latest version of this software ;-)")

            # Disconnect from opensubtitles.org server, then exit
            if session['token']: osd_server.LogOut(session['token'])
            continue 

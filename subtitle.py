import os
import sys
import logging
import requests,time,re,zipfile
from bs4 import BeautifulSoup


def sub_downloader(file_path):
	print("trying for second\n"+file_path)
	try:
		root, extension = os.path.splitext(file_path)
		if extension not in [".avi", ".mp4", ".mkv", ".mpg", ".mpeg", ".mov", ".rm", ".vob", ".wmv", ".flv", ".3gp",".3g2"]:
			return	
		if os.path.exists(root + ".srt"):
			return
		j=-1
		root2=root
		for i in range(0,len(root)):
			if(root[i]=="/"):
				j=i
		root=root2[j+1:]
		root2=root2[:j+1]
		r=requests.get("http://subscene.com/subtitles/release?q="+root);
		print("1 http://subscene.com/subtitles/release?q="+root+"\n$ "+root2)
		soup=BeautifulSoup(r.content,"lxml")
		atags=soup.find_all("a")
		href=""
		for i in range(0,len(atags)):
			spans=atags[i].find_all("span")
			if(len(spans)==2 and spans[0].get_text().strip()=="English"):
				href=atags[i].get("href").strip()	
				print("$$"+href)
		
	#	print(atags)print(spans)print(href)			
	
		if(len(href)>0):
			r=requests.get("http://subscene.com"+href);
			print("2 http://subscene.com"+href)
			soup=BeautifulSoup(r.content,"lxml")

			lin=soup.find_all('a',attrs={'id':'downloadButton'})[0].get("href")
			r=requests.get("http://subscene.com"+lin);
			print("3 http://subscene.com"+lin)

			soup=BeautifulSoup(r.content,"lxml")
			subfile=open(root2+".zip", 'wb')
			for chunk in r.iter_content(100000):
				subfile.write(chunk)
				subfile.close()
				time.sleep(1)
				zip=zipfile.ZipFile(root2+".zip")
				zip.extractall(root2)
				zip.close()
				os.unlink(root2+".zip")		
	except:
		#Ignore exception and continue
		print("Error in fetching subtitle for " + file_path)
		print("Error", sys.exc_info())
		logging.error("Error in fetching subtitle for " + file_path + str(sys.exc_info()))


def amit(path):
    root, _ = os.path.splitext(sys.argv[0])
    logging.basicConfig(filename=root + '.log', level=logging.INFO)
    logging.info("Started with params " + str(sys.argv))
	
    sub_downloader(path)

'''
    if len(sys.argv) == 1:
        print("This program requires at least one parameter")
        sys.exit(1)

    for path in sys.argv:
        if os.path.isdir(path):
            # Iterate the root directory recursively using os.walk and for each video file present get the subtitle
            for dir_path, _, file_names in os.walk(path):
                for filename in file_names:
                    file_path = os.path.join(dir_path, filename)
                    sub_downloader(file_path)
        else:
            sub_downloader(path)

'''


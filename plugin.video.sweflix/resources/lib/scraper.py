import urllib
import urllib2
import re
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import json
import HTMLParser
from BeautifulSoup import BeautifulSoup
from urllib import quote

# Add on info
__addon__        = xbmcaddon.Addon()
__addon_id__     = __addon__.getAddonInfo('id')
__addon_id_int__ = int(sys.argv[1])
__addon_dir__    = xbmc.translatePath(__addon__.getAddonInfo('path'))
__translation__    = __addon__.getLocalizedString
class scraper:
    global hdr
    hdr={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

def open_page(url):
    req = urllib2.Request(url, headers=hdr)
    response = urllib2.urlopen(req)
    json_object = json.load(response, encoding="UTF-8")
    response.close()
    return json_object

def get_categories(html=None):
    cats = {'ltst':__translation__(30022), 'pplr':__translation__(30021), 'rec':__translation__(30023), 'alpha': __translation__(30024)}
    return cats

def get_all_movies():
    url ='http://sweflix.com/api-v3/json.php?lim=9999'
    return open_page(url)

def get_all_movies_views():
    url ='http://sweflix.com/api-v3/json.php?lim=9999&orderBy=hits'
    return open_page(url)

def get_all_movies_alpha():
    url ='http://sweflix.com/api-v3/json.php?lim=9999&orderBy=titel&desc=false'
    return open_page(url)

def get_video_information(video):
    videoInfo={}
    videoInfo['id'] = video['id']
    videoInfo['rek'] = video['rek']
    videoInfo['titel'] = get_video_titel(video)
    videoInfo['logo'] = get_video_poster(video)
    videoInfo['url'] = get_video_url(video)
    videoInfo['plot'] = get_video_plot(video)
    videoInfo['genre'] = get_video_genre(video)
    videoInfo['imdbRating'] = get_video_imdbRate(video)
    videoInfo['year'] = get_video_year(video)
    videoInfo['duration'] = get_video_duration(video)
    #videoInfo['director'] = get_video_director(video)
    videoInfo['director'] = None

    return videoInfo

def get_video_titel(video):
    htmlEscaper = HTMLParser.HTMLParser()
    if video['titel']:
        if "&" in video['titel']:
            video['titel'].replace('&', 'and')
        return htmlEscaper.unescape(video['titel']).encode('utf-8')
    return False

def get_video_poster(video):
    if video['poster']:
        return video['poster']
    return False

def get_video_url(video):
    return video['mp4']

def get_video_plot(video):
    if video['plot']:
        return video['plot']
    return 'Did not find plot\nHittade inte handling.'

def get_video_genre(video):
    if video['cat']:
        genre = video['cat'].split(',')
        genres=''
        for each in genre:
            genres += each + ', '
        return genres.rstrip(', ')
    return 'test'


def get_video_subtitle(videoID):
    url ='http://sweflix.com/api-v3/json.php?id=' + videoID
    video_info=open_page(url)
    if video_info[0]['srt']:
        if "admin" in video_info[0]['srt']:
            subtitle=video_info[0]['srt'].split("/")
            return 'http://sweflix.com/beta57/admin/add/srt/' + quote(subtitle[len(subtitle)-1])
        return video_info[0]['srt']
    return ''

def get_video_imdbRate(video):
    if video['imdbrate']:
        return video['imdbrate']
    return None

def get_video_year(video):
    if video['year']:
        return int(video['year'])
    return None

def get_video_duration(video):
    if video['duration']:
        duration=video['duration']
        if "h" in duration:
            duration = duration.split("h")
            runtime=int(duration[0])*60
            duration =[int(s) for s in duration[1].split() if s.isdigit()]
            try:
                runtime += int(duration[0])
            except IndexError:
                'No minutes provided'
            return str(runtime) + ' minutes'
        else:
            return video['duration'] + 'utes'
    return None

def get_video_director(video):
    if video['imdb']:
        url ='http://www.omdbapi.com/?i=' + video['imdb']
        video_info=open_page(url)
        if video_info['Director']:
            return video_info['Director'].encode('utf-8')
    return None

if __name__ == '__main__':
    print 'Dev option'
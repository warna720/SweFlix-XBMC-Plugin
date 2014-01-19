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

def get_movie_menu():
    menu = {'ltst':__translation__(30022), 'pplr':__translation__(30021), 'rec':__translation__(30023), 'alpha': __translation__(30024), 
            'genres':__translation__(30020)}
    return menu

def get_movie_genres():
    genres = {  'Action':__translation__(30025), 'Adventure':__translation__(30026), 'Animation':__translation__(30027), 'Biography': __translation__(30028),
                'Comedy':__translation__(30029), 'Crime':__translation__(30030), 'Documentary':__translation__(30031), 'Drama':__translation__(30032), 
                'Family':__translation__(30033), 'Fantasy':__translation__(30034), 'History':__translation__(30035), 'Horror':__translation__(30036), 
                'Romance':__translation__(30037), 'Sci-Fi':__translation__(30038), 'Sport':__translation__(30039), 'Svenskt':__translation__(30040), 
                'Thriller':__translation__(30041)}
    return genres

def get_movie_genre(genre):
    return open_page('http://sweflix.com/api-v3/json.php?lim=9999&cat=' + genre)

def get_all_movies():
    url ='http://sweflix.com/api-v3/json.php?lim=9999'
    return open_page(url)

def get_all_movies_views():
    url ='http://sweflix.com/api-v3/json.php?lim=9999&orderBy=hits'
    return open_page(url)

def get_all_movies_alpha():
    url ='http://sweflix.com/api-v3/json.php?lim=9999&orderBy=titel&desc=false'
    return open_page(url)

def get_all_series():
    url ='http://sweflix.com/api-v3/json.php?lim=9999&orderBy=type'
    return open_page(url)

def get_all_shows(tid):
    url ='http://sweflix.com/api-v3/json-tv.php?lim=9999&desc=false&tid=' + tid
    return open_page(url)

def get_video_information(video):
    videoInfo={}
    videoInfo['id'] = video['id']
    videoInfo['tid'] = video['id']
    videoInfo['titel'] = get_video_titel(video)
    videoInfo['logo'] = get_video_poster(video)
    videoInfo['url'] = get_video_url(video)
    tvShow=False
    try:
        videoInfo['rek'] = video['rek']
        videoInfo['type'] = video['type']
        videoInfo['plot'] = get_video_plot(video)
        videoInfo['genre'] = get_video_genre(video)
        videoInfo['imdbRating'] = get_video_imdbRate(video)
        videoInfo['year'] = get_video_year(video)
        videoInfo['duration'] = get_video_duration(video)
        videoInfo['director'] = None
        videoInfo['trailer'] = None

        #videoInfo['director'] = get_video_director(video)
        #videoInfo['trailer'] = get_video_trailer(video)

        #Remove comment sign for the features that you want to activate
        #Warning, loading time will increase
    except KeyError:
        print 'Parameter rek, type, plot, genre, rating, year, duration, director and trailer is not available for the tv API'
        videoInfo['type'] = 'tv'
        videoInfo['plot'] = video['desc']
        tvShow=True
    if tvShow:
        try:
            videoInfo['titel'] = 'S' + video['tv_s'] + 'E' + video['tv_e'] + ' ' + videoInfo['titel']
        except TypeError:
            print 'got damn it sweflix, no titel for this id (in tv api):' + video['id']
    return videoInfo

def get_video_titel(video):
    htmlEscaper = HTMLParser.HTMLParser()
    if video['titel']:
        video['titel'] = htmlEscaper.unescape(video['titel']).encode('utf-8')
        return video['titel'].replace('&', 'and')

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
    return None


def get_video_subtitle(videoID):
    url ='http://sweflix.com/api-v3/json.php?id=' + videoID
    try:
        video_info=open_page(url)
        subtitleFound = True
    except ValueError:
        print 'No srt file for id: ' + videoID
        subtitleFound = False
    subtitlePath=False
    if subtitleFound:
        if video_info[0]['srt']:
            subtitlePath='srt'
        elif video_info[0]['srt2']:
            subtitlePath='srt2'
    if subtitlePath:
        if "admin" in video_info[0][subtitlePath]:
            subtitle=video_info[0][subtitlePath].split("/")
            return 'http://sweflix.com/beta57/admin/add/srt/' + quote(subtitle[len(subtitle)-1])
        return video_info[0][subtitlePath]
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
                print 'No minutes provided for video: ' + video['titel']
            return str(runtime)
        elif 'N/A' in video['duration']:
            return 1
        else:
            return video['duration'].replace(' min','')
    return None

def get_video_director(video):
    if video['imdb']:
        url ='http://www.omdbapi.com/?i=' + video['imdb']
        video_info=open_page(url)
        if video_info['Director']:
            return video_info['Director'].encode('utf-8')
    return None

def get_video_trailer(video):
    url=''
    if video['titel']:
        youtube_id = open_page("http://c13.cdn.secure.media.sweflix.com/api/trailer-api2.php?q=" + video['titel'].replace(' ', '%20'))
        url = ("plugin://plugin.video.youtube/?path=/root/video"
                "&action=play_video&videoid={0}").format(youtube_id[0]['id'])
    return url

if __name__ == '__main__':
    print 'Dev option'
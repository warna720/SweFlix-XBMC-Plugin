#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
__settings__     = xbmcaddon.Addon(id='plugin.video.sweflix')

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
    json_object = get_json(response)
    response.close()
    return json_object

def get_json(response):
    return json.load(response, encoding="UTF-8")

def auth_user():
    url = 'https://sweflix.net/api-v3/auth.php'
    username = __settings__.getSetting("username")
    password = __settings__.getSetting("password")
    #Password is already hashed with SHA256, no need to worry.

    data = urllib.urlencode({"username":username, "password": password})
    req = urllib2.Request(url, data, headers=hdr)
    response = urllib2.urlopen(req)
    try:
        json_object = get_json(response)
    except ValueError:
        return False
    response.close()
    if(json_object):
        return True
    return False

def getURL(videoType=''):
    #HOTFIX for cat + prm = 500
    #When fixed, remove "=''" from params
    #And put "movie" as param for "get_movie_genre"

    url = 'https://sweflix.net/api-v3/json.php?lim=9999&auth=d2873ty083q7eduq0387t498ujd02398t2'
    TVurl = 'https://sweflix.net/api-v3/json-tv.php?lim=9999&auth=d9e8yq8o3hf98247yg8234'
    premium = '&prm=0'
    if auth_user():
        premium = '&prm=1'
    if (videoType == 'movie'):
        return url + premium
    elif(videoType == 'tv'):
        return TVurl + premium
    return url

def get_movie_menu():
    menu = {'ltst':__translation__(30022), 'pplr':__translation__(30021), 'rec':__translation__(30023), 
        'alpha': __translation__(30024), 'genres':__translation__(30020), 'prem':__translation__(30025)}
    return menu

def get_movie_genres():
    genres = {  'Action':__translation__(30035), 'Adventure':__translation__(30036), 'Animation':__translation__(30037), 'Biography': __translation__(30038),
                'Comedy':__translation__(30039), 'Crime':__translation__(30040), 'Documentary':__translation__(30041), 'Drama':__translation__(30042), 
                'Family':__translation__(30043), 'Fantasy':__translation__(30044), 'History':__translation__(30045), 'Horror':__translation__(30046), 
                'Romance':__translation__(30047), 'Sci-Fi':__translation__(30048), 'Sport':__translation__(30049), 'Svenskt':__translation__(30050), 
                'Thriller':__translation__(30051)}
    return genres

def get_movie_genre(genre):
    return open_page(getURL() + '&cat=' + genre)

def get_all_movies():
    return open_page(getURL('movie'))

def get_all_movies_views():
    return open_page(getURL('movie') + '&orderBy=hits')

def get_all_movies_alpha():
    return open_page(getURL('movie') + '&orderBy=titel&desc=false')

def get_all_series():
    return open_page(getURL('movie') + '&orderBy=type')

def get_all_shows(tid):
    return open_page(getURL('tv') + '&desc=false&tid=' + tid)

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
        videoInfo['premium'] = get_video_premium(video)

        videoInfo['trailer'] = None
        videoInfo['director'] = None

        #videoInfo['trailer'] = get_video_trailer(video)
        #Dont uncomment the line above, because it's not needed right now as the 
        #trailers load only when it's requested resulting in significantly reduced loading times.

        #videoInfo['director'] = get_video_director(video)
        #Uncomment the line above to get more videoinformation.
        #Warning, loading time will increase.

    except KeyError:
        print 'Parameter rek, type, plot, genre, rating, year, duration, director and trailer is not available for the tv API'
        videoInfo['type'] = 'tv'
        videoInfo['plot'] = video['desc']
        videoInfo['duration'] = 1
        tvShow=True
    if tvShow:
        try:
            videoInfo['titel'] = 'S' + video['tv_s'] + 'E' + video['tv_e'] + ' ' + videoInfo['titel']
        except TypeError:
            print 'Got damn it sweflix, no titel for this id (in tv api):' + video['id']
    return videoInfo

def get_video_titel(video):
    htmlEscaper = HTMLParser.HTMLParser()
    if video['titel']:
        video['titel'] = htmlEscaper.unescape(video['titel']).encode('utf-8')
        return video['titel']
    return 'Error: Title is Null'

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

def get_video_premium(video):
    if (video['premium'] == '1'):
        return '1'
    return '0'

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
                print 'No minutes provided for videoID: ' + video['id']
            return str(runtime)
        elif 'N/A' in video['duration']:
            return 1
        else:
            return video['duration'].replace(' min','')
    return 0

def get_video_director(video):
    if video['imdb']:
        url ='http://www.omdbapi.com/?i=' + video['imdb']
        video_info=open_page(url)
        if video_info['Director']:
            return video_info['Director'].encode('utf-8')
    return None

def get_video_trailer(title):
    youtube_id = open_page("https://static2.sweflix.net/api/trailer-api2.php?q=" + title.replace('%20', ' '))
    url = ("plugin://plugin.video.youtube/?path=/root/video"
                    "&action=play_video&videoid={0}").format(youtube_id[0]['id'])
    return url

def get_not_premium_message():
    url = ("plugin://plugin.video.youtube/?path=/root/video"
                    "&action=play_video&videoid={0}").format("15_Y3_eRfOU")
    data = {"titel": "You are not premium :(", "premium":"1", 
            "id":"None", "plot":"", 
            "logo":"http://c3.cdn.sweflix.com/sweflxlogo2.png", "url":url}
    json_object = []
    json_object.append(data)

    return json_object

if __name__ == '__main__':
    print 'Dev option'
import re
import sys
from urllib import quote, unquote
import xbmcaddon
from resources.lib import scraper, utils
import xbmc
import HTMLParser
__addon__        = xbmcaddon.Addon()
__translation__  = __addon__.getLocalizedString

def add_directory(titel=None, mode=None, logo=None, url=None, plot=None, 
                    genre=None, year=None, rating=None, duration=None, 
                    director=None, trailer=None, videotype=''):
    if not logo:
        logo = 'http://c3.cdn.sweflix.com/sweflxlogo2.png'
    if 'tv' not in videotype:
        titel = titel.encode('utf-8')
    utils.add_directory_link(titel, 
                                logo, 
                                mode, 
                                '', 
                                plot=plot, 
                                trailer=trailer,
                                is_folder=True, 
                                is_playable=False, 
                                total_items=20)

def add_tv_shows(tv):
    add_directory(tv['titel'], 'tv-' + tv['tid'], tv['logo'], '', tv['plot'], 
                    tv['genre'], tv['year'], tv['imdbRating'], tv['duration'], 
                    tv['director'], tv['trailer'], tv['type'])

def add_video(video):
    htmlEscaper = HTMLParser.HTMLParser()
    try:
        genre = video['genre']
        year = video['year']
        rating = video['imdbRating']
        duration = video['duration']
        director = video['director']
        trailer = video['trailer']

    except KeyError:
        genre = None
        year = None
        rating = None
        duration = None
        director = None
        trailer = None

    try:
        utils.add_directory_link(video['titel'], 
                                    video['logo'], 
                                    'play_video', 
                                    video['url'],
                                    plot=htmlEscaper.unescape(video['plot']),
                                    genre=genre,
                                    year=year,
                                    rating=rating,
                                    duration=duration,
                                    director=director,
                                    srt=video['id'],
                                    trailer=trailer,
                                    is_folder=False, 
                                    is_playable=True,
                                    total_items=1)
    except TypeError:
        print_video_error(video)

def add_tv_show(show):
    add_video(show)

def print_video_error(video):
    print type(video['titel'])
    print video['titel']
    print 'your fucking titel is null in your db, fix it sweflix.'

def main(params):
    if not params.has_key('mode') or params['mode'] == 'categeories':
        add_directory(__translation__(30016), 'movies')
        add_directory(__translation__(30017), 'series')

    elif params['mode'] == 'movies':
        logo = 'http://c3.cdn.sweflix.com/sweflxlogo2.png'
        movie_menu = scraper.get_movie_menu()
        for mode, titel in movie_menu.iteritems():
            add_directory(titel, mode)

    elif params['mode'] == 'ltst':
        videos = scraper.get_all_movies()
        for vid in videos:
            video = scraper.get_video_information(vid)
            add_video(video)

    elif params['mode'] == 'rec':
        videos=scraper.get_all_movies()
        for vid in videos:
            video = scraper.get_video_information(vid)
            if video['rek'] == '1':
                add_video(video)

    elif params['mode'] == 'pplr':
        videos=scraper.get_all_movies_views()
        for vid in videos:
            video = scraper.get_video_information(vid)
            add_video(video)
                
    elif params['mode'] == 'alpha':
        videos=scraper.get_all_movies_alpha()
        for vid in videos:
            video = scraper.get_video_information(vid)
            add_video(video)

    elif 'genres' in params['mode']:
        if '-' in params['mode']:
            genre = params['mode'].split('-')
            videos = scraper.get_movie_genre(genre[1])

            for vid in videos:
                video = scraper.get_video_information(vid)
                add_video(video)
        else:
            genres = scraper.get_movie_genres()
            for mode, titel in genres.iteritems():
                add_directory(titel, 'genres-' + mode)

    elif params['mode'] == 'series':
        htmlEscaper = HTMLParser.HTMLParser()
        shows = scraper.get_all_series()
        for show in shows:
            if show['type'] == 'tv':
                video = scraper.get_video_information(show)
                add_tv_shows(video)

    elif 'tv-' in params['mode']:
        tid = params['mode'].split('-')
        shows = scraper.get_all_shows(tid[1])
        for show in shows:
            video = scraper.get_video_information(show)
            add_tv_show(video)

    elif params['mode'] == 'play_video':
        utils.play_video(params['url'])
        subtitles=scraper.get_video_subtitle(params['srt'])
        player = xbmc.Player()
        while not xbmc.Player().isPlaying():
            xbmc.sleep(10000)
        player.setSubtitles(subtitles)
    utils.end_directory()

if __name__ == '__main__':
    params = utils.get_params()
    print params
    main(params)
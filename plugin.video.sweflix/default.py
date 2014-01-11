import re
import sys
from urllib import quote, unquote
import xbmcaddon
from resources.lib import scraper, utils
import xbmc
import HTMLParser
__addon__        = xbmcaddon.Addon()
__translation__  = __addon__.getLocalizedString

def add_directory(titel, mode):
    logo = 'http://c3.cdn.sweflix.com/sweflxlogo2.png'
    utils.add_directory_link(titel.encode('utf-8'), 
                                     logo, 
                                     mode, 
                                     '', 
                                     is_folder=True, 
                                     is_playable=False, 
                                     total_items=20)

def add_video(video):
    if 'tv' not in params['mode']:
        if video['type'] == 'film':
            htmlEscaper = HTMLParser.HTMLParser()
            try:
                utils.add_directory_link(video['titel'], 
                                            video['logo'], 
                                            'play_video', 
                                            video['url'],
                                            plot=htmlEscaper.unescape(video['plot']),
                                            cat=video['genre'],
                                            year=video['year'],
                                            rating=video['imdbRating'],
                                            duration=video['duration'],
                                            director=video['director'],
                                            srt=video['id'],
                                            is_folder=False, 
                                            is_playable=True,
                                            total_items=1)
            except TypeError:
                print_video_error(video)

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
        print 'to be coded'

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
    main(params)
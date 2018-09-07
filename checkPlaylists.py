import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import webbrowser
import os
import sys
import spotipy.util as util
from json.decoder import JSONDecodeError


username = "herman.rommetveit"
scope = 'user-read-private user-read-playback-state user-modify-playback-state'
#client_credentials_manager = SpotifyClientCredentials(client_id='001037844ee04932b6d967bbbf011e2e',
#                                                      client_secret='fad660f0e7724d9b905d8ee76a85bc5d')
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

try:
    token = util.prompt_for_user_token(username, scope, redirect_uri='https://example.com/')
except (AttributeError, JSONDecodeError):
    os.remove(".cache-{herman.rommetveit}")
    token = util.prompt_for_user_token(username, scope)

sp = spotipy.client.Spotify(auth=token)
devices = sp.devices()
print(json.dumps(devices, sort_keys=True, indent=4))
deviceID = devices['devices'][0]['id']

def getCurrentPlayingInfo():
    #print(json.dumps(devices,sort_keys=True,indent=4))
    track = sp.current_user_playing_track()
    artist = track['item']['artists'][0]['name']
    TheTrack = track['item']['name']

    if artist != "":
        print("Currently playing " + artist + " - " + TheTrack)


def getUserInfo():
    user = sp.current_user()
    #print(json.dumps(user, sort_keys=True, indent=4))
    displayName = user['id']
    followers = user['followers']['total']
    return displayName, followers

def getAllPlaylistsWithSongs():
    playlists = sp.user_playlists(username)
    i = 0
    x = -1
    trackURis = []
    for playlist in playlists["items"]:
        print("Playlist", str(i + 1) + ":", playlist['name'])
        print("########################################")
        i += 1
        tracks = sp.user_playlist_tracks(username, playlist_id=playlist['id'], fields=None, limit=100)
        #print(json.dumps(tracks, sort_keys=True, indent=4))
        print("Songs: ")
        for track in tracks['items']:
            trackURis.append(track['track']['uri'])
            print(str(x + 1) + ":", track['track']['artists'][0]['name'] + " - " + track['track']['name'])
            x += 1
        print()

        # See album art and play song
    while True:
        trackSelectionList = []
        deviceSelectionList = devices['devices']
        try:
            Songselected = input("Enter a song number to see the album art and play the song ('e' for exit):")
            if Songselected == "e":
                intro()
                break
            trackSelectionList.append(trackURis[int(Songselected)])
            print("To which device do you want to play the song?")
            i = 0
            while i < len(deviceSelectionList):
                print(str(i+1) + ": " + deviceSelectionList[i]['name'])
                i += 1
            num = input("Choice: ")

            sp.start_playback(deviceSelectionList[int(num) - 1]['id'], None, trackSelectionList)

        except ValueError:
            print("Not a valid number.")
        except IndexError:
            print("That number does not correspond to a song.")

def getArtist():
    query = input("Search for a artist name: ")

    try:
        searchRes = sp.search(query, 1, 0, "artist")
        #print(json.dumps(searchRes, sort_keys=True, indent=4))
        artist = searchRes['artists']['items'][0]
        print(artist['name'], "has", str(artist['followers']['total']), "followers")
        print(artist['name'], "plays", artist['genres'][0])
        print()
        webbrowser.open(artist['images'][0]['url'])
        artistID = artist['id']
        getAlbums(artistID)
    except IndexError:
        print("Sorry, can't find that artist. Check for spelling errors.")

def getAlbums(artistID):
    TrackURIs = []
    TrackArt = []
    z = 0

    AlbumRes = sp.artist_albums(artistID)
    AlbumResItems = AlbumRes['items']
    #print(json.dumps(AlbumRes, sort_keys=True, indent=4))

    for item in AlbumResItems:
        print("ALBUM: " + item['name'])
        albumID = item['id']
        albumArt = item['images'][0]['url']

        #Tracks
        trackRes = sp.album_tracks(albumID)
        trackResItems = trackRes['items']
        for track in trackResItems:
            print(str(z) + ": " + track['name'])
            TrackURIs.append(track['uri'])
            TrackArt.append(albumArt)
            z += 1
        print()

    #See album art and play song
    while True:
        trackSelectionList = []
        try:
            Songselected = input("Enter a song number to see the album art and play the song ('e' for exit):")
            if Songselected == "e":
                intro()
                break
            trackSelectionList.append(TrackURIs[int(Songselected)])
            sp.start_playback(deviceID, None, trackSelectionList)
            webbrowser.open(TrackArt[int(Songselected)])
        except ValueError:
            print("Not a valid number.")
        except IndexError:
            print("That number does not correspond to a song.")

def intro():
    displayName, followers = getUserInfo()
    print("Welcome to spotipy " + str(displayName))
    print("You have " + str(followers) + " followers")
    print()
    print("Here are your choices: ")
    print("0: see all your playlists and songs")
    print("1: Search for an artist and play a song")
    print("2: Get current playing song")
    print("bye: exit program")
    print()

def main():
    intro()

    while True:
        choice = input("SO, what do you want to do? Choose: ")

        if choice == "0":
            getAllPlaylistsWithSongs()
        if choice == "1":
            getArtist()
        if choice == "2":
            getCurrentPlayingInfo()
        if choice == "bye":
            print("bye")
            break


main()

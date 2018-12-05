from __future__ import print_function
import sys
import spotipy
import spotipy.util as util
import os
from json.decoder import JSONDecodeError
import json
import oauth2
import re
import jellyfish
from SpotifyUserData import username, clientid, clientsecret

scope = 'user-library-read, playlist-modify-private, playlist-modify-private'


def prompt_for_user_token(username, scope, client_id = clientid,
        client_secret = clientsecret, redirect_uri = "http://google.com/", cache_path = "C:/Users/noelc/Desktop/Code/Spotifile/"):
    ''' prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor
        Parameters:
         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app
         - cache_path - path to location to save tokens
    '''

    if not client_id:
        client_id = os.getenv(clientid)

    if not client_secret:
        client_secret = os.getenv(clientsecret)

    if not redirect_uri:
        redirect_uri = os.getenv('http://google.com/')

    if not client_id:
        print('''
            You need to set your Spotify API credentials. You can do this by
            setting environment variables like so:
            export SPOTIPY_CLIENT_ID='your-spotify-client-id'
            export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
            export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
            Get your credentials at
                https://developer.spotify.com/my-applications
        ''')
        raise spotipy.SpotifyException(550, -1, 'no credentials set')

    cache_path = cache_path or ".cache-" + username
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri,
        scope=scope, cache_path=cache_path)

    # try to get a valid token for this user, from the cache,
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        print('''
            User authentication requires interaction with your
            web browser. Once you enter your credentials and
            give authorization, you will be redirected to
            a url.  Paste that url you were directed to to
            complete the authorization.
        ''')
        auth_url = sp_oauth.get_authorize_url()
        try:
            import webbrowser
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except:
            print("Please navigate here: %s" % auth_url)

        print()
        print()
        try:
            response = raw_input("Enter the URL you were redirected to: ")
        except NameError:
            response = input("Enter the URL you were redirected to: ")

        print()
        print()

        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
    # Auth'ed API request
    if token_info:
        return token_info['access_token']
    else:
        return None


try:
    sp = spotipy.Spotify(auth=token_info)
except:
    try:
        token_info = util.prompt_for_user_token(username,scope,client_id=clientid,client_secret=clientsecret,redirect_uri='http://google.com/')
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{username}")
        token_info = util.prompt_for_user_token(username,scope,client_id=clientid,client_secret=clientsecret,redirect_uri='http://google.com/')

try:
    sp = spotipy.Spotify(auth=token_info)
except:
    print("not auth")

#Get User's playlists
userplaylists = sp.current_user_playlists()

#Create new playlist
playlistname = input("Enter your playlist name: ")
if len(playlistname) < 1:
    playlistname = "Spotifile"
sf_playlist = sp.user_playlist_create(username, playlistname, public=False)
sf_playlist_id = sf_playlist["id"]

#Create search query list from file or directory search
querylist = []
qtracknames = []
qartistnames = []

#Searches chosen directory for .aiff files. Returns tuple as (tracknames, artistnames)
filedir = input("Enter the directory of your music folder: ")
from filewalk2 import filewalk as fw
if len(filedir) < 1:
    querylist.extend(fw())
else:
    querylist.extend(fw(filedir))

#Stores track and artist names seperately for search step
qtracknames = querylist[0]
qartistnames = querylist[1]

#Search for track and add it to playlist
track_name = []
track_id = []
addcount = 0

qtracknames2 = []
qartistnames2 = []

qtracknames3 = []
qartistnames3 = []

qtracknames4 = []
qartistnames4 = []

qtracknames5 = []
qartistnames5 = []
#Searching for tracknames
print("Round 1:", len(qtracknames), "tracks")
for n, q in enumerate(qtracknames):
    tracksearch = sp.search(q, limit=50, offset=0, type='track', market=None)
    added = False
#Looping through search results to find closest track
#If trackname distance is > 0.8 then check artist names
#If artistname distance is > 0.8 then add track id and name to lists
    for item in tracksearch["tracks"]["items"]:
        tname = item["name"]
        tdist = jellyfish.jaro_winkler(tname, q)
        if tdist > 0.8:
            for art in item["artists"]:
                aname = art["name"]
                adist = jellyfish.jaro_winkler(aname, qartistnames[n])
                if adist > 0.8:
                    track_id.append(item["id"])
                    track_name.append(tname)
                    added = True
                    addcount = addcount + 1
                    print("Found:", item["id"], tname)
                    break
        if added == True: break

    if added == False:
        qtracknames2.append(q)
        qartistnames2.append(qartistnames[n])

#Round 2: Searching for track without "(Original Mix)"
for n, q in enumerate(qtracknames2):
    if re.search("(.+?)(?=\(Original Mix\))", q):
        qtracknames2[n] = re.search("(.+?)(?=\s\(Original Mix\))", q).group()


print("Round 2:", len(qtracknames2), "tracks")
if qtracknames2:
    for n, q in enumerate(qtracknames2):
        omixsearch = sp.search(q, limit=50, offset=0, type='track', market=None)
        added2 = False
        for item in omixsearch["tracks"]["items"]:
            tname = item["name"]
            tdist = jellyfish.jaro_winkler(tname, q)
            if tdist > 0.8:
                for art in item["artists"]:
                    aname = art["name"]
                    adist = jellyfish.jaro_winkler(aname, qartistnames2[n])
                    if adist > 0.8:
                        track_id.append(item["id"])
                        track_name.append(tname)
                        added2 = True
                        addcount = addcount + 1
                        print("Found:", item["id"], tname)
                        break
            if added2 == True: break

        if added2 == False:
            qtracknames3.append(q)
            qartistnames3.append(qartistnames2[n])

#Round 3: searching for artist name and track name without "(Original Mix)"
print("Round 3:", len(qtracknames3), "tracks")
if qtracknames3:
    for n, q in enumerate(qtracknames3):
        aandtsearch = sp.search(qartistnames3[n] + " " + q, limit=50, offset=0, type='track', market=None)
        added3 = False
        for item in aandtsearch["tracks"]["items"]:
            tname = item["name"]
            tdist = jellyfish.jaro_winkler(tname, q)
            if tdist > 0.8:
                for art in item["artists"]:
                    aname = art["name"]
                    adist = jellyfish.jaro_winkler(aname, qartistnames3[n])
                    if adist > 0.8:
                        track_id.append(item["id"])
                        track_name.append(tname)
                        added3 = True
                        addcount = addcount + 1
                        print("Found:", item["id"], tname)
                        break
            if added3 == True: break

        if added3 == False:
            qtracknames4.append(q)
            qartistnames4.append(qartistnames3[n])

#Round 4: removing any featuring artists from track names
for n, q in enumerate(qtracknames4):
    a = q.split("feat.")
    if len(a) > 1:
        if re.search("(?=\(.*\))", a[1]):
            aappend = re.search("(\(.*\))", a[1]).group(0)
            qtracknames4[n] = a[0].strip() + " " + aappend.strip()
        else:
            qtracknames4[n] = a[0].strip()

    b = q.split("Feat.")
    if len(b) > 1:
        if re.search("(?=\(.*\))", b[1]):
            bappend = re.search("(\(.*\))", b[1]).group(0)
            qtracknames4[n] = b[0].strip() + " " + bappend.strip()
        else:
            qtracknames4[n] = b[0].strip()

print("Round 4:", len(qtracknames4), "tracks")
if qtracknames4:
    for n, q in enumerate(qtracknames4):
        featsearch = sp.search(q, limit=50, offset=0, type='track', market=None)
        added4 = False
        for item in featsearch["tracks"]["items"]:
            tname = item["name"]
            tdist = jellyfish.jaro_winkler(tname, q)
            if tdist > 0.8:
                for art in item["artists"]:
                    aname = art["name"]
                    adist = jellyfish.jaro_winkler(aname, qartistnames4[n])
                    if adist > 0.8:
                        track_id.append(item["id"])
                        track_name.append(tname)
                        added4 = True
                        addcount = addcount + 1
                        print("Found:", item["id"], tname)
                        break
            if added4 == True: break

        if added4 == False:
            qtracknames5.append(q)
            qartistnames5.append(qartistnames4[n])

#Saving track ids for future purposes
ftrackid = open("ftrackid.py", "w")
ftrackid.write(str(track_id))
ftrackid.close()

#Adding tracks to playlist. Since sp.user_playlist_add_tracks() breaks at a certain point, I decided to send it chunks of 50 track IDs at a time
print("Attempting to add: ", len(track_id), "tracks.")
for i in range(0, len(track_id), 50):
    chunk = track_id[i:i + 50]
    try:
        sp.user_playlist_add_tracks(username, sf_playlist_id, chunk, position=None)
    except:
        print("Failed to add tracks to playlist")

print("Successfully added", addcount, "tracks")
print("Failed to add", len(qtracknames)-addcount, "tracks")
print("Ratio:", addcount/len(qtracknames))

for n, q in enumerate(qtracknames5):
    if not qartistnames5 or not qtracknames5: break
    print("Failed to add:", qartistnames5[n], "-", qtracknames5[n])

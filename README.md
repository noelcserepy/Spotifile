# Welcome to Spotifile

The easy way to locate aiff files on your hard drive and add them to a new Spotify playlist. 
This is my first coding project so I'm sure many things can be improved. If you have any suggestions, let me know. 
You can of course also commit to Spotifile. Enjoy!

# Dependencies:

- pip install spotipy
- pip install python-oauth2
- pip install jellyfish
- pip install mutagen

# How to use:

Step 1:
Enter your Spotify API client_id, client_secret and Spotify Username in the file "SpotifyUserData.py"

Step 2:
Run spotifile.py, name your playlist and enter the directory to search in.

Step 3:
Enjoy watching the tracks being added to Spotify.

# Limitations:

- Momentarily this application only supports .aiff files.
- Spotifile depends on the proper labelling of music files with track and artist name (such as when bought).
- Not every song you may have on your hard drive exists in the Spotify library and therefore cannot be added. You will see a list at the end of the program if any songs were not added to your playlist. These will have to be added manually.

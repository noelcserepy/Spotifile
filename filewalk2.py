def filewalk(path="C:/Users/noelc/Desktop/Musig"):
    from os import walk
    import os.path
    import re
    import mutagen.aiff


# Walk dir and make a list of paths
    fpaths = []
    fnames = []
    for (dirpath, dirnames, filenames) in walk(path):
        for name in filenames:
            pths = os.path.abspath(os.path.join(dirpath, name))
            pypths = re.sub("\\\\", "/", pths)
            if re.search("(.*)\.aiff$", pypths):
                fpaths.append(pypths)
            else: continue
    print("Paths created:", len(fpaths))


# Open each file from path and save title and artist
    tracknames = []
    artistnames = []
    for path in fpaths:
        metadata = mutagen.aiff.Open(path)
        tracktag = metadata["TIT2"].pprint()
        tracknames.append(tracktag[5:])
        artisttag = metadata["TPE1"].pprint()
        artistnames.append(artisttag[5:])
    print("Tracks saved:", len(tracknames))
    # print(tracknames)
    # print(artistnames)


# Cleaning results by removing index numbers of songs eg. "01. bla bla bla"
    removed = 0
    for n, track in enumerate(tracknames):
        if re.search("^[0-9]+\.\s(.*)", track):
            tracknames[n] = re.search("^[0-9]+\.\s(.*)", track).group(1).strip()
            removed = removed + 1
        else: continue
    print("Indexes cleaned:", removed)
    print("Tracks in list:", len(tracknames))


# Merging artist and track lists to create a list of search queries
    querylist = []
    for n, track in enumerate(tracknames):
        querylist.append(artistnames[n] + " " + track)

    return tracknames, artistnames

filewalk()

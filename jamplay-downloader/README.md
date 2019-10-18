# JamPlay Downloader

## Overview

Script to automate downloading a full video series from www.jamplay.com along
with all supplemental materials. The intended use is for materials you've
already purchased; it's just much more convenient to let the script do its
job for an 50+ part series than to babysit it for hours on end.


## Dependencies

- Python 2.7+
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/)
- wget


## Usage

```
download-jamplay-lesson.py SERIES_URL OUT_PATH QUALITY COOKIE
```

`SERIES_URL` is the URL of the plain HTML page that contains links to all the
lessons in the series (so it's *not* the video player page!)

`OUT_PATH` must be an existing directoy (all downloaded files will be placed
here, no subfolders will be created).

`QUALITY` must be one of the following (note that `720p` often denotes 1080p
videos): `4K`, `720p`, `Super`, `High`, `Medium` or `Low`.

This is the easiest way to get hold of the session `COOKIE`:

1. Log in to JamPlay in Firefox
2. Open the **Developer Tools** and go to the **Network** tab
3. Refresh the page to make sure some traffic is logged
4. Right-click on any request to `members.jamplay.com` and copy it with **Copy
as cURL Request**
5. Extract the session cookie from the cURL command (the string right after
the `-H "Cookie:` part that starts with `__cfduid`; make sure to put the
entire string in double quotes!)


## License

Copyright © 2013-2019 John Novak <<john@johnnovak.net>>

This work is free. You can redistribute it and/or modify it under the terms of
the [Do What The Fuck You Want To Public License, Version
2](http://www.wtfpl.net/), as published
by Sam Hocevar. See the [COPYING](./COPYING) file for more details.


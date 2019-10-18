#!/usr/bin/env python

# --------------------------------------------------------------------------
# Script to download a full video series from www.jamplay.com
# Written by John Novak <john@johnnovak.net>, 2019
#
# Requires Python 2.7+, Beautiful Soup 4 and wget
# --------------------------------------------------------------------------

from bs4 import BeautifulSoup
from pprint import pprint

import json, os, sys, urllib2, re

DRY_RUN = 0

SERIES_URL_PREFIX = 'http://members.jamplay.com/ajax/lessons/v2/series?lesson_id='
PLAYLIST_URL_PREFIX = 'http://members.jamplay.com/ajax/lessons/v2/playlist?lesson_id='
SUPPLEMENTAL_DL_URL_PREFIX = 'http://www-ecs.jamplay.com/uploads/lessons/supplemental/'

VIDEO_QUALITIES = ['4K', '720p', 'Super', 'High', 'Medium', 'Low']


def info(message):
  print message


def exit_with_error(message):
  print "*** ERROR: " + message
  sys.exit(1)


def download_series(out_path, series_url, quality, cookie):
  info('Retrieving lesson series HTML at %s...' % series_url)
  series_toc_html = http_get(series_url, cookie)

  series_toc_soup = BeautifulSoup(series_toc_html, 'html.parser')
  lesson_urls = collect_lesson_urls(series_toc_soup)
  info('Found %d lessons' % len(lesson_urls))

  lesson_ids = [get_lesson_id_from_url(url) for url in lesson_urls]

  series = retrieve_series(lesson_ids[0], cookie)
  titles = collect_lesson_titles(series)

  download_supplemental_files(out_path, lesson_urls, titles, cookie)
  download_videos(out_path, lesson_ids, titles, cookie, quality)


def download_videos(out_path, lesson_ids, titles, cookie, quality):
  for lesson_no, lesson_id in enumerate(lesson_ids, start=1):
    playlist = retrieve_playlist(lesson_id, cookie)
    lesson_title = titles[lesson_no - 1]

    info("\n")

    for scene_no, scene in enumerate(playlist, start=1):
      scene_title = scene['title']
      info("Processing lesson: '%s', scene: '%s'" % (lesson_title,
                                                     scene_title))

      video_url = find_video_url(scene['sources'], quality)
      outfile = mk_outfname(lesson_title, scene_title, out_path)
      download_file(video_url, outfile)


def download_file(url, outfile):
  wget_cmd = mk_wget_command(url, outfile)

  if DRY_RUN:
    print wget_cmd
  else:
    os.system(wget_cmd)

  info("\n")


def download_supplemental_files(out_path, lesson_urls, titles, cookie):

  def download(lesson_soup, title, filetype):
    urls = get_supplemental_dl_urls(lesson_soup, filetype)
    for i, url in enumerate(urls, start=1):
      fname = '%s %s.%s' % (mk_safe_filename(title), str(i), filetype)
      outfile = os.path.join(out_path, fname)
      download_file(url, outfile)

  for lesson_idx, lesson_url in enumerate(lesson_urls, start=0):
    info('Retrieving lesson HTML at %s...' % lesson_url)
    lesson_html = http_get(lesson_url, cookie)
    lesson_soup = BeautifulSoup(lesson_html, 'html.parser')

    title = titles[lesson_idx]
    download(lesson_soup, title, 'pdf')
    download(lesson_soup, title, 'gpx')
    download(lesson_soup, title, 'gif')


def get_supplemental_dl_urls(series_toc_soup, filetype):
  div = series_toc_soup.find_all(id='supplemental_content_nav')
  list_items = div[0].find_all('li', class_=filetype)
  urls = []
  for li in list_items:
    fname = li.a['rel'][0]
    urls.append('%s%s.%s' % (SUPPLEMENTAL_DL_URL_PREFIX, fname, filetype))
  return urls


def collect_lesson_urls(series_toc_soup):
  divs = series_toc_soup.select("div.lesson_hold")
  urls = []
  for d in divs:
    lesson_link = d.find_all(href=re.compile('lesson'))[0]
    urls.append(lesson_link['href'])
  return urls


def get_lesson_id_from_url(url):
  title = url.split('/')[-1]
  return title.split('-')[0]


def http_get(url, cookie):
  opener = urllib2.build_opener()
  opener.addheaders.append(('Cookie', cookie))
  response = opener.open(url)
  return response.read()


def retrieve_series(lesson_id, cookie):
  series_url = SERIES_URL_PREFIX + lesson_id
  info('Retrieving series JSON at %s...' % series_url)
  series_json = http_get(series_url, cookie)
  return json.loads(series_json)


def collect_lesson_titles(series_json):
  titles = []
  for lesson_no, lesson in enumerate(series_json, start=1):
    title = '%02d - %s' % (lesson_no, lesson['title'])
    titles.append(title)
  return titles


def find_video_url(sources, quality):
  try:
    start_idx = VIDEO_QUALITIES.index(quality)
  except ValueError:
    exit_with_error("Invalid video quality '%s',\n" \
      "  valid video qualities: %s" %
      (quality, ", ".join(VIDEO_QUALITIES))
    )
  else:
    for quality in VIDEO_QUALITIES[start_idx:]:
      for src in sources:
        if src['label'] == quality:
          info("Found video in quality '%s'" % quality)
          return src['file']

    exit_with_error("No valid video quality found in response,\n" \
      "  retrieved video qualities: %s\n" \
      "  valid video qualities: %s" %
      (
        ', '.join([s['label'] for s in sources]),
        ", ".join(VIDEO_QUALITIES)
      )
    )


def retrieve_playlist(lesson_id, cookie):
  url = PLAYLIST_URL_PREFIX + lesson_id
  info('Retrieving playlist JSON at %s...' % url)

  playlist_json = http_get(url, cookie)
  return json.loads(playlist_json)


def mk_outfname(lesson_title, scene_title, out_path):
  fname = '%s - %s.mp4' % (
    mk_safe_filename(lesson_title), mk_safe_filename(scene_title))
  return os.path.join(out_path, fname)


def mk_safe_filename(filename):
  return re.sub('[^\w\-_\. ]', '_', filename)

def mk_wget_command(url, outfile):
  return "wget '%s' -O '%s'" % (url, outfile)


def main(args):
  if len(args) < 4:
    print 'Usage: %s SERIES_URL OUT_PATH QUALITY COOKIE' % (args[0])
    sys.exit(1)
  out_path = args[1]
  series_url = args[2]
  quality = args[3]
  cookie = args[4]

  if quality not in VIDEO_QUALITIES:
    exit_with_error("Invalid video quality: '%s'" % quality)

  download_series(out_path, series_url, quality, cookie)


main(sys.argv)


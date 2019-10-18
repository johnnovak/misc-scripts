#!/usr/bin/env python

# Convert line elements with overlapping endpoints into polylines in an
# SVG file.

import os
import sys

try:
    from lxml import etree 
except ImportError:
    import xml.etree.ElementTree as etree

from collections import defaultdict
from optparse import OptionParser


SVG_NS = 'http://www.w3.org/2000/svg'

START = 1
END = 2


class Line(object):
    def __init__(self, line_element):
        a = line_element.attrib
        self.x1 = float(a['x1'])
        self.y1 = float(a['y1'])
        self.x2 = float(a['x2'])
        self.y2 = float(a['y2'])
        self.strokeWidth = float(a['stroke-width'])

    def reverse(self):
        self.x1, self.x2 = self.x2, self.x1
        self.y1, self.y2 = self.y2, self.y1

    def start_hash(self):
        return str(self.x1) + ',' + str(self.y1)

    def end_hash(self):
        return str(self.x2) + ',' +  str(self.y2)

    def endpoint(self, direction):
        if direction == START:
            return self.start_hash()
        else:
            return self.end_hash()

    def get_other_hash(self, key):
        h = self.start_hash()
        if h == key:
            h = self.end_hash()
        return h

    def __repr__(self):
        return '((%s,%s),(%s,%s),sw:%s)' % (self.x1, self.y1,
                                            self.x2, self.y2,
                                            self.strokeWidth)

class EndpointHash(object):
    def __init__(self, lines):
        self.endpoints = defaultdict(list)
        for l in lines:
            self.endpoints[l.start_hash()].append(l)
            self.endpoints[l.end_hash()].append(l)

    def count_overlapping_points(self):
        count = 0
        for key, lines in self.endpoints.iteritems():
            l = len(lines)
            if l > 1:
                count += 1
        return count

    def _del_line(self, key, line):
        self.endpoints[key].remove(line)
        if len(self.endpoints[key]) == 0:
            del self.endpoints[key]

    def remove_line(self, line):
        key = line.start_hash()
        self._del_line(key, line)
        self._del_line(line.get_other_hash(key), line)

    def pop_connected_line(self, line, key):
        if key in self.endpoints:
            line = self.endpoints[key][0]
            self.remove_line(line)
            return line
        else:
            return


def parse_svg(fname):
    print "Parsing '%s'..." % (fname)
    return etree.parse(fname)


def get_lines(svg):
    lines = []
    for l in svg.getroot().iter('{%s}line' % SVG_NS):
        lines.append(Line(l))
    return lines


def align_lines(l1, l2):
    if (   l1.x1 == l2.x1 and l1.y1 == l2.y1
        or l1.x2 == l2.x2 and l1.y2 == l2.y2):
        l2.reverse()


def connect_lines(lines, endpoint_hash, line, direction, poly):
    while True:
        key = line.endpoint(direction)
        connected_line = endpoint_hash.pop_connected_line(line, key)
        if connected_line:
            if direction == START:
                poly.insert(0, connected_line)
            else:
                poly.append(connected_line)
            align_lines(line, connected_line)
            lines.remove(connected_line)
            line = connected_line
        else:
            break


def find_polylines(lines, endpoint_hash):
    polylines = []
    while lines:
        line = lines.pop()
        endpoint_hash.remove_line(line)
        poly = [line]
        connect_lines(lines, endpoint_hash, line, START, poly)
        connect_lines(lines, endpoint_hash, line, END, poly)
        polylines.append(poly)
    return polylines


def optimize(svg):
    lines = get_lines(svg)
    print '%s line segments found' % len(lines)

    lines_by_width = defaultdict(list)
    for l in lines:
        lines_by_width[l.strokeWidth].append(l)
    del lines

    print '%s different stroke widths found:' % len(lines_by_width)
    for width, lines in lines_by_width.iteritems():
        print '  strokeWidth: %s (%s lines)' % (width, len(lines))

    polylines = []
    for width, lines in lines_by_width.iteritems():
        print 'Finding polylines (strokeWidth: %s)... ' % width

        endpoint_hash = EndpointHash(lines)
        overlapping_points = endpoint_hash.count_overlapping_points()
        print ('  %s line segments, %s overlapping points'
               % (len(lines), overlapping_points)),

        p = find_polylines(lines, endpoint_hash)
        print '-> %s polylines' % len(p)
        polylines += p

    return polylines


def write_svg(polylines, outfile):
    print "Writing '%s'..." % outfile

    f = open(outfile, 'w')
    f.write("""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" version="1.1">
""")

    def point_to_str(x, y):
        return '%s,%s ' % (x, y)

    for p in polylines:
        points = []
        for line in p:
            if not points:
                points.append(point_to_str(line.x1, line.y1))
            points.append(point_to_str(line.x2, line.y2))

        f.write('<polyline fill="none" stroke="#000" stroke-width="%s" points="%s"/>\n'
                % (p[0].strokeWidth, ' '.join(points)))

    f.write('</svg>\n')
    f.close()


def get_filesize(fname):
    return os.stat(fname).st_size


def print_size_stats(infile, outfile):
    insize = get_filesize(infile)
    outsize = get_filesize(outfile)
    print ('Original file size: %.2fKiB, new file size: %.2fKiB (%.2f)'
          % (insize / 1024., outsize / 1024., float(outsize) / insize * 100))


def main():
    usage = 'Usage: %prog INFILE OUTFILE'
    parser = OptionParser(usage=usage)

    options, args = parser.parse_args()

    if len(args) < 2:
        parser.error('input and output files must be specified')
        return 2

    infile = args[0]
    outfile = args[1]

    svg = parse_svg(infile)
    polylines = optimize(svg)
    print '%s polyline(s) found in total' % len(polylines)

    write_svg(polylines, outfile)
    print_size_stats(infile, outfile)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)


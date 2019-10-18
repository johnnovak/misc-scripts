# polylinize.py

## Overview

This is a simple Python script to convert individual line segments having
overlapping endpoints into polylines in an SVG file. This comes in handy when
exporting SVG images from a drawing program that outputs continuous lines as
thousands of `line` elements instead of much fewer `polyline` elements (e.g.
SketchUp). This makes the filesize grow just too large if you intend to use
the resuling SVG images on a website, for example.

The motivation for writing the script was that although tools like
[svg-scour](https://github.com/nhooey/svg-scour) and
[svgo](https://github.com/svg/svgo) do a great job at optimizing and cleaning
up SVG files, they do not have the ability to convert connected line elements
into polylines. So my solution was to run the SVG files through this script
first, then use **scour** or **svgo** to reduce the filesizes even further.

The script is intended to be used on line art images that only contain black
`line` elements with different `strokeWidth` attributes. All other SVG
elements and attributes are discarded in the optimisation process.


## Dependencies

- Requires Python 2.5+
- Optionally requires [lxml](https://github.com/lxml/lxml) for faster
  processing (recommended)


## Usage

```
polylinize.py SVG_INPUT SVG_OUTPUT
```


## Caveats

There are a few caveats you should be aware of as they might cause issues or
unexpected behaviour:

- Only `line` elements are processed, all other SVG elements are discarded.

- `line` elements are grouped by the `strokeWidth` attribute and then output
  as black `polyline` elements (all color information is discarded).

- The algorithm that finds connected line segments is non-deterministic. This
  means that you can easily get different results when using the script
  multiple times on the same input file.

- The algorithm does not attempt to find the most optimal (least storage
  space) solution.

- Two lines are considered to be connected when their endpoint coordinates,
  as they appear in the SVG file, match exactly.


## License

Copyright © 2013-2019 John Novak <<john@johnnovak.net>>

This work is free. You can redistribute it and/or modify it under the terms of
the [Do What The Fuck You Want To Public License, Version
2](http://www.wtfpl.net/), as published
by Sam Hocevar. See the [COPYING](./COPYING) file for more details.


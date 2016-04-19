# FuzzImageMagick
Full setup for fuzzing GraphicsMagick. Currently (2016-04-19) covers ~23% of the codebase.

## 1. Download GraphicsMagick
    hg clone http://hg.code.sf.net/p/graphicsmagick/code graphicsmagick

## 2. Build GraphicsMagick

### Vanilla Build:

    CC=afl-clang-fast CXX=afl-clang-fast++ ./configure && make

### Minimize Shared libraries + ASAN
    AFL_USE_ASAN=1 AFL_HARDEN=1 CC=afl-clang-fast CXX=afl-clang-fast++ ./configure --enable-static=yes --with-bzlib=no --with-dps=no --with-fpx=no --with-ttf=no --with-gslib=no --with-jbig=no --with-jpeg=no --with-jp2=no --with-lcms2=no --with-lzma=no --with-magick-plus-plus=no --with-png=no --with-tiff=no --with-trio=no --with-webp=no --with-wmf=no --with-x=no --with-xml=no --with-zlib=no && AFL_USE_ASAN=1 AFL_HARDEN=1 make


## 3. Fuzz with AFL

    afl-fuzz -m none -i "samples" -o "fuzz_results" gm convert @@ /dev/null

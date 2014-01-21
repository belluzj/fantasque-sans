#!/bin/sh

# choose package target based on Distro
case $( lsb_release -si ) in
  Ubuntu|Debian)      pkg=deb ;;
  Fedora|RedHat|SLES) pkg=rpm ;;
esac
# But make it overridable from outside:
pkg=${PKG:-${pkg}}

name='fantasque-sans'
version='1.4.1'
desc='A font family with a great monospaced variant for programmers.'
url=http://openfontlibrary.org/en/font/fantasque-sans

fpm -s dir -t ${pkg} -a all \
  -n ${name}-fonts          \
  -v ${version}             \
  --url ${url}              \
  --description "${desc}"   \
	--license OFL             \
  FantasqueSansMono.ttf=/usr/share/fonts/truetype/${name}/         \
  FantasqueSansMonoBold.ttf=/usr/share/fonts/truetype/${name}/     \
  OTF/FantasqueSansMono.otf=/usr/share/fonts/opentype/${name}/     \
  OTF/FantasqueSansMonoBold.otf=/usr/share/fonts/opentype/${name}/ \
  OFL.txt=/usr/share/doc/${name}/copyright \
  README.md=/usr/share/doc/${name}/        \
	Specimen=/usr/share/doc/${name}/

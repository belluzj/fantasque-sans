#!/bin/sh

# choose package target based on Distro
case $( lsb_release -si ) in
  Ubuntu|Debian)      pkg=deb ;;
  Fedora|RedHat|SLES) pkg=rpm ;;
esac
# But make it overridable from outside:
pkg=${PKG:-${pkg}}

name='fantasque-sans'
version='1.8.0'
desc='A font family with a great monospaced variant for programmers.'
url=http://openfontlibrary.org/en/font/fantasque-sans

fpm -s dir -t ${pkg} -a all \
  -n ${name}-fonts          \
  -v ${version}             \
  --url ${url}              \
  --description "${desc}"   \
	--license OFL             \
  Variants/Normal/TTF/FantasqueSansMono-Regular.ttf=/usr/share/fonts/truetype/${name}/         \
  Variants/Normal/TTF/FantasqueSansMono-Bold.ttf=/usr/share/fonts/truetype/${name}/     \
  Variants/Normal/TTF/FantasqueSansMono-Italic.ttf=/usr/share/fonts/truetype/${name}/     \
  Variants/Normal/TTF/FantasqueSansMono-BoldItalic.ttf=/usr/share/fonts/truetype/${name}/     \
  Variants/Normal/OTF/FantasqueSansMono-Regular.otf=/usr/share/fonts/opentype/${name}/     \
  Variants/Normal/OTF/FantasqueSansMono-Bold.otf=/usr/share/fonts/opentype/${name}/ \
  Variants/Normal/OTF/FantasqueSansMono-Italic.otf=/usr/share/fonts/opentype/${name}/ \
  Variants/Normal/OTF/FantasqueSansMono-BoldItalic.otf=/usr/share/fonts/opentype/${name}/ \
  Extras/fontconfig/ss01.conf=/etc/fonts/conf.avail/25-${name}-nondescript-k.conf \
  LICENSE.txt=/usr/share/doc/${name}/copyright \
  README.md=/usr/share/doc/${name}/        \
  CHANGELOG.md=/usr/share/doc/${name}/        \
  Specimen=/usr/share/doc/${name}/

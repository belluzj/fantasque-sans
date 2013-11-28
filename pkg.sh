#!/bin/sh

# choose package target based on Distro
case $( lsb_release -si ) in
  Ubuntu|Debian)      pkg=deb ;;
  Fedora|RedHat|SLES) pkg=rpm ;;
esac
# But make it overridable from outside:
pkg=${PKG:-${pkg}}

name='cosmic-sans-neue'
version='1.3.1'
desc='A font family with a great monospaced variant for programmers.'
url=http://openfontlibrary.org/en/font/cosmic-sans-neue-mono

fpm -s dir -t ${pkg} -a all \
  -n ${name}-fonts          \
  -v ${version}             \
  --url ${url}              \
  --description "${desc}"   \
	--license OFL             \
  CosmicSansNeueMono.ttf=/usr/share/fonts/truetype/${name}/         \
  CosmicSansNeueMonoBold.ttf=/usr/share/fonts/truetype/${name}/     \
  OTF/CosmicSansNeueMono.otf=/usr/share/fonts/opentype/${name}/     \
  OTF/CosmicSansNeueMonoBold.otf=/usr/share/fonts/opentype/${name}/ \
  OFL.txt=/usr/share/doc/${name}/copyright \
  README.md=/usr/share/doc/${name}/        \
	Specimen=/usr/share/doc/${name}/

#!/bin/bash

# Generate font files with FontForge, and a CSS declaration for this font.

basename=$1
ttf="${basename}.ttf"
otf="OTF/${basename}.otf"
texFamily="cm" # arbitrary two letters out of the font's name

texCut="r" # Regular
if [[ "${basename,,}" == *bold* ]]; then
  texCut="b" # Bold
fi

echo -e "\e[1;37mGenerating ${basename}... \e[0m"

fontforge -lang=py -script - <<EOF
import fontforge;

font = fontforge.open("Sources/${basename}.sfd");

bitmask = font.validate();
if bitmask != 0:
  exit(42);

font.generate("${basename}.ttf");
font.generate("OTF/${basename}.otf");
font.generate("Webfonts/${basename}.svg");

# TeX stuff
font.encoding = "AdobeStandard";
font.generate("TeX/f${texFamily}${texCut}8a.pfb",
  flags=("afm", "tfm", "pfm"));
EOF
error=$?

cat > Webfonts/${basename}-decl.css <<EOF
@font-face {
    font-family: '${basename}';
    src: url('${basename}.eot'); /* IE 9 Compatibility Mode */
    src: url('${basename}.eot?#iefix') format('embedded-opentype'), /* IE < 9 */
         url('${basename}.woff') format('woff'), /* Firefox >= 3.6, any other modern browser */
         url('${basename}.ttf') format('truetype'), /* Safari, Android, iOS */
         url('${basename}.svg#${basename}') format('svg'); /* Chrome < 4, Legacy iOS */
}

EOF

if [ "x$error" != "x0" ]; then
  echo -e "\e[1;31mError in ${basename}.\e[0m"
  if [ "x$error" = "x42" ]; then
    echo "Font ${basename}.sfd is not valid"
  fi
else
  echo -e "\e[1;32m${basename} OK.\e[0m"
fi

exit $error

#!/bin/bash

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

# TeX stuff
font.encoding = "AdobeStandard";
font.generate("TeX/f${texFamily}${texCut}8a.pfb",
  flags=("afm", "tfm", "pfm"));
EOF

error=$?
if [ "x$error" != "x0" ]; then
  echo -e "\e[1;31mError in ${basename}.\e[0m"
  if [ "x$error" = "x42" ]; then
    echo "Font ${basename}.sfd is not valid"
  fi
else
  echo -e "\e[1;32m${basename} OK.\e[0m"
fi

exit $error

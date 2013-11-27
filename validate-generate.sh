#!/bin/bash

basename=$1
ttf="${basename}.ttf"
otf="OTF/${basename}.otf"

echo -e "\e[1;37mGenerating ${basename}... \e[0m"

if [ -f "$ttf" ]; then
  rm "$ttf"
fi

if [ -f "$otf" ]; then
  rm "$otf"
fi

fontforge -lang=py -script - <<EOF
import fontforge;

font = fontforge.open("Sources/${basename}.sfd");

bitmask = font.validate();
if bitmask != 0:
  exit(42);

font.generate("${basename}.ttf");
font.generate("OTF/${basename}.otf");
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

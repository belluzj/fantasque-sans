SOURCES=$(wildcard Sources/*.sfd)
BASENAMES=$(patsubst Sources/%.sfd,%,$(SOURCES))
TTF_FILES=$(patsubst %,%.ttf,$(BASENAMES))
# TTF_HINTED_FILES=$(patsubst %,%-autohint.ttf,$(BASENAMES))
OTF_FILES=$(patsubst %,OTF/%.otf,$(BASENAMES))
SVG_FILES=$(patsubst %,Webfonts/%.svg,$(BASENAMES))
WOFF_FILES=$(patsubst %,Webfonts/%.woff,$(BASENAMES))
EOT_FILES=$(patsubst %,Webfonts/%.eot,$(BASENAMES))
CSS_FRAGMENTS=$(patsubst %,Webfonts/%-decl.css,$(BASENAMES))
CSS_FILE=Webfonts/stylesheet.css

all: zip

OTF/%.otf %.ttf Webfonts/%.svg Webfonts/%.eot Webfonts/%.woff Webfonts/%-decl.css: Sources/%.sfd
	mkdir -p OTF TeX Webfonts
	./validate-generate.sh "$*"
	# TODO determine perfect parameters
	ttfautohint "$*.ttf" "$*.hinted.ttf"
	mv "$*.hinted.ttf" "$*.ttf"
	sfnt2woff "OTF/$*.otf"
	mv "OTF/$*.woff" Webfonts
	ttf2eot "$*.ttf" > "Webfonts/$*.eot"

$(CSS_FILE): $(CSS_FRAGMENTS)
	cat $(CSS_FRAGMENTS) > $(CSS_FILE)

.PHONY: install clean zip
install: $(TTF_FILES)
	cp $^ ~/.fonts/
	fc-cache -f

zip: $(TTF_FILES) $(OTF_FILES) $(SVG_FILES) $(EOT_FILES) $(WOFF_FILES) $(SOURCES) $(CSS_FILE)
	zip CosmicSansNeueMono.zip OFL.txt README.md Webfonts/README.md $^

clean:
	rm -f *.ttf *.zip OTF/* TeX/* Webfonts/*.eot Webfonts/*.woff Webfonts/*.svg Webfonts/*.css


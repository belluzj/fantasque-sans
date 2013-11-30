SOURCES=$(wildcard Sources/*.sfd)
BASENAMES=$(patsubst Sources/%.sfd,%,$(SOURCES))
TTF_FILES=$(patsubst %,%.ttf,$(BASENAMES))
# TTF_HINTED_FILES=$(patsubst %,%-autohint.ttf,$(BASENAMES))
OTF_FILES=$(patsubst %,OTF/%.otf,$(BASENAMES))

all: zip

OTF/%.otf %.ttf: Sources/%.sfd
	mkdir -p OTF TeX
	./validate-generate.sh $*
	# TODO determine perfect parameters
	ttfautohint $*.ttf $*.hinted.ttf
	mv $*.hinted.ttf $*.ttf

.PHONY: install clean zip
install: $(TTF_FILES)
	cp $^ ~/.fonts/
	fc-cache -f

zip: $(TTF_FILES) $(OTF_FILES) $(SOURCES)
	zip CosmicSansNeueMono.zip OFL.txt README.md $^

clean:
	rm -f *.ttf OTF/* TeX/*


BASENAMES=$(patsubst Sources/%.sfd,%,$(wildcard Sources/*.sfd))
TTF_FILES=$(patsubst %,%.ttf,$(BASENAMES))
TTF_HINTED_FILES=$(patsubst %,%-autohint.ttf,$(BASENAMES))
OTF_FILES=$(patsubst %,OTF/%.otf,$(BASENAMES))

all: zip

OTF/%.otf %.ttf: Sources/%.sfd
	./validate-generate.sh $*

%-autohint.ttf: %.ttf
	# TODO determine perfect parameters
	ttfautohint $< $@

.PHONY: install clean zip
install: $(TTF_FILES)
	cp $^ ~/.fonts/
	fc-cache -f

zip: $(TTF_FILES) $(TTF_HINTED_FILES) $(OTF_FILES)
	zip CosmicSansNeueMono.zip OFL.txt README.md $^

clean:
	rm $(TTF_FILES) $(TTF_HINTED_FILES) $(OTF_FILES)


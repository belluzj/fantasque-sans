SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)
BASENAMES=$(patsubst Sources/%.sfdir,%,$(SOURCES))
TTF_FILES=$(patsubst %,Variants/Normal/TTF/%.ttf,$(BASENAMES))
ZIP_FILE=Variants/Normal/FantasqueSansMono.zip

INSTALLED_TTF_FILES=$(patsubst %,~/.fonts/%.ttf,$(BASENAMES))

all: $(ZIP_FILE)

$(ZIP_FILE): $(TTF_FILES)
	Scripts/zip-all-variants Variants

Variants/Normal/TTF/%.ttf: Sources/%.sfdir
	mkdir -p Variants
	Scripts/validate-font "$<"
	Scripts/generate-font-variants "$<" Variants

.PHONY: install clean
install: $(INSTALLED_TTF_FILES)

$(INSTALLED_TTF_FILES): $(TTF_FILES)
	mkdir -p ~/.fonts/
	cp $^ ~/.fonts/
	fc-cache -f

clean:
	rm -rf Variants

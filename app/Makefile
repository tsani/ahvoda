.PHONY: all clean dependencies
.SUFFIXES:

# JavaScript source and destination directories
JSSRC=static/js/src
JSDIST=static/js/dist

# LESS source and destination directories
LESSSRC=static/less/src
LESSDIST=static/less/dist

# LESS compiler and its settings
LESSC=lessc
LESSFLAGS=

# JavaScript "compiler" (compressor and mangler) and settings
JSC=uglifyjs
JSFLAGS=-c --enclose

CSSC=uglifycss

# The JavaScript source files
JSSRCFILES=$(shell find $(JSSRC) -name '*.js' -type f)

BUSINESSAPP=ahvoda-app

# All the LESS source code.
LESSFILES=$(shell find $(LESSSRC) -name '*.less' -type f)
# The Makefile dependency fragments generated by lessc.
LESSDEPFILES=$(patsubst %,%.d,$(LESSFILES))
# The input LESS files that we're actually interested in.
LESSSRCFILES=$(LESSSRC)/external.less $(LESSSRC)/internal.less
# The output CSS files.
LESSDISTFILES=$(patsubst $(LESSSRC)/%.less,$(LESSDIST)/%.min.css,$(LESSSRCFILES))

# Building the full distribution means building the LESS distribution and the
# JavaScript distribution
all: $(LESSDIST) $(JSDIST)

# To build the JavaScript distribution is to build the minified and normal
# distributions of the business app.
$(JSDIST): $(JSDIST)/$(BUSINESSAPP).min.js $(JSDIST)/$(BUSINESSAPP).js

# To build the minified business app, we concatenate all the JavaScript source
# files and uglify them (mangle + compress).
$(JSDIST)/$(BUSINESSAPP).min.js: $(JSSRCFILES)
	$(JSC) $^ -o $@ --source-map $@.map $(JSFLAGS)

# To build the business app, all the JavaScript source files need to be put
# through UglifyJS
$(JSDIST)/$(BUSINESSAPP).js: $(JSSRCFILES)
	$(JSC) $^ -o $@ --source-map $@.map

# To build the LESS distribution, we need to build the depfiles and finally the
# CSS files.
$(LESSDIST): $(LESSDEPFILES) $(LESSDISTFILES)

# Generic rule for building a depfile for a LESS file.
%.less.d: %.less
	$(LESSC) -M $(LESSFLAGS) $< $(patsubst $(LESSSRC)/%.less,$(LESSDIST)/%.css,$<) > $<.d
	rm $(patsubst $(LESSSRC)/%.less,$(LESSDIST)/%.css,$<)

# Rule for transforming LESS into CSS
$(LESSDIST)/%.css: $(LESSSRC)/%.less
	$(LESSC) $(LESSFLAGS) $< $@

%.min.css: %.css
	$(CSSC) $< > $@

# Inject the dependency files into this makefile.
-include $(LESSDEPFILES)

clean:
	-rm $(LESSDIST)/*.css
	-rm $(JSDIST)/$(BUSINESSAPP).{min.,}js
	-rm $(LESSSRC)/*.d

dependencies:
	bower install

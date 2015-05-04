.PHONY:
.SUFFIXES:

LESSC="lessc"

all: static

static: css

css: app/static/css/external.css app/static/css/internal.css app/static/css/swipe.css

# Rule for compiling .less files
app/static/css/%.css: less/%.less
	$(LESSC) $< $@

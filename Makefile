.PHONY:
.SUFFIXES:

LESSC="lessc"

all: static

static: css

css: app/static/css/main.css app/static/css/external.css

# Rule for compiling .less files
app/static/css/%.css: less/%.less
	$(LESSC) $< $@

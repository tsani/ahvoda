.PHONY:
.SUFFIXES:

LESSC="lessc"

all: static

static: css

css: app/static/css/main.css app/static/css/external.css app/static/css/internal.css app/static/css/swipe.css

app/static/css/external.css: less/main.less less/external.less
	$(LESSC) $< $@

app/static/css/internal.css: less/main.less less/internal.less
	$(LESSC) $< $@

# Rule for compiling .less files
app/static/css/%.css: less/%.less
	$(LESSC) $< $@

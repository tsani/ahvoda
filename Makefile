.PHONY:
.SUFFIXES:

LESSC="lessc"

all: static

static: css

css: app/static/css/external.css app/static/css/internal.css

app/static/css/external.css: less/external.less less/main.less
	$(LESSC) $< $@

app/static/css/internal.css: less/internal.less less/main.less
	$(LESSC) $< $@

clean:
	rm -v app/static/css/*.css

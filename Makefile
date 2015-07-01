.PHONY:
.SUFFIXES:

LESSC="lessc"

all: static

static: css

css: app/static/css/external.css app/static/css/internal.css

less/main.less: less/colors.less less/prefixes.less

less/external.less: less/main.less

less/internal.less: less/main.less

app/static/css/external.css: less/external.less
	$(LESSC) $< $@

app/static/css/internal.css: less/internal.less
	$(LESSC) $< $@

clean:
	rm -v app/static/css/*.css

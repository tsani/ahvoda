.PHONY: all clean dependencies
.SUFFIXES:

LESSC=lessc

all: static/css

static/css: static/css/external.css static/css/internal.css

less/main.less: less/colors.less less/prefixes.less
	touch less/main.less

less/external.less: less/main.less
	touch less/external.less

less/internal.less: less/main.less
	touch less/internal.less

static/css/external.css: less/external.less
	$(LESSC) $< $@

static/css/internal.css: less/internal.less
	$(LESSC) $< $@

clean:
	rm -v static/css/*.css

dependencies:
	bower install

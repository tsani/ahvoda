.PHONY: all app dependencies venv
.SUFFIXES:

all: app dependencies

app:
	+$(MAKE) -C app

dependencies:
	venv/bin/pip install -r requirements.txt
	+$(MAKE) -C app dependencies

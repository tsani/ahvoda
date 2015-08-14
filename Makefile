.PHONY: all clean app dependencies java/pojos migration upgrade
.SUFFIXES:

JS2PVER = 0.4.13
JS2P = bin/jsonschema2pojo-$(JS2PVER)/jsonschema2pojo
JS2PFLAGS = \
		--annotation-style "GSON" \
		--generate-constructors \
		--joda-dates \
		--source-type "JSONSCHEMA"

PYTHON=venv/bin/python
PIP=venv/bin/pip
PIPFLAGS=-q

all: venv dependencies app upgrade

migration:
	$(PYTHON) manage.py db migrate

upgrade:
	$(PYTHON) manage.py db upgrade

app:
	+$(MAKE) -C app

dependencies:
	$(PIP) $(PIPFLAGS) install -r requirements.txt
	+$(MAKE) -C app dependencies

venv:
	virtualenv venv

clean:
	rm -r java/pojos/*

java/pojos: app/json-schema/definitions
	# filter-json-api.py $< # extract essential parts of the json schema
	$(JS2P) $(JS2PFLAGS) -s $(patsubst %/api.json,%,$<) -t $@

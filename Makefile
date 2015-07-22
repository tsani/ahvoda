.PHONY: all clean app dependencies venv java/pojos
.SUFFIXES:

JS2PVER = 0.4.13
JS2P = bin/jsonschema2pojo-$(JS2PVER)/jsonschema2pojo
JS2PFLAGS = \
		--annotation-style "GSON" \
		--class-prefix "Ah" \
		--generate-constructors \
		--joda-dates \
		--source-type "JSONSCHEMA"

all: app dependencies

app:
	+$(MAKE) -C app

dependencies:
	venv/bin/pip install -r requirements.txt
	+$(MAKE) -C app dependencies

clean:
	rm java/pojos/*

java/pojos: app/json-schema/definitions
	# filter-json-api.py $< # extract essential parts of the json schema
	$(JS2P) $(JS2PFLAGS) -s $(patsubst %/api.json,%,$<) -t $@

release:
ifndef VERSION
	$(error VERSION is undefined)
endif
	git describe --exact
	python setup.py sdist
	twine upload dist/yaclifw-$(VERSION).tar.gz

clean:
	rm -rf build dist yaclifw.egg-info *.pyc

.PHONY: register clean

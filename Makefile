.PHONY: all c test install clean

all: c test

c:
	$(MAKE) -C c

test:
	uv run --extra dev pytest tests/

install:
	uv tool install .

clean:
	$(MAKE) -C c clean

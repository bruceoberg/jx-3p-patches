ifdef SystemRoot
	RM = del /Q
else
	RM = rm -f
endif

DECODER_DIR = decoder
ENCODER_DIR = encoder
BUILD := $(abspath ../build)

.PHONY: all decoder encoder clean

all: decoder encoder

decoder:
	$(MAKE) -C $(DECODER_DIR) -f makefile BUILD=$(BUILD)/decoder

encoder:
	$(MAKE) -C $(ENCODER_DIR) BUILD=$(BUILD)/encoder

clean:
	$(MAKE) -C $(DECODER_DIR) -f makefile clean BUILD=$(BUILD)/decoder
	$(MAKE) -C $(ENCODER_DIR) clean BUILD=$(BUILD)/encoder

ifdef SystemRoot
	RM = del /Q
else
	RM = rm -f
endif

DECODER_DIR = decoder
ENCODER_DIR = encoder

.PHONY: all decoder encoder clean

all: decoder encoder

decoder:
	$(MAKE) -C $(DECODER_DIR) -f makefile

encoder:
	$(MAKE) -C $(ENCODER_DIR)

clean:
	$(MAKE) -C $(DECODER_DIR) -f makefile clean
	$(MAKE) -C $(ENCODER_DIR) clean

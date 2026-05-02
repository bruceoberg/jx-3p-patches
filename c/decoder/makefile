ifdef SystemRoot
	OS = win32
	RM = del /Q
	CP = copy
	FixPath = $(subst /,\,$1)
	MKDIR = if not exist "$(call FixPath, $1)" mkdir "$(call FixPath, $1)"
	LibSndFile = libsndfile-1
else
	OS = linux
	RM = rm -f
	CP = cp
	FixPath = $1
	MKDIR = mkdir -p $1
	LibSndFile = sndfile
endif

incdir=include
srcdir=src
BUILD ?= build
objdir=$(BUILD)/obj
bindir=$(BUILD)/bin
libdir=$(call FixPath, lib/$(OS))
CC=gcc
CFLAGS=-I$(incdir) -Wall -g


# targets
dist : $(bindir)/decode_patches
all : $(bindir)/analyzer $(bindir)/bitstream $(bindir)/c1diff $(bindir)/decode_patches
.PHONY : dist all


# build directories (order-only prerequisites)
$(objdir) $(bindir):
	$(call MKDIR, $@)


# components
detector.o : $(srcdir)/detector.c | $(objdir)
	$(CC) -c -o $(objdir)/$@ $< $(CFLAGS)

demodulator.o : $(srcdir)/demodulator.c | $(objdir)
	$(CC) -c -o $(objdir)/$@ $< $(CFLAGS)

decoder_patch.o : $(srcdir)/decoder_patch.c | $(objdir)
	$(CC) -c -o $(objdir)/$@ $< $(CFLAGS)


# executables
analyzer.o : $(srcdir)/analyzer.c | $(objdir)
	$(CC) -c -o $(objdir)/$@ $< $(CFLAGS)
$(bindir)/analyzer: detector.o analyzer.o | $(bindir)
	$(CC) -o $@ $(addprefix $(objdir)/, $^) $(CFLAGS) -l$(LibSndFile)

bitstream.o : $(srcdir)/bitstream.c | $(objdir)
	$(CC) -c -o $(objdir)/$@ $< $(CFLAGS)
$(bindir)/bitstream: detector.o demodulator.o bitstream.o | $(bindir)
	$(CC) -o $@ $(addprefix $(objdir)/, $^) $(CFLAGS) -l$(LibSndFile)

c1diff.o : $(srcdir)/c1diff.c | $(objdir)
	$(CC) -c -o $(objdir)/$@ $< $(CFLAGS)
$(bindir)/c1diff: detector.o demodulator.o c1diff.o | $(bindir)
	$(CC) -o $@ $(addprefix $(objdir)/, $^) $(CFLAGS) -l$(LibSndFile)

decode_patches.o : $(srcdir)/decode_patches.c | $(objdir)
	$(CC) -c -o $(objdir)/$@ $< $(CFLAGS)
$(bindir)/decode_patches: detector.o demodulator.o decoder_patch.o decode_patches.o | $(bindir)
	$(CC) -o $@ $(addprefix $(objdir)/, $^) $(CFLAGS) -l$(LibSndFile)


clean:
	$(RM) $(call FixPath, $(objdir)/*.o)
	$(RM) $(call FixPath, $(bindir)/analyzer*) $(call FixPath, $(bindir)/bitstream*) $(call FixPath, $(bindir)/c1diff*) $(call FixPath, $(bindir)/decode_patches*)

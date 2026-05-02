CFLAGS=-Wall
LIBS=-lsndfile
BUILD ?= build
OBJDIR := $(BUILD)/obj
BINDIR := $(BUILD)/bin
READER_OBJS := $(addprefix $(OBJDIR)/, reader.o)
WRITER_OBJS := $(addprefix $(OBJDIR)/, writer.o audio.o csv_parser.o)

.PHONY: all clean
all: $(BINDIR)/reader $(BINDIR)/writer

$(OBJDIR) $(BINDIR):
	mkdir -p $@

$(OBJDIR)/audio.o: audio.c | $(OBJDIR)
	gcc $(CFLAGS) -c -o $@ audio.c

$(OBJDIR)/reader.o: reader.c | $(OBJDIR)
	gcc $(CFLAGS) -c -o $@ reader.c

$(OBJDIR)/writer.o: writer.c audio.h | $(OBJDIR)
	gcc $(CFLAGS) -c -o $@ writer.c

$(OBJDIR)/csv_parser.o: csv_parser.c patch.h | $(OBJDIR)
	gcc $(CFLAGS) -c -o $@ csv_parser.c

$(BINDIR)/reader: $(READER_OBJS) | $(BINDIR)
	gcc $(CFLAGS) $(LIBS) -o $@ $(READER_OBJS)

$(BINDIR)/writer: $(WRITER_OBJS) | $(BINDIR)
	gcc $(CFLAGS) $(LIBS) -o $@ $(WRITER_OBJS)

clean:
	rm -rf $(BUILD)

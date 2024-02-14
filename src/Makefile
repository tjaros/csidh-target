TARGET ?= main
SRC_DIRS ?= ../src

SRCS := main.c csidh.c fp.c mont.c randombytes.c uint.c parametrization.c
OBJS := $(addsuffix .o,$(basename $(SRCS)))
DEPS := $(OBJS:.o=.d)

INC_DIRS := $(shell find $(SRC_DIRS) -type d)
INC_FLAGS := $(addprefix -I,$(INC_DIRS))

CFLAGS ?= -DDBG -DF419

$(TARGET): $(OBJS)
	$(CC) -o $@ $(OBJS) 

.PHONY: clean
clean:
	$(RM) $(TARGET) $(OBJS) $(DEPS)

-include $(DEPS)

CC=gcc

#CC_FLAGS=-O3
CC_FLAGS=-Wall #-O3
DEBUGFLAGS=-ggdb -DDEBUG0

INCLUDE=.

all: find_val


find_val: $(OBJS)

	mkoctfile find_val.cc -I$(INCLUDE)

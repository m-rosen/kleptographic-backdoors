
# Written by Miriam Rosén in 2023

# ------------------------------------------------------
# Options
CC=gcc -std=gnu99
CFLAGS= -pedantic -Wall -Wextra -O3 -march=native
ODIR=build

NTEST=1000 # Number of seed pairs to generate with run_statistics

# ------------------------------------------------------
# Files
DEPS=backdoor_x25519.h monocypher/monocypher.h monocypher/utils.h

_MC=monocypher.o utils.o
MC =$(patsubst %,$(ODIR)/%,$(_MC))

_OBJ=backdoor_x25519.o statistics_x25519 test_x25519.o
OBJ=$(patsubst %,$(ODIR)/%,$(_OBJ))

# ------------------------------------------------------
# Monocypher
$(ODIR)/monocypher.o: monocypher/monocypher.c
	$(CC) -c -o $@ $< $(CFLAGS)

$(ODIR)/utils.o: monocypher/utils.c
	$(CC) -fPIC -c -o $@ $< $(CFLAGS)

# ------------------------------------------------------
# Objects
$(ODIR)/backdoor_x25519.o : backdoor_x25519.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

$(ODIR)/test_x25519.o : test_x25519.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

$(ODIR)/statistics_x25519.o : statistics_x25519.c $(DEPS)
	$(CC) -DNTEST=$(NTEST) -c -o  $@ $< $(CFLAGS)

# ------------------------------------------------------
# Programs
test: $(ODIR)/test_x25519.o $(ODIR)/backdoor_x25519.o $(MC)
	$(CC) -o $(ODIR)/$@ $^ $(CFLAGS) -lbsd
	
statistics: $(ODIR)/statistics_x25519.o $(ODIR)/backdoor_x25519.o $(MC)
	$(CC) -o $(ODIR)/$@ $^ $(CFLAGS) -lbsd


run_test: test
	$(ODIR)/test 

run_statistics: statistics
	$(ODIR)/statistics

# ------------------------------------------------------
# Objects needed for kyber integration
kyber_obj : $(ODIR)/backdoor_x25519.o $(MC)


# ------------------------------------------------------
clean:
	rm -rf build/
	mkdir build
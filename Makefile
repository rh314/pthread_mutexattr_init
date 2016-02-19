CFLAGS=-pthread

default:: sem-create sem-post sem-wait

sem-create: xsem.o
sem-post: xsem.o
sem-wait: xsem.o

clean:
	rm -f *.o sem-create sem-post sem-wait

CFLAGS = -Wall -pedantic -Werror -Wextra -Wconversion -std=gnu11


MONITOR: init main.o monitor.o procesador_petri.o
	mkdir -p build
	gcc main.o monitor.o procesador_petri.o -o build/main -pthread
	make clean_post
	clear
	./build/main

init:
	make clean

main.o: main.c main.h macros.h monitor.c monitor.h procesador_petri.c procesador_petri.h
	gcc -c main.c

monitor.o: monitor.c monitor.h macros.h procesador_petri.c procesador_petri.h
	gcc -c monitor.c

procesador_petri.o: procesador_petri.c procesador_petri.h macros.h
	gcc -c procesador_petri.c

clean:
	rm -f *.o
	rm -f *.so
	rm -f build/main

clean_post:
	rm -f *.o
	rm -f *.so

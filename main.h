#ifndef MAIN_H
#define MAIN_H

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include "monitor.h"
#include "procesador_petri.h"

//#define _REENTRANT
//#define _POSIX_PRIORITY_SCHEDULING

#define handle_error_en(en, msg) \
               do { errno = en; perror(msg); exit(EXIT_FAILURE); } while (0)


typedef struct segmento
{
    int *secuencia;
    unsigned int segmento_size;
    monitor_t *monitor;
    char *id;
} segmento_t;


static void *thread_run(void *arg);

#endif

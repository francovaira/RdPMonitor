/*
    Prueba del monitor implementado en C
*/

#include "main.h"

int main(void)
{
    pthread_t threadPROD;
    pthread_t threadCONS;
    pthread_attr_t attr;
    monitor_t monitor;
    procesador_petri_t petri;
    segmento_t segmentoPROD;
    segmento_t segmentoCONS;
    int s;

    printf("\nholis por aca 1\n");

    procesador_de_petri_init(&petri);
    monitor_init(&monitor, &petri);

    int seqPROD[3] = {0, 3, 4}; // T invariante del productor
    segmentoPROD.secuencia = seqPROD;
    segmentoPROD.segmento_size = 3;
    segmentoPROD.monitor = &monitor;
    segmentoPROD.id = "PROD";
    
    int seqCONS[3] = {1, 2, 5}; // T invariante del consumidor
    segmentoCONS.secuencia = seqCONS;
    segmentoCONS.segmento_size = 3;
    segmentoCONS.monitor = &monitor;
    segmentoCONS.id = "CONS";

    pthread_attr_init(&attr);
    s = pthread_attr_setscope(&attr, PTHREAD_SCOPE_SYSTEM);
    if (s != 0)
       handle_error_en(s, "pthread_attr_setscope");

    s = pthread_attr_setschedpolicy(&attr, SCHED_RR);
    if (s != 0)
        handle_error_en(s, "pthread_attr_setschedpolicy");

    pthread_create(&threadPROD, &attr, thread_run, (void *) &segmentoPROD);
    pthread_create(&threadCONS, &attr, thread_run, (void *) &segmentoCONS);

    pause();
}

static void *thread_run(void *arg)
{
    segmento_t *self = arg;
    long int cantidad_disparos;
    time_t t;
    time(&t);
    //printf("\n current time is : %s",ctime(&t));

    while (1)
    {
        for (int i = 0; i < self->segmento_size; ++i)
        {
            if(self->secuencia[i] != NULL_TRANSITION)
            {
                printf("HILO %s ##### cantidad de disparos: %ld\n", self->id, ++cantidad_disparos);
                self->monitor->disparar(self->monitor,self->secuencia[i]);
                //printf("time: %s\n\n", ctime(&t));
            }
            
            // ejecuta las acciones correspondientes al disparo
            /*if (self->actions[i] != NULL || self->objetos[i] != NULL)
            {
                self->actions[i](self->objetos[i]);
            }*/
        }
    }
}


/*
    Prueba del monitor implementado en C
*/

#include "main.h"

int main(void)
{
    pthread_t main_thread;
    pthread_attr_t attr;
    monitor_t monitor;
    procesador_petri_t petri;
    segmento_t segmento;
    int s;

    printf("\nholis por aca 1\n");

    procesador_de_petri_init(&petri);
    monitor_init(&monitor, &petri);

    int seq[11] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    segmento.secuencia = seq;
    segmento.segmento_size = 11;
    segmento.monitor = &monitor;

    pthread_attr_init(&attr);
    s = pthread_attr_setscope(&attr, PTHREAD_SCOPE_SYSTEM);
    if (s != 0)
       handle_error_en(s, "pthread_attr_setscope");

    s = pthread_attr_setschedpolicy(&attr, SCHED_RR);
    if (s != 0)
        handle_error_en(s, "pthread_attr_setschedpolicy");

    for (int i = 0; i < HILOS; ++i)
    {
        pthread_create(&main_thread, &attr, thread_run, (void *) &segmento);
    }

    pause();
}

static void *thread_run(void *arg)
{
    segmento_t *self = arg;
    while (1)
    {
        for (int i = 0; i < self->segmento_size; ++i)
        {
            if(self->secuencia[i] != NULL_TRANSITION)
            {
                self->monitor->disparar(self->monitor,self->secuencia[i]); // FIXME original
            }
            
            // ejecuta las acciones correspondientes al disparo
            /*if (self->actions[i] != NULL || self->objetos[i] != NULL)
            {
                self->actions[i](self->objetos[i]);
            }*/
            sleep(1);
        }
        printf("post delay\n");
    }
}


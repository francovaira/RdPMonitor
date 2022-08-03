#include "monitor.h"
#include "macros.h"

static const char* TAG = "Monitor";

static void print_marcado(procesador_petri_t *petri)
{
    for (int i = 0; i < PLAZAS; ++i) {
        printf("%li",petri->matriz_estado[i]);
        printf(",");
    }
    printf("\r\n");
}

static void print_occupancy(procesador_petri_t *petri)
{
    printf("------------------- OCCUPANCY -------------------");

    for (int i = 0; i < PLAZAS; ++i)
    {
        if(i%2==0)
        {
            if(i%3==0)
            {
                printf("\n");
            }

            if(petri->matriz_estado[i] == 1)
            {
                printf("X   ");
            }
            else
            {
                printf("O   ");
            }
        }
    }
    printf("\r\n\n");
}

void monitor_disparar2(monitor_t *monitor, int disparo)
{
    pthread_mutex_lock(&monitor->entrada);

    int k = monitor->petri->solicitud_disparo(monitor->petri, disparo); // SOLO CONSULTA SI PUEDE DISPARAR
    while (k == 0) // if (k == 0) no se pudo disparar
    {
        #if DEBUG
            printf("No sensibilizada: %i -- espera\n", disparo);
        #endif
//      if(monitor->petri->matriz_noperennes[disparo])
//      {
//          ESP_LOGW(TAG, "No Sensibilizada No Perenne: %i -- salgo\n", disparo);
//          return;
//      }
//      else
        {
            pthread_cond_wait(&monitor->condition[disparo], &monitor->entrada);
        }
        k = monitor->petri->solicitud_disparo(monitor->petri, disparo);
    }
    monitor->petri->disparar(monitor->petri, disparo); // DISPARA EFECTIVAMENTE

    #if DEBUG
        print_marcado(monitor->petri);
        print_occupancy(monitor->petri);
        printf("Si sensibilizada: %i -- disparo\n", disparo);
        // monitor->petri->toString(monitor->petri);
    #endif

    for (int i = 0; i < TRANSICIONES; ++i)
    {
        //pthread_cond_broadcast(&monitor->condition[i]);
        pthread_cond_signal(&monitor->condition[i]); // FIXME original
    }
    pthread_mutex_unlock(&monitor->entrada);
}

void monitor_init(monitor_t *monitor, procesador_petri_t *petri)
{
    pthread_mutex_init(&monitor->entrada, NULL);
    for (int i = 0; i < TRANSICIONES; ++i)
    {
        pthread_cond_init(&monitor->condition[i], NULL);
    }
    monitor->petri = petri;
    monitor->disparar = monitor_disparar2;
}



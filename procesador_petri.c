#include <stdio.h>
#include "procesador_petri.h"

static const char* TAG = "Petri";
static long int matriz_estado_aux[PLAZAS];

// Retorna 1 si es posible disparar la red con la transicion deseada. En caso contrario retorna cero.
static int petri_solicitud_disparo(procesador_petri_t *petri, int t_disparar)
{
    for (int i = 0; i < PLAZAS; ++i)
    {
        matriz_estado_aux[i] = petri->matriz_estado[i] + petri->matriz_incidencia[i][t_disparar];
        if (matriz_estado_aux[i] == -1)
            return 0;
    }
    return 1;
}

// Dispara la red dada la transicion [disparo]. Retorna 1 si pudo disparar, 0 caso contrario
static int petri_disparar(procesador_petri_t *petri, int disparo)
{
    if(petri_solicitud_disparo(petri, disparo))
    {
        for (int i = 0; i < PLAZAS; ++i)
        {
            petri->matriz_estado[i] = matriz_estado_aux[i];
        }
        return 1;
    }
    else return 0;
}

void petri_toString(procesador_petri_t *petri)
{
    printf("MARCADO: ");
    for (int i = 0; i < PLAZAS; ++i)
    {
        printf("%li, ", petri->matriz_estado[i]);
    }
    printf("\n");
}

void procesador_de_petri_init(procesador_petri_t *petri)
{
    petri->solicitud_disparo = petri_solicitud_disparo;
    petri->disparar = petri_disparar;
    petri->toString = petri_toString;

    long int estado[PLAZAS] = {MARCADO};
    for (int i =0; i<PLAZAS; i++)
    {
        petri->matriz_estado[i] = estado[i];
    }
    long int perennes[TRANSICIONES] = {NOPERENNE};
    for (int i =0; i<TRANSICIONES; i++)
    {
        petri->matriz_noperennes[i] = perennes[i];
    }
    long int incidencia[PLAZAS][TRANSICIONES] = {INCIDENCIA};
    for (int i = 0; i < PLAZAS; ++i) 
    {
        for (int j = 0; j <TRANSICIONES; ++j) 
        {
            petri->matriz_incidencia[i][j] = incidencia[i][j];
        }
    }
}
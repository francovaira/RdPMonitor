1) Se define el mapa con obstaculos y todo

2) Se define punto de comienzo y punto destino

3) Se calcula el path, se obtiene la secuencia de posiciones por las que tiene que pasar

4) La rdp todo este tiempo estuvo ejecutandose pero no habia nada sensibilizado por no haber un robot (ver como hacer esto)
   Se ubica fisicamente al robot en el punto inicio (esto se haria automaticamente despues), al darle start al programa
   se envia un mensaje MQTT al robot y comienza a moverse. Cuando llega a la celda siguiente envia un mensaje MQTT avisando que llego.
   Al hacer esto se ejecuta la red de tal manera que se marca como desocupada la celda primera y ocupada la actual. VER COMO HACER ESTE BLOQUEO

5) Se repite el paso 4 hasta llegar a destino
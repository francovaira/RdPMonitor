import os
from bs4 import BeautifulSoup

def clean_file(text):
    """Elimina los salto de linea, espacios y palabras sobrantes en el archivo para luego ser procesado 
    correctamente en otro script de python. \n
    Crea un archivo temporal para trabajar y al final lo elimina.

    Parameters \n
    ----------
        text -- Archivo html que fue convertido a txt.
    """

    # En las siguiente lineas de código se abren y se cierran dos archivos, los cuales 
    # son leídos y escritos para dejar el archivo "limpio" para el próximo script. 
    f = open ("matricesI.txt", "w")
    f.write(text)
    f.close()

    f1 = open('matricesI.txt', 'r')
    f2 = open('matricesI.txt.tmp', 'w')
    for line in f1:
        f2.write(line.replace('\n', ' '))
    f1.close()
    f2.close()

    # f1 = open('matricesI.txt.tmp', 'r')
    # f2 = open('matricesI.txt', 'w')
    # for line in f1:
    #     f2.write(line.replace('I + ', 'I +\n'))
    # f1.close()
    # f2.close()

    # f1 = open('matricesI.txt', 'r')
    # f2 = open('matricesI.txt.tmp', 'w')
    # for line in f1:
    #     f2.write(line.replace('I - ', 'I -\n'))
    # f1.close()
    # f2.close()

    f1 = open('matricesI.txt.tmp', 'r')
    f2 = open('matricesI.txt', 'w')
    for line in f1:
        print('s1 and s2 are equal')
        # if (line == 'incidence'):
    # f2.write(line.replace(' incidence ', '\0incidence'))
    # f1.close()
    # f2.close()
    # sleep(2)
    exit()

    f1 = open('matricesI.txt', 'r')
    f2 = open('matricesI.txt.tmp', 'w')
    for line in f1:
        f2.write(line.replace('Back', '\nBack'))
    f1.close()
    f2.close()

    f1 = open('matricesI.txt.tmp', 'r')
    f2 = open('matricesI.txt', 'w')
    for line in f1:
        f2.write(line.replace('P', '\nP'))
    f1.close()
    f2.close()

    f1 = open('matricesI.txt', 'r')
    f2 = open('matricesI.txt.tmp', 'w')
    for line in f1:
        f2.write(line.replace('Combined', '\nCombined'))
    f1.close()
    f2.close()

    f1 = open('matricesI.txt.tmp', 'r')
    f2 = open('matricesI.txt', 'w')
    for line in f1:
        f2.write(line.replace('', ''))
    f1.close()
    f2.close()

    f1 = open('matricesI.txt', 'r')
    f2 = open('matricesI.txt.tmp', 'w')
    for line in f1:
        if(line.find('Forwa')!=-1):
            break
        else:
            f2.write(line)
    f1.close()
    f2.close()

    # #Elimina archivo temporal
    # os.remove("matricesI.txt.tmp")

# def main():
    # Abre un archivo html a partir del path indicado por consola, y lo carga en un archivo
    # BeatifulSoup para extraer los datos html de dicho archivo.
# archivo = input("ejemplo.html")
html = open("./ejemplo.html",'r')
soup = BeautifulSoup(html,'lxml')

# Elimina todos elementos de estilo
for script in soup(["style"]):
    script.extract()

# Obtener texto del archivo BeautifulSoup
text = soup.get_text(separator='\n', strip=True)

# Elimina los saltos de lina y los espacios al principio y al final de cada línea
lines = (line.strip() for line in text.split("\n"))

# Separa varios encabezados en cada linea
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

# Elimina líneas en blanco
text = '\n'.join(chunk for chunk in chunks if chunk)

clean_file(text)
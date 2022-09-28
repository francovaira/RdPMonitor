import os
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def combined_incidence():
    f = open ("matricesI.txt", "w")
    f.write(get_text())
    f.close()

    f1 = open('matricesI.txt', 'r')
    f2 = open('matricesI.txt.tmp', 'w')
    for line in f1:
        line = re.sub(r"T\d+", '', line)
        line = line.replace('\n', ' ')
        line = re.sub(r"P\d+\s", '\n', line)
        line = line.replace('Combined', '\nCombined')
        f2.write(line)
    f1.close()
    f2.close()

    f1 = open('matricesI.txt.tmp', 'r')
    f2 = open('matricesI.txt', 'w')
    for line in f1:
        if(line.find('Combined')!=-1):
            for line in f1:
                if(line.find('Inhibition')!=-1):
                    break
                else:
                    f2.write(line)
        else:
            continue
    f1.close()
    f2.close()

    f1 = open('matricesI.txt', 'r')
    f2 = f1.read()
    
    transitions = transitions_count('matricesI.txt')
    my_list = f2.split()

    composite_list = [my_list[x:x+transitions] for x in range(0, len(my_list),transitions)]

    #Elimina archivo temporal
    f1.close()
    os.remove("matricesI.txt")
    os.remove("matricesI.txt.tmp")

    final_list = []
    for x in composite_list:
        temp = list(map(int, x))
        final_list.append(temp)
        
    return final_list

def transitions_count(file_name):
    file = open(file_name, 'r')
    file = file.readline()
    return len(file.split())

def initial_marking():
    f = open ("matricesI.txt", "w")
    f.write(get_text())
    f.close()

    f1 = open('matricesI.txt', 'r')
    f2 = open('matricesI.txt.tmp', 'w')
    for line in f1:
        if(line.find('Initial')!=-1):
            for line in f1:
                if(line.find('Current')!=-1):
                    break
                else:
                    f2.write(line)
        else:
            continue
    f1.close()
    f2.close()

    f1 = open('matricesI.txt.tmp', 'r')
    f2 = open('matricesI.txt', 'w')
    for line in f1:
        line = line.replace('\n', ' ')
        f2.write(line)
    f1.close()
    f2.close()
    os.remove("matricesI.txt.tmp")
    
    f1 = open('matricesI.txt', 'r')
    f2 = f1.read()
    my_list = f2.split()
    marking = list(map(int, my_list))
    f1.close()
    os.remove("matricesI.txt")

    return marking


def get_text():
    # Abre un archivo html a partir del path indicado por consola, y lo carga en un archivo
    # BeatifulSoup para extraer los datos html de dicho archivo.
    html = open(os.getenv('MATRIZ_HTML_PATH'),'r')
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

    return text
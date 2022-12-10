import re
import numpy as np
from PIL import Image

#Primero hay que abrir el archivo codigo.txt para leer las instrucciones.

f = open('codigo.txt', 'r')
lines = f.readlines() #lines es una lista con todas las lineas del archivo
f.close()
string = "" #string junta todas las lineas con instrucciones en una sola.
for i in range(3, len(lines)):
    string = string+lines[i]
ancho = re.findall(r'\d+', str(lines[0])) #se consigue el ancho se la imagen
ancho = int(ancho[0])

color = re.findall(r'Negro|Blanco|Verde|Rojo|Azul|\(\d+,\d+,\d+\)', str(lines[1])) #y el color


#Funcion: colorDefondo(color)
#Transforma el string del objeto de regex color es una tupla con los valores RGB.
#Por ejemplo: si color[0] = "Azul", colorDeFondo retornara la tupla de enteros (0,0,255)
#
#Parametros:
#   color (objeto regex): objeto de regex que tiene el string con el color en un grupo de captura.
#
#Retorno:
#   rgb (int): tupla de enteros con el color en RGB.
#

def colorDeFondo(color):
    if str(color[0]) == "Negro":
        return (0,0,0)

    elif str(color[0]) == "Blanco":
        return (255,255,255)

    elif str(color[0]) == "Azul":
        return (0,0,255)

    elif str(color[0]) == "Rojo":
        return (255,0,0)

    elif str(color[0]) == "Verde":
        return (0,255,0)

    else:
        rgb = []
        valores = re.findall(r'\d+', color[0])
        rgb.append(valores[0])
        rgb.append(valores[1])
        rgb.append(valores[2])
        return tuple(rgb)

fondo = colorDeFondo(color) #Se guarda la tupla para mas tarde

#Se definen los tres regex que seran utilizados
#regexPrimero separa todas las instrucciones en un solo grupo de captura
#regexBueno toma las instrucciones aisladas y separa la informacion importante en distintos grupos de captura
#regexSintaxis sirve para detectar errores de sintaxis en el archivo

regexPrimero = r"(Pintar (?:Negro|Blanco|Verde|Rojo|Azul|(?:RGB\(\d+,\d+,\d+\)))|Avanzar(?: \d+)?|Izquierda|Derecha|(?:Repetir (?:\d+) veces (?:\{(?:\s|.)*\})))"
regexBueno = r"((Pintar) (Negro|Blanco|Verde|Rojo|Azul|(?:(RGB)\((\d+,\d+,\d+)\)))|(Avanzar)(?: )?(\d+)?|Izquierda|Derecha|(?:(Repetir) (\d+) veces (\{(?:\s|.)*\})))"
regexSintaxis = r"(Pintar (?:Negro|Blanco|Verde|Rojo|Azul|(?:RGB\(\d+,\d+,\d+\)))|Avanzar(?: \d+)?|Izquierda|Derecha|(?:Repetir (?:\d+) veces)|[\{\}])"

flag = True #flag servira para determinar si crear o no la imagen pixelart.png
f = open('errores.txt', 'w')
for i in range(3,(len(lines)-1)):
    linea = re.findall(regexSintaxis, str(lines[i])) #se usa regexSintaxis para aislar todo lo que esta "bien escrito"
    stringAux = ""
    for j in linea:
        stringAux = stringAux + " " + j
    #Se compara lo que capto regexSintaxis con la linea original, si son distintos esto quiere decir que hay algo en la linea original que no esta "bien escrito"
    if len(stringAux) != (len(lines[i].strip()) + 1):
        flag = False #se cambia flag a False
        f.write(str(i+1)+" "+lines[i].strip()+"\n") #y se registra la linea con el error en errores.txt

if flag == True: #si flag es True quiere decir que no se encontro ningun error de sintaxis.
    f.write("No hay errores!")

f.close()
pos = [0, 0, "E"] #pos lleva cuentas de la posicion del "Jugador" para saber que parte de la matriz pintar, hacia donde avanzar y hacia donde girar


#Funcion: avanzar(pos, ins)
#Ejecuta la instruccion Avanzar tomando en cuenta la posicion y hacia donde mira el "Jugador"
#
#Parametros:
#   pos (int, int, str): posicion actual.
#   ins (objeto regex): objeto con las especificaciones de la instruccion.
#Retorno:
#   pos (int, int, str): posicion actualizada luego de avanzar.
#

def avanzar(pos, ins):
    if ins[0][6] == "1" or str(ins[0][6]) == "":
        if pos[2] == "N":
            pos[0]-=1
        elif pos[2] == "S":
            pos[0]+=1
        elif pos[2] == "E":
            pos[1]+=1
        elif pos[2] == "O":
            pos[1]-=1
    else:
        if pos[2] == "N":
            pos[0]-=int(ins[0][6])
        elif pos[2] == "S":
            pos[0]+=int(ins[0][6])
        elif pos[2] == "E":
            pos[1]+=int(ins[0][6])
        elif pos[2] == "O":
            pos[1]-=int(ins[0][6])
    return pos


#Funcion: derecha(pos)
#Ejecuta la instruccion Derecha tomando en cuenta hacia donde mira el "Jugador"
#
#Parametros:
#   pos (int, int, str): posicion actual.
#Retorno:
#   pos (int, int, str): posicion actualizada luego de girar a la derecha.
#

def derecha(pos):
    if pos[2] == "N":
        pos[2] = "E"
    elif pos[2] == "S":
        pos[2] = "O"
    elif pos[2] == "E":
        pos[2] = "S"
    elif pos[2] == "O":
        pos[2] = "N"
    return pos

#Funcion: izquierda(pos)
#Ejecuta la instruccion Izquierda tomando en cuenta hacia donde mira el "Jugador"
#
#Parametros:
#   pos (int, int, str): posicion actual.
#Retorno:
#   pos (int, int, str): posicion actualizada luego de girar a la izquierda.
#

def izquierda(pos):
    if pos[2] == "N":
        pos[2] = "O"
    elif pos[2] == "S":
        pos[2] = "E"
    elif pos[2] == "E":
        pos[2] = "N"
    elif pos[2] == "O":
        pos[2] = "S"
    return pos

#Funcion: pintar(pos, ins, matrix)
#Ejecuta la instruccion Pintar tomando en cuenta la posicion actual y el color que se desea aplicar.
#
#Parametros:
#   pos (int, int, str): posicion actual.
#   ins (objeto regex): objeto con las especificaciones de la instruccion.
#   matrix ((int,int,int)): matriz desde la cual se generará la imagen pixelart.png
#Retorno:
#   matrix ((int,int,int)): matriz actualizada luego de pintar.
#

def pintar(pos, ins, matrix):
    if str(ins[0][2]) == "Negro":
        matrix[pos[0]][pos[1]] = (0,0,0)

    elif str(ins[0][2]) == "Blanco":
        matrix[pos[0]][pos[1]] = (255,255,255)

    elif str(ins[0][2]) == "Azul":
        matrix[pos[0]][pos[1]] = (0,0,255)

    elif str(ins[0][2]) == "Rojo":
        matrix[pos[0]][pos[1]] = (255,0,0)

    elif str(ins[0][2]) == "Verde":
        matrix[pos[0]][pos[1]] = (0,255,0)

    elif str(ins[0][3]) == "RGB":
        rgb = list(re.split(r",", ins[0][4]))
        for i in range(len(rgb)):
            rgb[i] = int(rgb[i])
        matrix[pos[0]][pos[1]] = tuple(rgb)

    return matrix

#Funcion: repetir (regex, regex2, ins, matrix, pos)
#Ejecuta las instrucciones dentro de un repetir utilizando recursividad.
#
#Parametros:
#   regex (regex): regexBueno definido anteriormente, servirá para aplicar recursión.
#   regex2 (regex): regexPrimero definido anteriormente, servirá para aplicar recursión.
#   ins (objeto regex): objeto con las especificaciones de la instruccion.
#   matrix ((int,int,int)): matriz desde la cual se generará la imagen pixelart.png
#   pos (int, int, str): posicion actual.
#Retorno:
#   matrix ((int,int,int)): matriz actualizada luego aplicar las instrucciones de Repetir y siguientes.
#   pos ((int, int, str)): posición actualizada luego aplicar las instrucciones de Repetir y siguientes.
#
#---------------------------------------------------------------------------------------------------------------#
#regexBueno separa todas las instrucciones pero con la instruccion Repetir pasa algo distinto.
#Cuando encuentra un repetir y luego fuera de este otro repetir mas, juntara todo lo que hay entre el el primer "{" del primer repetir y el último "}" del
#último repetir. Debido a esto se utiliza paridad de parentesis para separar lo que va dentro del primer repetir de lo que le sigue en la cadena de
#instrucciones.

def repetir (regex, regex2, ins, matrix, pos):
    counter = 0
    l = ins[0][9]
    for i in range(len(l)): #en este "for" es donde se revisa la paridad de parentesis.
        if l[i] == '{':
            counter+=1
        elif l[i] == '}':
            counter -=1
        if counter == 0:
            string1 = l[1:i]
            string2 = l[i+1:len(l)] #cuando la encuentra separa el string.
            break 
    instrucciones1 = re.findall(regex2, string1) #encuentra la cadena de instrucciones para ambos strings.
    instrucciones2 = re.findall(regex2, string2) #string1 es lo que va dentro del repetir y string2 es lo que le sigue.
    for i in range(int(ins[0][8])): #se repite la cantidad de veces necesaria guardada en el grupo de captura 8 las instrucciones del string 1
        for instru in instrucciones1:
            matrix, pos = ejecutarInstrucciones(regex, regex2, instru, pos, matrix)
    
    if string2 != "\n": #el string2 puede ser solo un salto de linea lo que pasa cuando el repetir esta al final de codigo.txt. en este caso no es necesario hacer nada mas.
        for instru in instrucciones2:
            matrix, pos = ejecutarInstrucciones(regex, regex2, instru, pos, matrix) #si string2 != "\n" ejecuta las instrucciones faltantes fuera del repetir.

    return matrix, pos

#Funcion: ejecutarInstrucciones(regex, regex2, string, pos, matrix)
#Separa las instrucciones y las ejecuta una a una llamando a las funciones antes definidas.
#
#Parametros:
#   regex (regex): regexBueno definido anteriormente, servirá para aplicar recursión.
#   regex2 (regex): regexPrimero definido anteriormente, servirá para aplicar recursión.
#   string (str): string con las instrucciones en una sola linea.
#   pos (int, int, str): posicion actual.
#   matrix ((int,int,int)): matriz desde la cual se generará la imagen pixelart.png
#Retorno:
#   matrix ((int,int,int)): matriz actualizada luego aplicar las instrucciones.
#   pos ((int, int, str)): posición actualizada luego aplicar las instrucciones.
#

def ejecutarInstrucciones(regex, regex2, string, pos, matrix):
    ins = re.findall(regex, string) #regexSeparar
    if ins[0][5] == "Avanzar":
        pos = avanzar(pos, ins)
    elif ins[0][0] == "Derecha":
        pos = derecha(pos)
    elif ins[0][0] == "Izquierda":
        pos = izquierda(pos)
    elif ins[0][1] == "Pintar":
        matrix = pintar(pos, ins, matrix)
    elif ins[0][7] == "Repetir":
        matrix, pos = repetir(regex, regex2, ins, matrix, pos)
    return matrix, pos

#Funcion: MatrizAImagen(matriz, filename='pixelart.png', factor=10)
#Funcion entregada para generar la imagen a partir de la matriz creada.

def MatrizAImagen(matriz, filename='pixelart.png', factor=10):
    '''
    Convierte una matriz de valores RGB en una imagen y la guarda como un archivo png.
    Las imagenes son escaladas por un factor ya que con los ejemplos se producirian imagenes muy pequeñas.
        Parametros:
                matriz (lista de lista de tuplas de enteros): Matriz que representa la imagen en rgb.
                filename (str): Nombre del archivo en que se guardara la imagen.
                factor (int): Factor por el cual se escala el tamaño de las imagenes.
    '''
    matriz = np.array(matriz, dtype=np.uint8)
    np.swapaxes(matriz, 0, -1)

    N = np.shape(matriz)[0]

    img = Image.fromarray(matriz, 'RGB')
    img = img.resize((N*10, N*10), Image.Resampling.BOX)
    img.save(filename)


if flag == True:    #Solo seguir con el proceso si no hay errores de sintaxis.

    value = np.empty((), dtype=object) #construir el array con el color base
    value[()] = fondo
    a = np.full((ancho, ancho), value, dtype=object)

    instrucciones = re.findall(regexPrimero, string) #Primera instancia de reconocimiento de instrucciones.
    for i in instrucciones:
        a, pos = ejecutarInstrucciones(regexBueno, regexPrimero, str(i), pos, a) #Ejecutarlas una a una.

    matriz = [] #para poder generar la imagen hay que transformar la matriz de tipo numpy.array a una lista de listas de python
    for i in range(ancho):
        matriz.append([])
        for j in range(ancho):
            matriz[i].append(a[i][j])

    MatrizAImagen(matriz) #generacion de la imagen.
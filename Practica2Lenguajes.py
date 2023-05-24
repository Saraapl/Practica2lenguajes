from dataclasses import dataclass, field
from typing import Optional, Tuple


def buscar(x: tuple, a):
  for i in range(len(x)):
    if x[i] == a:
      return i
  return -1


@dataclass
class Carpeta():
  nombre: str
  numero_elementos: int

  def __eq__(self, otro: object) -> bool:
    if not isinstance(otro, Carpeta):
      return False
    return self.nombre == otro.nombre


@dataclass
class Archivo():
  nombre: str
  extension: str
  peso: int

  def __eq__(self, otro: object) -> bool:
    if not isinstance(otro, Archivo):
      return False
    return self.nombre == otro.nombre and self.extension == otro.extension


@dataclass
class NodoPersistente():
  valor: Archivo | Carpeta
  hijos: Tuple[Optional["NodoPersistente"], Optional["NodoPersistente"],
               Optional["NodoPersistente"],
               Optional["NodoPersistente"]] = field(default=(None, None, None,
                                                             None))

  def __str__(self):
    return f"{self.valor}"


def set_hijo(actual: NodoPersistente, hijo: Optional[NodoPersistente],
             idx: int):
  assert isinstance(actual.valor, Carpeta)
  #hasta la posicion indice, pegar el hijo nuevo, desde indice + 1
  hijos = (*actual.hijos[:idx], hijo, *actual.hijos[idx + 1:])
  return NodoPersistente(
    Carpeta(actual.valor.nombre, actual.valor.numero_elementos), hijos)


def cambiar_valor(actual: NodoPersistente, valor: Archivo | Carpeta):
  #si es una carpeta y la edito, dejar el mismo numero de elementos
  if isinstance(actual.valor, Carpeta):
    copia = Carpeta(valor.nombre, actual.valor.numero_elementos)
    return NodoPersistente(copia, actual.hijos)
  return NodoPersistente(valor, actual.hijos)


def insertar(actual: Optional[NodoPersistente], carpeta_madre: str,
             valor: NodoPersistente):
  if actual is None or isinstance(actual.valor,
                                  Archivo):  #archivo es punto muerto
    return actual

  if actual.valor.nombre == carpeta_madre:
    if actual.valor.numero_elementos >= 4:
      print("No se puede insertar, la carpeta esta llena")
      return actual
    primera_vacia = buscar(actual.hijos, None)  # Primera posicion vacia
    nuevo = Carpeta(actual.valor.nombre, actual.valor.numero_elementos + 1)
    copia = cambiar_valor(actual, nuevo)
    return set_hijo(copia, valor, primera_vacia)

  copia = actual
  for i in range(4):
    hijo = actual.hijos[i]
    copia = set_hijo(copia, insertar(hijo, carpeta_madre, valor), i)
  return copia


def modificar(actual: Optional[NodoPersistente], carpeta_madre: str,
              viejo: Archivo | Carpeta, nuevo: Archivo | Carpeta):
  if actual is None or isinstance(actual.valor, Archivo):
    #Llego a un archivo o a un punto muerto
    return actual

  copia = actual
  if actual.valor.nombre == carpeta_madre:
    encontrado = False
    for i in range(4):
      hijo = actual.hijos[i]
      if hijo and hijo.valor == viejo:
        encontrado = True
        copia = set_hijo(copia, cambiar_valor(hijo, nuevo), i)
      else:
        copia = set_hijo(copia, hijo, i)

    if not encontrado:
      print("No se encontro el valor viejo en la carpeta madre")

    return copia

  for i in range(4):
    hijo = actual.hijos[i]
    copia = set_hijo(copia, modificar(hijo, carpeta_madre, viejo, nuevo), i)
  return copia


def imprimir_arbol(actual: NodoPersistente | None, nivel: int, idx: int):
  if actual is None:
    return
  print("│   " * nivel, end="")
  if idx == 3:
    print("└──", end="")
  else:
    print("├──", end="")
  print(actual.valor)
  for i, hijo in enumerate(actual.hijos):
    imprimir_arbol(hijo, nivel + 1, i)


def nombre_mas_largo(actual: NodoPersistente):
  if isinstance(actual.valor, Archivo):
    return f"{actual.valor.nombre}.{actual.valor.extension}"

  maximo_actual = ""
  for i in range(4):
    hijo = actual.hijos[i]
    if hijo:
      maximo_hijo = nombre_mas_largo(hijo)
      if len(maximo_hijo) > len(maximo_actual):
        maximo_actual = maximo_hijo

  return maximo_actual


def obtener_ruta(actual: NodoPersistente, objetivo: Archivo | Carpeta,
                 ruta: str):
  if actual.valor == objetivo and isinstance(actual.valor, Archivo):
    return ruta + "/" + actual.valor.nombre + "." + actual.valor.extension

  if actual.valor == objetivo and isinstance(actual.valor, Carpeta):
    return ruta + "/" + actual.valor.nombre

  resultado = None
  for i in range(4):
    hijo = actual.hijos[i]
    if not hijo: continue
    hijo_ruta = obtener_ruta(hijo, objetivo, ruta + "/" + actual.valor.nombre)
    if hijo_ruta:
      resultado = hijo_ruta
  return resultado


def menu():
  nombres = set()
  nombres.add("raiz")

  def modificar_archivo(raiz):
    print("Escriba el nombre del archivo que desea modificar")
    nombre_viejo = input()
    print("Escriba la extension del archivo que desea modificar")
    extension_vieja = input()
    print(
      "Escriba el nombre de la carpeta madre donde está alojado el archivo que desea modificar"
    )
    madre = input()
    print("Escriba el nuevo nombre del archivo")
    nuevo_nombre = input()
    if nuevo_nombre in nombres:
      print("El nombre ya existe, no se puede agregar")
      return raiz
    nombres.add(nuevo_nombre)
    print("Escriba la nueva extension del archivo")
    nueva_extension = input()
    print("Escriba el nuevo peso del archivo")
    nuevo_peso = int(input())
    viejo = Archivo(nombre_viejo, extension_vieja, peso=-1)
    nuevo = Archivo(nuevo_nombre, nueva_extension, nuevo_peso)
    return modificar(raiz, madre, viejo, nuevo)

  def modificar_carpeta(raiz):
    print("Escriba el nombre de la carpeta que desea modificar")
    nombreviejo = input()
    if nombreviejo == "raiz":
      print("No se puede modificar la raiz")
      return raiz
    print(
      "Escriba el nombre de la carpeta madre donde está alojada la carpeta que desea modificar"
    )
    madre = input()
    print("Escriba el nuevo nombre de la carpeta")
    nuevonombre = input()
    if nuevonombre in nombres:
      print("El nombre ya existe, no se puede agregar")
      return
    nombres.add(nuevonombre)
    nueva = Carpeta(nuevonombre, 0)
    vieja = Carpeta(nombreviejo, 0)
    return modificar(raiz, madre, vieja, nueva)

  def agregar_carpeta(raiz):
    print(
      "Escriba el nombre de la carpeta madre donde desea alojar la nueva carpeta"
    )
    carpeta_madre = input()
    print("Escriba el nombre de la nueva carpeta")
    nombre_nueva_carpeta = input()
    if nombre_nueva_carpeta in nombres:
      print("El nombre ya existe, no se puede agregar")
      return raiz
    nombres.add(nombre_nueva_carpeta)
    nueva_carpeta = Carpeta(nombre=nombre_nueva_carpeta, numero_elementos=0)
    return insertar(raiz, carpeta_madre, NodoPersistente(nueva_carpeta))

  def agregar_archivo(raiz):
    print(
      "Escriba el nombre de la carpeta madre donde desea alojar el nuevo archivo"
    )
    carpeta_madre = input()
    print("Escriba el nombre del nuevo archivo")
    nombre_nuevo_archivo = input()
    if nombre_nuevo_archivo in nombres:
      print("El nombre ya existe, no se puede agregar")
      return raiz
    nombres.add(nombre_nuevo_archivo)
    print("Escriba la extensión del archivo")
    extension = input()
    print("Escriba el peso del archivo")
    peso = int(input())
    nuevo_archivo = Archivo(nombre_nuevo_archivo, extension, peso)
    return insertar(raiz, carpeta_madre, NodoPersistente(nuevo_archivo))

  def ruta_nombre_mas_largo(raiz):
    nombre_largo = nombre_mas_largo(raiz)
    if nombre_largo == "":
      print("No hay archivos en el árbol")
      return
    nombre, extension = nombre_largo.split(".")
    resultado = obtener_ruta(raiz, Archivo(nombre, extension, 0), "")
    print("La ruta del archivo con el nombre más largo es: ", resultado)

  raiz = NodoPersistente(Carpeta("raiz", 0))
  while True:
    print(
      "Bienvenido, presione 1 para agregar un archivo, 2 para agregar una carpeta, 3 para modificar un archivo, 4 para modificar una carpeta, 5 para imprimir el árbol, 6 para obtener la ruta del archivo con el nombre más largo"
    )
    opcion = int(input())
    if opcion == 1:
      raiz = agregar_archivo(raiz)
    elif opcion == 2:
      raiz = agregar_carpeta(raiz)
    elif opcion == 3:
      raiz = modificar_archivo(raiz)
    elif opcion == 4:
      raiz = modificar_carpeta(raiz)
    elif opcion == 5:
      imprimir_arbol(raiz, nivel=0, idx=0)
    elif opcion == 6:
      ruta_nombre_mas_largo(raiz)
    else:
      print("Opción inválida")


if __name__ == "__main__":
  menu()

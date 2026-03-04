# planetas

Proyecto de ejemplo que contiene código en C++ y scripts de visualización en Python para simular y visualizar órbitas.

Cómo subir a GitHub (si el push falla por autenticación, sigue las instrucciones):

1. Inicializar repo (si no está inicializado):

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/wilfergv9/planetas
git push -u origin main
```

Archivos principales:
- `solar_system.cpp`
- `visualizar_orbitas.py`
- `orbits.csv`

Licence: sin especificar

## Ejecución del proyecto

1. **Compilar el simulador** (requiere g++ con soporte OpenMP):

```bash
g++ solar_system.cpp -fopenmp -O2 -o solar_system
```

2. **Generar las órbitas**

```bash
# ejecuta la simulación; puedes cambiar el número de años (por defecto 10)
./solar_system [años]
```

   El programa creará (o sobrescribirá) `orbits.csv` en el directorio actual.

3. **Visualizar los resultados**

   - Asegúrate de tener Python 3 y las dependencias instaladas:

     ```bash
     pip install matplotlib pandas numpy
     ```

   - Ejecuta el script de visualización en la misma carpeta donde esté `orbits.csv`:

     ```bash
     python visualizar_orbitas.py
     ```

   - Se abrirá una ventana con una animación del sistema solar. Presiona **Ctrl+C** en la terminal para cerrar la animación si es necesario.

> 💡 Si quieres rehacer la simulación con más años o parámetros distintos, simplemente recompila (si modificaste el código) y vuelve a ejecutar `./solar_system`.

Archivos principales:
- `solar_system.cpp`
- `visualizar_orbitas.py`
- `orbits.csv`

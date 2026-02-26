#include <iostream>
#include <fstream>
#include <string>
#include <math.h>
#include <vector>

struct Vector3
{
    double e[3] = { 0 };

    Vector3() {}
    ~Vector3() {}

    inline Vector3(double e0, double e1, double e2)
    {
        this->e[0] = e0;
        this->e[1] = e1;
        this->e[2] = e2;
    }
};

struct OrbitalEntity
{
    double e[7] = { 0 };

    OrbitalEntity() {}
    ~OrbitalEntity() {}

    inline OrbitalEntity(double e0, double e1, double e2, double e3, double e4, double e5, double e6)
    {
        this->e[0] = e0;
        this->e[1] = e1;
        this->e[2] = e2;
        this->e[3] = e3;
        this->e[4] = e4;
        this->e[5] = e5;
        this->e[6] = e6;
    }
};

int main()
{
    OrbitalEntity* orbital_entities;
    int N_ASTEROIDS = 0;
    int N_BODIES = 9 + N_ASTEROIDS;
    orbital_entities = (OrbitalEntity*)malloc(sizeof(OrbitalEntity) * N_BODIES);

    orbital_entities[0] = { 0.0,0.0,0.0,        0.0,0.0,0.0,        1.989e30 };       // Sol
    orbital_entities[1] = { 57.909e9,0.0,0.0,   0.0,47.36e3,0.0,    0.33011e24 };     // Mercurio
    orbital_entities[2] = { 108.209e9,0.0,0.0,  0.0,35.02e3,0.0,    4.8675e24 };      // Venus
    orbital_entities[3] = { 149.596e9,0.0,0.0,  0.0,29.78e3,0.0,    5.9724e24 };      // Tierra
    orbital_entities[4] = { 227.923e9,0.0,0.0,  0.0,24.07e3,0.0,    0.64171e24 };     // Marte
    orbital_entities[5] = { 778.570e9,0.0,0.0,  0.0,13e3,0.0,       1898.19e24 };     // Júpiter
    orbital_entities[6] = { 1433.529e9,0.0,0.0, 0.0,9.68e3,0.0,     568.34e24 };      // Saturno
    orbital_entities[7] = { 2872.463e9,0.0,0.0, 0.0,6.80e3,0.0,     86.813e24 };      // Urano
    orbital_entities[8] = { 4495.060e9,0.0,0.0, 0.0,5.43e3,0.0,     102.413e24 };     // Neptuno

    double t_0 = 0;
    double t = t_0;
    double dt = 86400;                  // 1 día en segundos
    double t_end = 86400 * 365 * 10;   // 10 años en segundos
    double BIG_G = 6.67e-11;

    // -------------------------------------------------------
    // EXPORTACIÓN A CSV
    // Cada fila: tiempo, x0,y0,z0, x1,y1,z1, ... x8,y8,z8
    // -------------------------------------------------------
    // Puedes cambiar el nombre del archivo o la ruta según tu sistema
    std::ofstream csv_file("orbits.csv");

    // Encabezado del CSV
    csv_file << "t";
    std::string names[] = {"Sol","Mercurio","Venus","Tierra","Marte","Jupiter","Saturno","Urano","Neptuno"};
    for (int i = 0; i < N_BODIES; i++)
        csv_file << "," << names[i] << "_x," << names[i] << "_y," << names[i] << "_z";
    csv_file << "\n";

    // Guardar estado inicial
    csv_file << t;
    for (int i = 0; i < N_BODIES; i++)
        csv_file << "," << orbital_entities[i].e[0] << "," << orbital_entities[i].e[1] << "," << orbital_entities[i].e[2];
    csv_file << "\n";

    // Frecuencia de muestreo: guardar cada SAMPLE_EVERY pasos
    // Con dt=1 día y 10 años => 3650 pasos. Guardamos cada día (todos los pasos).
    // Si la simulación fuera más larga, puedes subir este valor.
    int SAMPLE_EVERY = 1;
    int step = 0;

    std::cout << "Iniciando simulación..." << std::endl;

    while (t < t_end)
    {
        // Calcular aceleraciones y actualizar velocidades
        for (size_t m1_idx = 0; m1_idx < N_BODIES; m1_idx++)
        {
            Vector3 a_g = { 0,0,0 };

            for (size_t m2_idx = 0; m2_idx < N_BODIES; m2_idx++)
            {
                if (m1_idx != m2_idx)
                {
                    Vector3 r_vector;
                    r_vector.e[0] = orbital_entities[m1_idx].e[0] - orbital_entities[m2_idx].e[0];
                    r_vector.e[1] = orbital_entities[m1_idx].e[1] - orbital_entities[m2_idx].e[1];
                    r_vector.e[2] = orbital_entities[m1_idx].e[2] - orbital_entities[m2_idx].e[2];

                    double r_mag = sqrt(r_vector.e[0] * r_vector.e[0] +
                                        r_vector.e[1] * r_vector.e[1] +
                                        r_vector.e[2] * r_vector.e[2]);

                    double acceleration = -1.0 * BIG_G * orbital_entities[m2_idx].e[6] / pow(r_mag, 2.0);
                    Vector3 r_unit_vector = { r_vector.e[0] / r_mag, r_vector.e[1] / r_mag, r_vector.e[2] / r_mag };

                    a_g.e[0] += acceleration * r_unit_vector.e[0];
                    a_g.e[1] += acceleration * r_unit_vector.e[1];
                    a_g.e[2] += acceleration * r_unit_vector.e[2];
                }
            }

            orbital_entities[m1_idx].e[3] += a_g.e[0] * dt;
            orbital_entities[m1_idx].e[4] += a_g.e[1] * dt;
            orbital_entities[m1_idx].e[5] += a_g.e[2] * dt;
        }

        // Actualizar posiciones
        for (size_t entity_idx = 0; entity_idx < N_BODIES; entity_idx++)
        {
            orbital_entities[entity_idx].e[0] += orbital_entities[entity_idx].e[3] * dt;
            orbital_entities[entity_idx].e[1] += orbital_entities[entity_idx].e[4] * dt;
            orbital_entities[entity_idx].e[2] += orbital_entities[entity_idx].e[5] * dt;
        }

        t += dt;
        step++;

        // Guardar en CSV según la frecuencia de muestreo
        if (step % SAMPLE_EVERY == 0)
        {
            csv_file << t;
            for (int i = 0; i < N_BODIES; i++)
                csv_file << "," << orbital_entities[i].e[0]
                         << "," << orbital_entities[i].e[1]
                         << "," << orbital_entities[i].e[2];
            csv_file << "\n";
        }
    }

    csv_file.close();
    std::cout << "Simulación completa. Datos exportados a orbits.csv" << std::endl;
    std::cout << "Pasos totales: " << step << std::endl;

    free(orbital_entities);
    return 0;
}

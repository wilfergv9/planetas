#include <iostream>
#include <fstream>
#include <string>
#include <math.h>
#include <random>
#include <vector>
#include <omp.h>  // OpenMP for parallelization

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

int main(int argc, char** argv)
{
    OrbitalEntity* orbital_entities;
    // Número objetivo de cuerpos (incluye el Sol y los 8 planetas)
    int N_ASTEROIDS = 491; // 500 total - 9 existentes = 491
    int N_BODIES = 9 + N_ASTEROIDS;
    orbital_entities = (OrbitalEntity*)malloc(sizeof(OrbitalEntity) * N_BODIES);

    // Inicializar el Sol y los planetas conocidos
    orbital_entities[0] = { 0.0,0.0,0.0,        0.0,0.0,0.0,        1.989e30 };       // Sol
    orbital_entities[1] = { 57.909e9,0.0,0.0,   0.0,47.36e3,0.0,    0.33011e24 };     // Mercurio
    orbital_entities[2] = { 108.209e9,0.0,0.0,  0.0,35.02e3,0.0,    4.8675e24 };      // Venus
    orbital_entities[3] = { 149.596e9,0.0,0.0,  0.0,29.78e3,0.0,    5.9724e24 };      // Tierra
    orbital_entities[4] = { 227.923e9,0.0,0.0,  0.0,24.07e3,0.0,    0.64171e24 };     // Marte
    orbital_entities[5] = { 778.570e9,0.0,0.0,  0.0,13e3,0.0,       1898.19e24 };     // Júpiter
    orbital_entities[6] = { 1433.529e9,0.0,0.0, 0.0,9.68e3,0.0,     568.34e24 };      // Saturno
    orbital_entities[7] = { 2872.463e9,0.0,0.0, 0.0,6.80e3,0.0,     86.813e24 };      // Urano
    orbital_entities[8] = { 4495.060e9,0.0,0.0, 0.0,5.43e3,0.0,     102.413e24 };     // Neptuno

    // Constante gravitacional y distribución aleatoria para asteroides
    double BIG_G = 6.67e-11;
    std::mt19937_64 rng(42);
    std::uniform_real_distribution<double> dist_a(0.3 * 1.49596e11, 50.0 * 1.49596e11); // semi-ejes en m (0.3-50 AU)
    std::uniform_real_distribution<double> dist_theta(0.0, 2.0 * M_PI);
    std::uniform_real_distribution<double> dist_inc(-0.2, 0.2); // inclinación en radianes
    std::uniform_real_distribution<double> dist_mass(1e12, 1e20); // masas pequeñas

    for (int idx = 9; idx < N_BODIES; idx++) {
        double a = dist_a(rng);
        double theta = dist_theta(rng);
        double inc = dist_inc(rng);

        double x = a * cos(theta);
        double y = a * sin(theta) * cos(inc);
        double z = a * sin(theta) * sin(inc);

        // Velocidad circular aproximada alrededor del Sol
        double v = sqrt(BIG_G * orbital_entities[0].e[6] / a);
        double vx = -v * sin(theta);
        double vy = v * cos(theta) * cos(inc);
        double vz = v * cos(theta) * sin(inc);

        double mass = dist_mass(rng);
        orbital_entities[idx] = { x, y, z, vx, vy, vz, mass };
    }

    double t_0 = 0;
    double t = t_0;
    double dt = 86400;                  // 1 día en segundos

    // permitir especificar años de simulación en la línea de comandos
    double years = 10.0;
    if (argc > 1) {
        try {
            years = std::stod(argv[1]);
        } catch (...) {
            std::cerr << "Argument must be number of years; using default 10" << std::endl;
        }
    }
    double t_end = 86400 * 365 * years;   // años en segundos

    // OpenMP thread info
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        int nthreads = omp_get_num_threads();
        if (tid == 0) {
            std::cout << "OpenMP: usando " << nthreads << " threads\n";
        }
        std::cout << "  hilo " << tid << " inicializado\n";
    }

    // -------------------------------------------------------
    // EXPORTACIÓN A CSV
    // Cada fila: tiempo, x0,y0,z0, x1,y1,z1, ... x8,y8,z8
    // -------------------------------------------------------
    // Puedes cambiar el nombre del archivo o la ruta según tu sistema
    std::ofstream csv_file("orbits.csv");

    // Encabezado del CSV
    csv_file << "t";
    std::vector<std::string> names;
    names.push_back("Sol");
    names.push_back("Mercurio");
    names.push_back("Venus");
    names.push_back("Tierra");
    names.push_back("Marte");
    names.push_back("Jupiter");
    names.push_back("Saturno");
    names.push_back("Urano");
    names.push_back("Neptuno");

    // Generar nombres para los cuerpos añadidos (asteroides/satélites)
    for (int i = 9; i < N_BODIES; i++) {
        // Nombre tipo Asteroid001 ...
        char buf[32];
        snprintf(buf, sizeof(buf), "Asteroid%03d", i - 8);
        names.push_back(std::string(buf));
    }

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

    // performance measurement
    double sim_start = omp_get_wtime();
    double max_speed = 0.0;

    std::cout << "Iniciando simulación..." << std::endl;

    while (t < t_end)
    {
        // Calcular aceleraciones y actualizar velocidades
        // calcular aceleraciones en paralelo por cuerpo
        #pragma omp parallel for schedule(dynamic)
        for (int m1_idx = 0; m1_idx < N_BODIES; m1_idx++)
        {
            Vector3 a_g = { 0,0,0 };

            for (int m2_idx = 0; m2_idx < N_BODIES; m2_idx++)
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

            // compute speed magnitude
            double vx = orbital_entities[m1_idx].e[3];
            double vy = orbital_entities[m1_idx].e[4];
            double vz = orbital_entities[m1_idx].e[5];
            double speed = sqrt(vx*vx + vy*vy + vz*vz);
            #pragma omp critical
            if (speed > max_speed) max_speed = speed;
        }

        // Actualizar posiciones en paralelo
        #pragma omp parallel for schedule(static)
        for (int entity_idx = 0; entity_idx < N_BODIES; entity_idx++)
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
    double sim_end = omp_get_wtime();
    double elapsed = sim_end - sim_start;
    std::cout << "Simulación completa. Datos exportados a orbits.csv" << std::endl;
    std::cout << "Pasos totales: " << step << std::endl;
    std::cout << "Tiempo transcurrido: " << elapsed << " s (" << (step/elapsed) << " pasos/s)" << std::endl;
    std::cout << "Velocidad máxima registrada: " << max_speed << " m/s" << std::endl;

    free(orbital_entities);
    return 0;
}

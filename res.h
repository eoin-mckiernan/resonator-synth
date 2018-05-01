#include <cstddef>
#include <math.h>

class RES {
public:

	static void acalc(double freq, double q, int sr, double *a1, double *a2);

	static void filterArray(double *out, std::size_t out_size, const double *in, std::size_t in_size, double *z, std::size_t z_size, double a1, double a2);

	static double filter1(double *z,std::size_t z_size, double a1, double a2, double x);
};

#include <cstddef>
#include <math.h>

#include "res.h"

void RES::acalc(double freq, double q, int sr, double *a1, double *a2)
{
	double omega = 2*M_PI*freq/sr;
	double r = 1 - sin(omega/q);
	*a1 = -2*r*cos(omega);
	*a2 = pow(r,2);
	return;
}

double RES::filter1(double *z,std::size_t z_size, double a1, double a2, double x)
{
	double accin = x - a1*z[0] - a2*z[1];
	z[1] = z[0];
	z[0] = accin;
	return accin;
}

void RES::filterArray(double *out, std::size_t out_size, const double *in, std::size_t in_size, double *z, std::size_t z_size, double a1, double a2)
{
	for(int i = 0; i < in_size; i++)
	{
		out[i] = RES::filter1(z, z_size, a1, a2, in[i]);
	}
	return;
}

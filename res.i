%module res

%{
#define SWIG_FILE_WITH_INIT
#include "res.h"
%}

#include <typemaps.i>

%include <numpy.i>

%init %{
import_array();
%}

%apply (double* IN_ARRAY1, int DIM1) { (const double* in, std::size_t in_size) };
%apply double *OUTPUT { double* a1, double* a2 };
%apply (double* INPLACE_ARRAY1, int DIM1) { (double* out, std::size_t out_size) };
%apply (double* INPLACE_ARRAY1, int DIM1) { (double* z, std::size_t z_size) };

%include "res.h"

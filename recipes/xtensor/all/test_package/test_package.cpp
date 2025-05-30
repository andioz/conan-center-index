#ifdef XTENSOR_VERSION_LESS_0_26_0
#include "xtensor/xarray.hpp"
#include "xtensor/xio.hpp"
#include "xtensor/xview.hpp"
#else
#include "xtensor/containers/xarray.hpp"
#include "xtensor/io/xio.hpp"
#include "xtensor/views/xview.hpp"
#endif
#include <iostream>

int main(int argc, char *argv[]) {
  xt::xarray<double> arr1{{1.0, 2.0, 3.0}, {2.0, 5.0, 7.0}, {2.0, 5.0, 7.0}};

  xt::xarray<double> arr2{5.0, 6.0, 7.0};

  xt::xarray<double> res = xt::view(arr1, 1) + arr2;

  std::cout << res << std::endl;

  return 0;
}

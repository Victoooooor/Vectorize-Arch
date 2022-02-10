#ifndef IMAGESAMPLER_H
#define IMAGESAMPLER_H

#include "quasisampler_prototype.h"
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <pyboostcvconverter/pyboostcvconverter.hpp>

#define BOOST_LIB_NAME "boost_numpy"
#include <boost/config/auto_link.hpp>


namespace BN_Sample{

  namespace np = boost::python::numpy;
  namespace py = boost::python;

struct ChannelException : public std::exception
{
	const char * what () const throw ()
    {
    	return "Image Channel Exception";
    }
};
class ImageQuasisampler : public Quasisampler {
private:
  uint8_t *data;
  int channels, type;
  double mag;

public:
  
  ImageQuasisampler();
  ImageQuasisampler(PyObject *inputObject, double mag = 1.0);
    // virtual ~ImageQuasisampler();
  // Simple PGM parser (Low fault tolerance)
  bool loadImg(PyObject *inputObject, double mag = 1.0);

  unsigned getImportanceAt(Point2D pt);
  cv::Mat debugTool();
  cv::Mat getSampledPoints();
};
}
#endif // IMAGESAMPLER_H
/*

File: example3.cpp

An example of the use of the Quasisampler class.
Reminder: This is a toy implementation, created
to aid in understanding how the system works.

This example generates a set of points for a
grayscale bitmap.

Usage: example3 image.pgm [magnitude_factor=200]

This is a toy (non-optimized) implementation of the importance sampling
technique proposed in the paper:
"Fast Hierarchical Importance Sampling with Blue Noise Properties",
by Victor Ostromoukhov, Charles Donohue and Pierre-Marc Jodoin,
to be presented at SIGGRAPH 2004.


Implementation by Charles Donohue,
Based on Mathematica code by Victor Ostromoukhov.
Universite de Montreal
05.08.04

*/
#include <cstring>
#include <iostream>
#include <fstream>
#include "include/sampler/imagesampler.h"
#include <opencv2/highgui.hpp>
#include <opencv2/plot.hpp>

using namespace std;
using namespace cv;






typedef std::vector<Point2D> PointList;

int main(int argc, char* argv[])
{
  if (argc<2)
  {
    std::cout << "Usage: " << argv[0] << " image.pgm [magnitude_factor = 200]" << std::endl;
  }

  double mag_factor = 200.0;
  if (argc>2) mag_factor = atof(argv[2]);

  // initialize sampler
  ImageQuasisampler test();
  test.loadPGM("image.pgm");
  // generate points
  PointList points = test.getSamplingPoints();
  std::vector<double> x_ind;
  std::vector<double> y_ind;
  // print points
  for ( PointList::iterator it=points.begin(); it!=points.end(); it++ ){
    x_ind.push_back(it->x);
    y_ind.push_back(it->y);
  }
  Mat plot_result;
  Ptr<plot::Plot2d> plot = plot::Plot2d::create( y_ind, x_ind );
  plot->setNeedPlotLine(0);
  plot -> setShowGrid(0);
  plot->render(plot_result);

  namedWindow( "Display window", WINDOW_AUTOSIZE );
  imshow( "The plot rendered with default visualization options", plot_result );
  waitKey(0);
  destroyWindow("Display window");

  return 0;
}


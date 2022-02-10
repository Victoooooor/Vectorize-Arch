#include "sampler/imagesampler.h"

// #include "numpy/ndarrayobject.h"
// #include "opencv2/core/core.hpp"


namespace BN_Sample{

  using namespace boost::python;

  namespace np = boost::python::numpy;
  namespace py = boost::python;

typedef std::vector<Point2D> PointList;

ImageQuasisampler::ImageQuasisampler() {
  // Load the Matrix
  data = nullptr;
  mag = 1.0;
}

ImageQuasisampler::ImageQuasisampler(PyObject *inputObject, double mag) {
  // Load the Matrix
  if (!loadImg(inputObject, mag)) {
    this->data = nullptr;
    this->mag = 1.0;
    this->width = this->height = this->channels = 0;
    this->type = -1;
  }
}

bool ImageQuasisampler::loadImg(PyObject *inputObject, double mag) {
  cv::Mat returned = BN_Sample::fromNDArrayToMat(inputObject);
  if (returned.channels() >3 || returned.dims > 3){
    this->data = nullptr;
    this->mag = 1.0;
    this->width = this->height = this->channels = 0;
    this->type = -1;
    throw ChannelException();
    return false;
  }
  if (returned.type() != 16){
    std::cout<<"Require uint8"<<std::endl;
    this->data = nullptr;
    this->mag = 1.0;
    this->width = this->height = this->channels = 0;
    this->type = -1;
    throw ChannelException();
    return false;
  }
  this->data = returned.isContinuous()? returned.data: returned.clone().data;
  this->mag = mag;
  this->width = returned.cols;
  this->height = returned.rows;
  this->channels = returned.channels();
  this->type = returned.type();
  std::cout<<this->type<<std::endl;
  return true;
}

unsigned ImageQuasisampler::getImportanceAt(Point2D pt) {
  if(this->data == nullptr){
    throw "No Valid Data loaded";
    exit(-1);
  }
  unsigned sum = 0;
  for (int i=0; i< this->channels; i++){
    int index = ((int) (this->width * (pt.y)) + (int)(pt.x)) * this->channels + i;
    if (index > this->width * this->height * this->channels){
      std::cout<<"outside" <<std::endl;
    }
      
    sum += (this->data)[index];
  }
    
  sum = (unsigned) this->mag * sum;
  // std::cout <<"x"<<pt.x << "  y" <<pt.y <<"  sum" << sum <<std::endl;
  return sum;
}

cv::Mat ImageQuasisampler::debugTool(){
  
  cv::Mat passing = Mat::zeros((unsigned)this->width,(unsigned)this->height, CV_64F);
  for(int i = 0; i < (unsigned)this->width; i++){
    for(int j = 0; j < (unsigned)this->height; j++){
      for (int k = 0; k <this->channels; k++)
        passing.at<double>(i,j) += (this->data)[((int) (this->width * (this->height - j)) + (i)) * this->channels + k];
      passing.at<double>(i,j) /= 3;
    }
  }

  return passing;
}

cv::Mat ImageQuasisampler::getSampledPoints(){
  
  PointList points = this->getSamplingPoints();
  int num_pts = points.size();
  cv::Mat passing = Mat::zeros(num_pts, 2, CV_64F);
  for(int i = 0; i < passing.rows; i++){
        passing.at<double>(i,0)=points[i].x;
        passing.at<double>(i,1)=points[i].y;
  }

  return passing;
}

}
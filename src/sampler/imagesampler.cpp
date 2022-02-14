#include "sampler/imagesampler.h"
#include <cstring>
// #include "numpy/ndarrayobject.h"
 #include "opencv2/core/core.hpp"
#include "opencv2/opencv.hpp"

namespace BN_Sample{

  using namespace boost::python;
  using namespace std;
  namespace np = boost::python::numpy;
  namespace py = boost::python;

typedef std::vector<Point2D> PointList;

ImageQuasisampler::ImageQuasisampler() {
  // Load the Matrix
  this->data.clear();
  this->mag = 1.0;
}

ImageQuasisampler::ImageQuasisampler(PyObject *inputObject, double width, double height, double mag):Quasisampler(width, height) {
  // Load the Matrix
  if (!loadImg(inputObject, mag)) {
    this->data.clear();
    this->mag = 1.0;
    this->width = this->height = this->channels = 0;
    this->type = -1;
  }
}

bool ImageQuasisampler::loadImg(PyObject *inputObject, double mag) {
  cv::Mat returned = BN_Sample::fromNDArrayToMat(inputObject);
  if (returned.channels() >3 || returned.dims > 3){
    this->data.clear();
    this->mag = 1.0;
    this->width = this->height = this->channels = 0;
    this->type = -1;
    throw ChannelException();
    return false;
  }
  if (returned.type() != 16){
    std::cout<<"Require uint8"<<std::endl;
    this->data.clear();
    this->mag = 1.0;
    this->width = this->height = this->channels = 0;
    this->type = -1;
    throw ChannelException();
    return false;
  }

  this->mag = mag;
  this->width = returned.cols;
  this->height = returned.rows;
  this->channels = returned.channels();
  this->type = returned.type();
  int data_len =(int)(this->width * this->height * this->channels);
  std::cout<<"data_len: "<<data_len<<std::endl;
  this->data.clear();
  std::cout<<"data alocated"<<std::endl;
  int index = 0;
  for(int row = 0; row < returned.rows; ++row) {
    uchar* p = returned.ptr(row);
    for(int col = 0; col < returned.cols*returned.channels(); ++col) {
         this->data.push_back(*p);
//         std::cout<<this->data.back()<<" ";
         p++;  //points to each pixel value in turn assuming a CV_8UC1 greyscale image
    }


}

  std::cout<<this->type<<std::endl;
  return true;
}

  bool ImageQuasisampler::loadPGM(char* filename, double mag)
  {
    std::cout<<filename<<std::endl;
    int w,h = 0;
    if (!filename) { cerr << "Could not load PGM: no filename given." << endl; return false; }
    char buffer[80];
    ifstream infile(filename);
    if ( !infile.is_open() ) { cerr << "Could not open file: " << filename << endl; return false; }
    infile.getline(buffer,80);
    if ( strcmp(buffer,"P2")  )
    {  cerr << "PGM file header not recognized (P2 type only)" << endl; return false;  }
    do { infile.getline(buffer,80); } while ( buffer[0]=='#' );
    w = atoi(buffer);
    char *tmp = strchr(buffer,' '); tmp++; // skip whitespace
    h = atoi(tmp);
    do { infile.getline(buffer,80); } while ( buffer[0]=='#' );
    unsigned maxval;
    maxval = atoi(buffer);  // nb: not used.
    this->data.clear();
    unsigned temp = 0;
    for (unsigned i=0; i<w*h; i++) {
        infile >> temp;
        this->data.push_back(temp);
//        std::cout<<(int)data[i]<<" ";
    }
    infile.close();

    if (mag != 1.0)
        this->mag = mag;

    this->width = w; this->height = h; this->channels = 1;
    return true;
  }

unsigned ImageQuasisampler::getImportanceAt(Point2D pt) {
    int x = (int)pt.x;
    int y = (int)pt.y;
    int w = (int)( this->width);
    int h = (int)(this->height);

  if(this->data.empty()){
    throw "No Valid Data loaded";
    exit(-1);
  }
  unsigned sum = 0;
    for(int i = 0; i< this->channels; i++){
    int index = ((h-y)*w + x) * this->channels + i;
    if (index > (this->width * this->height * this->channels)){
        std::cerr<<"outside" <<std::endl;
        break;
    }

    sum += (this->data)[index];
    }

//  }
    
  sum = (unsigned) this->mag * sum;
  return sum;
}

cv::Mat ImageQuasisampler::debugTool(){
  
  cv::Mat passing = Mat::zeros((unsigned)this->width,(unsigned)this->height, CV_32S);
  for(int i = 0; i < (int)this->width; i++){
    for(int j = 0; j < (int)this->height; j++){

        passing.at<int>(i,j) +=this->getImportanceAt(Point2D((double)i, (double)j));
    }
  }

  return passing;
}

cv::Mat ImageQuasisampler::getSampledPoints(){
  
  PointList points = this->getSamplingPoints();

  int num_pts = points.size();
//  std::cout<<"numpts"<<num_pts<<std::endl;
  cv::Mat passing = Mat::zeros(num_pts, 2, CV_64F);
  for(int i = 0; i < passing.rows; i++){
        passing.at<double>(i,0)=points[i].x;
        passing.at<double>(i,1)=points[i].y;
  }

  return passing;
}

}
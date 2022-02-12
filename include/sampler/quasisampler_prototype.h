/*
 File: quasisampler_prototype.h
 Quasisampler prototype.

 This is a toy (non-optimized) implementation of the importance sampling
 technique proposed in the paper:
 "Fast Hierarchical Importance Sampling with Blue Noise Properties",
 by Victor Ostromoukhov, Charles Donohue and Pierre-Marc Jodoin,
 to be presented at SIGGRAPH 2004.

 
 Implementation by Charles Donohue,
 Based on Mathematica code by Victor Ostromoukhov.
 Universite de Montreal
 18.08.04

*/

#ifndef QUASISAMPLER_PROTOTYPE_H
#define QUASISAMPLER_PROTOTYPE_H

#include "opencv2/core/core.hpp"
#include <Python.h>
#include <cstddef>
#include <cstring>
#include <math.h>
#include <vector>
#include <iostream>
#include <fstream>

#define LUT_SIZE 21 // Number of Importance Index entries in the Lookup table.
#define NUM_STRUCT_INDEX_BITS 6 // Number of significant bits taken from F-Code.

#define GOLDEN_RATIO PHI // Phi is the Golden Ratio.
#define PHI     1.6180339887498948482045868343656 // ( 1 + sqrt(5) ) / 2
#define PHI2    2.6180339887498948482045868343656 // Phi squared
#define LOG_PHI 0.48121182505960347 // log(Phi)
#define SQRT5   2.2360679774997896964091736687313 // sqrt(5.0)

// Two-bit sequences.
#define B00 0
#define B10 1
#define B01 2



/// The six tile types.
enum TileType {
  TileTypeA,TileTypeB,TileTypeC,TileTypeD,TileTypeE,TileTypeF
};

/// Simple 2D point and vector type.
class Point2D
{
public:
  double x,y;

  Point2D(){};
  Point2D(const double x, const double y) { this->x=x; this->y=y; }
  Point2D(const double vect[2]) { x=vect[0]; y=vect[1]; }

  Point2D operator+(const Point2D& pt) const{ return Point2D(x+pt.x,y+pt.y); }
  Point2D operator-(const Point2D& pt) const{ return Point2D(x-pt.x,y-pt.y); }
  Point2D operator*(double factor) const{ return Point2D(x*factor,y*factor); }
  Point2D operator/(double factor) const{ return Point2D(x/factor,y/factor); }

  /// Returns the squared distance to the origin, or the squared length of a vector.
  double d2() const { return x*x+y*y; }
};

/// This is a base class that implements the Quasi-Sampler importance sampling
/// system, as presented in the paper :
/// "Fast Hierarchical Importance Sampling with Blue Noise Properties",
/// by Victor Ostromoukhov, Charles Donohue and Pierre-Marc Jodoin,
/// to be presented at SIGGRAPH 2004.
/// This is a pure-virtual class, and you must implement the "getImportanceAt()" function
/// in order to use the sampling system.
/// The mechanics of the system can be observed in the given source code.
class Quasisampler
{

protected:

  //
  // Static tables.
  //


  /// Fibonacci sequence (first 32 numbers).
  static const unsigned fiboTable[32]; // defined at end of file.

  /// Unit vectors rotated around origin, in \f$ \frac{\pi}{10} \f$ increments, 
  /// counter-clockwise. 0 = North.
  /// This table can be used to accelerate the trigonomic operations within the tile
  /// subdivision process, since all angles can only take these values.
  static const Point2D vvect[20]; // defined at end of file.

  /// Pre-calculated correction vectors lookup table.
  /// These are available in ASCII format on the web-site.
  static const double lut[LUT_SIZE][21][2]; // defined at end of file.

  //
  //  Static functions.
  //

  /// Fibonacci number at a given position.
  /// The value returned is \f$ F_i = F_{i-1} + F_{i-2}  \f$.
  static unsigned fibonacci(unsigned i);

  /// Returns the required level of subdivision for a given importance value.
  /// The value returned is \f$ \lceil{\log_{\phi^2}(importance)}\rceil \f$,
  /// where \f$ \phi=\frac{1 + {\sqrt{5}}}{2}\f$  is the Golden Ratio.
  static unsigned getReqSubdivisionLevel( unsigned importance );

  /// Returns the decimal value of an F-Code, over a given number of bits.
  /// The value returned is \f$ \sum_{j=2}^{m} b_{j} F_{j} \f$.
  static unsigned calcFCodeValue(unsigned bitsequence,unsigned nbits);


  /// Returns the Structural Index (i_s) for a given F-Code.
  static unsigned calcStructuralIndex(unsigned bitsequence);

  /// Returns the Importance Index (i_v) for a given importance value.
  /// The value returned is \f$ \lfloor n \cdot ({\log_{\phi^2} \sqrt{5} \cdot x}) ~ {\bf mod} ~ 1 \rfloor \f$.
  static unsigned calcImportanceIndex( unsigned importance );


  /// Fetches the appropriate vector from the lookup table.
  static Point2D calcDisplacementVector(unsigned importance, unsigned f_code, int dir);



  //
  // Inner classes.
  //


  /// Individual tile elements, which also serve as nodes for the tile subdivision tree.
  class TileNode
  {

    unsigned level; // Depth in the tree.
    int tileType; // Types A through F.
    int dir; // Tile orientation, 0=North, in Pi/10 increments, CCW.
    double scale; 
    Point2D p1,p2,p3; // Three points of the triangle. Counter-clockwise.

    /// The F-Code binary sequence.
    unsigned f_code; 
    
    // tiling tree structure
    TileNode* parent;
    unsigned parent_slot; // position in parent's list (needed for iterators)
    bool terminal; // true for leaf nodes
    std::vector<TileNode*> children;

  public:

    /// Builds a tile according to the given specifications.
    TileNode(  
      TileNode* parent = NULL, 
      int tileType = TileTypeF,
      Point2D refPt = Point2D(0,0),
      int dir = 15, // 15 = East.
      unsigned newbits = 0,
      int parent_slot = 0,
      double scale = 1.0);
    

    /// Helper constructor.
    /// Creates an initial tile that is certain to contain the ROI.
    /// The starting tile is of type F (arbitrary).
    TileNode( double roi_width,  double roi_height);
    
    ~TileNode();
    /// Splits a tile according to the given subdivision rules.
    /// Please refer to the code for further details.
    void refine();

    /// Prunes the subdivision tree at this node.
    void collapse();

    /// Returns the next node of the tree, in depth-first traversal.
    /// Returns NULL if it is at the last node.
    TileNode* nextNode();

    /// Returns the next closest leaf to a node.
    /// Returns NULL if it's the last leaf.
    TileNode* nextLeaf();

    // Public accessors

    Point2D getP1() const;
    Point2D getP2() const;
    Point2D getP3() const;
    Point2D getCenter() const;
    unsigned getFCode() const;
    bool isSamplingType() const;
    unsigned getLevel();
    bool isTerminal() const;
    TileNode* getParent();
    TileNode* getChild(unsigned i);

    /// Obtains the correction vector from the lookup table,
    /// then scales and adds it to the reference point.
    Point2D getDisplacedSamplingPoint(unsigned importance);

  }; // end of class TileNode.

  /// Leaf iterator for the tile subdivision tree.
  /// The traversal is made in a depth-first manner.
  /// Warning: This does not behave like STL style iterators.
  class TileLeafIterator
  {
    TileNode* shape;
  public:
    TileLeafIterator();
    TileLeafIterator(TileNode* s );

    TileNode* operator*();
    TileNode* operator->();

    void begin(TileNode* s);

    /// Subdivides the tile and moves to its 1st child.
    void refine();

    /// Prunes the subdivision tree.
    void collapse();

    /// Moves to the next node in the subdivision tree, in depth-first traversal.
    /// Returns false iff there is no such node.
    bool next();

    /// Checks if there is a next tile, in depth-first traversal.
    bool hasNext();
  };


  //
  // Instance members.
  //

  /// Root node of the tile subdivision tree.
  TileNode *root;
  
  /// Extents of the region of interest.
  double width, height;

  /// Protected constructor, which initializes the Region of Interest.
  Quasisampler(double width=0.0, double height=0.0);
  
  virtual ~Quasisampler() { if (root) delete root; }



  /// This is a helper function which constrains the incoming points
  /// to the region of interest.
  unsigned getImportanceAt_bounded(Point2D pt);

  /// Subdivides all tiles down a level, a given number of times.
  void subdivideAll(int times=1);

  /// Generates the hierarchical structure.
  void buildAdaptiveSubdivision( unsigned minSubdivisionLevel = 6 );

  /// Collect the resulting point set.
  void collectPoints(std::vector<Point2D> &pointlist,bool filterBounds = true );

public:

  /// This virtual function must be implemented in order to use the sampling system.
  /// It should return the value of the importance function at the given point.
  virtual unsigned getImportanceAt( Point2D pt ) = 0;

  /// Builds and collects the point set generated be the sampling system,
  /// using the previously defined importance function.
  std::vector<Point2D> getSamplingPoints();

}; 


#endif //QUASISAMPLER_PROTOTYPE_H


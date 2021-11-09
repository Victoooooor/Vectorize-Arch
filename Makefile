CXX=g++
CXXFLAGS= $(shell libpng-config --libs --ldflags)
BUILDDIR=build

# build the edge detector
$(BUILDDIR)/edge: src/edge/edge.cpp
	mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -o $@ $^

run_edge: $(BUILDDIR)/edge
	$< $(ARGS)

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)

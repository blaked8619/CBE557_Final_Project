gmsh tube.geo \
  -3 \                             # mesh the volume (so all boundary faces exist)
  -clmin 0.3 -clmax 0.3 \          # tighten the global element size
  -smooth 10 \                     # Laplacian‐smooth the node positions
  -o tube.stl -format stl          # write *all* boundary triangles to STL


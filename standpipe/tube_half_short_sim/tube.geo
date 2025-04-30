SetFactory("OpenCASCADE");
Mesh.SaveAll = 1;

// Create the outer cylinder (solid)
Cylinder(1) = {0, 0, 0, 0, 0, 25, 10};

// Create the inner cylinder (to be removed)
Cylinder(2) = {0, 0, 0, 0, 0, 25, 8};

// Subtract the inner cylinder from the outer one to create a tube
tube() = BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; };

// Optionally, assign a physical volume
Physical Volume("Tube") = {tube()};


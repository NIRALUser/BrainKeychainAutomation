scale(3)
difference() {
    union() {
        //cube([7.5, 2, 0.5]);
        cube([length, 2, 0.5]);
        translate([1.5, 0.4, 0.5])
            linear_extrude(0.6)
                text(input, size = 1.5);
    }
    translate([1, 1, 0.5])
        cylinder(h = 3, r = 0.6,center = true,$fn = 20);
}
$fn = 15;


union() {
	difference() {
		difference() {
			cylinder(center = false, d = 0.7500000000, h = 1.0000000000);
			translate(v = [0, 0, -0.3750000000]) {
				translate(v = [-0.0, -0.0, 1.0]) {
					rotate(a = -180.0, v = [1.0, 0.0, -0.0]) {
						rotate(a = [90.0000000000, 0.0000000000, 0.0000000000]) {
							cylinder(center = true, d = 0.2500000000, h = 1.5000000000);
						}
					}
				}
			}
		}
		union() {
			translate(v = [-0.2360000000, 0, 0]) {
				cylinder(center = false, d = 0.1250000000, h = 0.3750000000);
			}
			translate(v = [-0.2360000000, 0, 0]) {
				translate(v = [-0.0, -0.0, -0.1]) {
					cylinder(center = false, d = 0.1100000000, h = 0.1000000000);
				}
			}
		}
		union() {
			translate(v = [0.2360000000, 0, 0]) {
				cylinder(center = false, d = 0.1250000000, h = 0.3750000000);
			}
			translate(v = [0.2360000000, 0, 0]) {
				translate(v = [-0.0, -0.0, -0.1]) {
					cylinder(center = false, d = 0.1100000000, h = 0.1000000000);
				}
			}
		}
	}
	translate(v = [0, 0, -0.3750000000]) {
		translate(v = [-0.0, -0.0, 1.0]) {
			rotate(a = -180.0, v = [1.0, 0.0, -0.0]) {
				rotate(a = [90.0000000000, 0.0000000000, 0.0000000000]) {
					cylinder(center = true, d = 0.2500000000, h = 1.5000000000);
				}
			}
		}
	}
	union() {
		translate(v = [-0.2360000000, 0, 0]) {
			cylinder(center = false, d = 0.1250000000, h = 0.3750000000);
		}
		translate(v = [-0.2360000000, 0, 0]) {
			translate(v = [-0.0, -0.0, -0.1]) {
				cylinder(center = false, d = 0.1100000000, h = 0.1000000000);
			}
		}
	}
	union() {
		translate(v = [0.2360000000, 0, 0]) {
			cylinder(center = false, d = 0.1250000000, h = 0.3750000000);
		}
		translate(v = [0.2360000000, 0, 0]) {
			translate(v = [-0.0, -0.0, -0.1]) {
				cylinder(center = false, d = 0.1100000000, h = 0.1000000000);
			}
		}
	}
}
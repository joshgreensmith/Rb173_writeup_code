import com.hamoid.*;
import java.util.Date;
import java.sql.Timestamp;

import shapes3d.*;
import shapes3d.contour.*;
import shapes3d.org.apache.commons.math.*;
import shapes3d.org.apache.commons.math.geometry.*;
import shapes3d.path.*;
import shapes3d.utils.*;

// Whether to export video to a local file
boolean export_video = false;
VideoExport videoExport;

// Video export path
String filename = "../rb173/shell_trap_output/pos.txt";

int num_steps;
PVector[][] positions;

// Atom position scaling for output
int scaling = 30000;
int scaling_increment = 1000;

// Whether to draw the resonant spheroid with its calculated size
boolean draw_shell_ellipsoid = true;
float shell_radius = 0.003457310243726826;

int num_atoms = 1000;
int draw_step = 0;
int axes_size = 450;

// Defaults
// float x_angle = 1.645;
// float z_angle = -1.405;

// Bottom view
float x_angle = 2.065;
float z_angle = -0.505;

int rotate_x = 0;
int rotate_z = 0;
float angle_increment = 0.015;

void setup() {
  size(800, 800, P3D);
  if (export_video) {
    Timestamp timestamp = new Timestamp(System.currentTimeMillis());
    videoExport = new VideoExport(this, "video_out/" + timestamp.toString() + ".mov");
    videoExport.setFrameRate(30);
    videoExport.startMovie();
  }

  // Import position output file
  String[] lines = loadStrings(filename);

  // Calculate number of steps in the sim code
  for (int i = 0; i < lines.length; i++) {
    if (lines[i].startsWith("step")) {
      num_steps += 1;
    }
  }

  // Initialise 2d position array with correct dimensions
  positions = new PVector[num_steps][num_atoms];

  // Populate positions array
  int step = -1;
  int atom = 0;
  for (int i = 0; i < lines.length; i++) {
    if (lines[i].startsWith("step")) {
      step += 1;
      atom = 0;
    } else {
      float x = Float.parseFloat(lines[i].split("\\(")[1].split(",")[0]);
      float y = Float.parseFloat(lines[i].split("\\(")[1].split(",")[1]);
      float z = Float.parseFloat(lines[i].split("\\(")[1].split(",")[2].split("\\)")[0]);
      positions[step][atom] = new PVector(x, y, z);
      atom += 1;
    }
  }
  
  shape = new Ellipsoid(
    shell_radius * scaling * 2, shell_radius * scaling * 2, shell_radius * scaling, // 3 orthogonal radii
    24,           // number of segments (in XZ plane)
    12            // number of slices along Y axis
   );
  shape.fill(#e6e6e6);
  shape.stroke(#cfcfcf);
}

void draw() {
  draw_step += 1;

  background(255);
  translate(width/2, height/2);

  textSize(10);
  stroke(0);
  fill(0);
  strokeWeight(4);
  text(draw_step % num_steps, -270, -260, 200);
  
  rotateX(x_angle);
  rotateZ(z_angle);

  // Rotate angle if key pressed
  if (rotate_x != 0) {x_angle += rotate_x * angle_increment;} 
  if (rotate_z != 0) {z_angle += rotate_z * angle_increment;} 
  
  // Draw atoms 
  stroke(0);
  strokeWeight(3);
  for (int atom = 0; atom < num_atoms; atom ++) {
    point(
      positions[draw_step % num_steps][atom].x * scaling, 
      positions[draw_step % num_steps][atom].y * scaling, 
      positions[draw_step % num_steps][atom].z * scaling
      );
  }
  
  drawAxes();
  if(draw_shell_ellipsoid) {shape.draw(getGraphics());}
  
  // If exporting video, save frame and exit after one loop
  if (export_video) {
    videoExport.saveFrame();
    if (draw_step == num_steps) {
      videoExport.endMovie();
      exit();
    }
  }
}

void drawAxes() {
  push();
  translate(-axes_size/2, -axes_size/2, -axes_size/2);
  strokeWeight(2);
  stroke(0, 0, 192);
  line(0, 0, 0, axes_size, 0, 0);
  line(0, 0, 0, 0, axes_size, 0);
  line(0, 0, 0, 0, 0, axes_size);

  // Draw grid lines
  stroke(200);
  for (int i=30; i<axes_size+1; i+=30) {
    line(i, 0, 0, i, axes_size, 0);
    line(0, i, 0, axes_size, i, 0);
    line(i, 0, 0, i, 0, axes_size);
    line(0, 0, i, axes_size, 0, i);
  }
  
  pop();
}

void keyPressed() {
  // Left arrow
  if (keyCode == 37) {
    rotate_z = -1;
  }
  // Up arrow
  if (keyCode == 38) {
    rotate_x = -1;
  }
  // Right arrow
  if (keyCode == 39) {
    rotate_z = +1;
  }
  // Down arrow
  if (keyCode == 40) {
    rotate_x = +1;
  }
  // Tab key to reset
  if (keyCode == 9) {
    draw_step = 0;
  }
}

void keyReleased() {
  // Left arrow
  if (keyCode == 37) {
    rotate_z = 0;
  }
  // Up arrow
  if (keyCode == 38) {
    rotate_x = 0;
  }
  // Right arrow
  if (keyCode == 39) {
    rotate_z = 0;
  }
  // Down arrow
  if (keyCode == 40) {
    rotate_x = 0;
  }
  println(x_angle, z_angle, '\n');
}

void mouseWheel(MouseEvent event) {
  float e = event.getCount();
  // Zoom in if scrolling forward
  if (e < 0) {
    scaling += scaling_increment;
  } else {
    scaling_increment -= scaling_increment;
  }
  println(scaling);
}

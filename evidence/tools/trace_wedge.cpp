#include "student.h"
#include <cstdio>
int main() { Scene scene=tiny_scene(); for(int x: {290,300,315}) { std::printf("PIXEL %d,380\n",x); vec3 c=cast_ray(camera_ray(x,380,800,600,PI/3),scene,0); std::printf("RESULT %g %g %g\n",c.x,c.y,c.z); } }

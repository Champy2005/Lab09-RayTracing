// Estimate how often a floor cosine sample reaches the lamp, with and without scene occlusion.
#include "student.h"
#include "core/cornell.h"
#include <cstdio>

int main() {
  PtScene scene = cornell_box();
  Rng random(2468, 9);
  const vec3 origin{278, EPS, 278};
  int geometric = 0, visible = 0;
  const int samples = 200000;
  for(int i = 0; i < samples; ++i) {
    const float u1 = random.next(), u2 = random.next();
    const vec3 direction = cosine_sample_hemisphere(vec3{0, 1, 0}, u1, u2);
    const float t = (554 - origin.y) / direction.y;
    const vec3 point = origin + direction * t;
    if(point.x >= 213 && point.x <= 343 && point.z >= 227 && point.z <= 332) {
      ++geometric;
      Hit hit;
      if(pt_intersect(Ray{origin, direction}, scene, 1e30f, hit) && pt_material(scene, hit).emission.x > 0) ++visible;
    }
  }
  std::printf("Cosine samples from (278, EPS, 278), seed 2468 stream 9: %d\n", samples);
  std::printf("Directions within lamp rectangle, ignoring occlusion: %d (%.6f%%)\n", geometric, 100.0 * geometric / samples);
  std::printf("Directions that hit lamp before other geometry: %d (%.6f%%)\n", visible, 100.0 * visible / samples);
}

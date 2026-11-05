// Independent geometric edge cases, sampling checks, and BVH/brute-force agreement.
#include "student.h"
#include "core/bvh.h"
#include "core/cornell.h"
#include "core/mesh.h"
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <limits>

static int checks = 0;
static void require(bool condition, const char* message) {
  ++checks;
  if(!condition) {
    std::fprintf(stderr, "FAIL: %s\n", message);
    std::exit(1);
  }
}
static bool close(float a, float b, float tolerance = 1e-4f) {
  return std::fabs(a - b) <= tolerance;
}

int main() {
  float t = 0, u = 0, v = 0;
  Sphere sphere{{0, 0, -5}, 1, Material{}};
  require(ray_sphere(Ray{{0, 0, 0}, {0, 0, -1}}, sphere, t) && close(t, 4), "sphere entry");
  require(ray_sphere(Ray{{0, 0, -5}, {0, 0, -1}}, sphere, t) && close(t, 1), "sphere inside exit");
  require(ray_sphere(Ray{{1, 0, 0}, {0, 0, -1}}, sphere, t) && close(t, 5), "sphere tangent");
  require(ray_sphere(Ray{{0, 0, 0}, {0, 0, -2}}, sphere, t) && close(t, 2), "non-unit sphere ray");
  require(!ray_sphere(Ray{{0, 0, 0}, {0, 0, 1}}, sphere, t), "sphere behind ray");
  Ray camera = camera_ray(0, 0, 1, 1, PI / 3);
  require(close(length(camera.o), 0) && close(camera.d.z, -1), "pinhole origin and centred ray");
  require(camera_ray(0, 0, 800, 600, PI / 3).d.y > 0, "top row points up");
  vec3 reflected = reflect(normalize(vec3{1, -1, 0}), vec3{0, 1, 0});
  require(reflected.x > 0 && reflected.y > 0 && close(length(reflected), 1), "reflection normal component");
  vec3 transmitted;
  require(refract(vec3{0, 0, -1}, vec3{0, 0, 1}, 1.5f, transmitted) && close(transmitted.z, -1), "normal-incidence entry");
  require(refract(vec3{0, 0, 1}, vec3{0, 0, 1}, 1.5f, transmitted) && close(transmitted.z, 1), "normal-incidence exit");
  require(!refract(vec3{0.9f, 0, std::sqrt(0.19f)}, vec3{0, 0, 1}, 1.5f, transmitted), "total internal reflection");
  const vec3 a{-1, -1, -5}, b{1, -1, -5}, c{0, 1, -5};
  const Ray forward{{0, 0, 0}, {0, 0, -1}};
  require(ray_triangle(forward, a, b, c, t, u, v) && close(t, 5) && close(u, 0.25f) && close(v, 0.5f), "triangle barycentrics");
  require(ray_triangle(Ray{{0, 0, -10}, {0, 0, 1}}, a, b, c, t, u, v), "two-sided triangle exit");
  require(!ray_triangle(Ray{{5, 0, 0}, {0, 0, -1}}, a, b, c, t, u, v), "triangle outside");
  require(!ray_triangle(Ray{{0, 0, 0}, {1, 0, 0}}, a, b, c, t, u, v), "triangle parallel");
  require(!ray_triangle(forward, a, a, a, t, u, v), "degenerate triangle");
  Mesh one;
  one.positions = {a, b, c}; one.tris = {{0, 1, 2}};
  Hit hit;
  require(!intersect_mesh(forward, one, 5, hit), "strict triangle t_max");
  require(intersect_mesh(forward, one, 6, hit) && close(hit.n.z, 1), "flat normal");
  one.normals = {{0, 0, 1}, {0, 1, 0}, {1, 0, 0}};
  require(intersect_mesh(forward, one, 6, hit) && length(hit.n - normalize(vec3{0.5f, 0.25f, 0.25f})) < 1e-4f, "smooth normal interpolation");
  const float inf = std::numeric_limits<float>::infinity();
  const AABB box{{-1, -1, -6}, {1, 1, -4}};
  require(ray_aabb(forward, vec3{inf, inf, -1}, box, 10, t) && close(t, 4), "parallel inside slabs");
  require(ray_aabb(Ray{{1, 0, 0}, {0, 0, -1}}, vec3{inf, inf, -1}, box, 10, t), "parallel ray on box boundary without NaN");
  require(!ray_aabb(Ray{{2, 0, 0}, {0, 0, -1}}, vec3{inf, inf, -1}, box, 10, t), "parallel ray outside slab");
  require(!ray_aabb(forward, vec3{inf, inf, -1}, box, 3, t), "box beyond t_max");
  require(ray_aabb(Ray{{0, 0, -5}, {0, 0, -1}}, vec3{inf, inf, -1}, box, 10, t) && t < 0, "origin inside box");
  require(!ray_aabb(Ray{{0, 0, 0}, {0, 0, 1}}, vec3{inf, inf, 1}, box, 10, t), "box behind ray");
  Mesh knot = make_torus_knot(64, 8);
  place(knot, 7, vec3{0, 0, -10});
  double orientation = 0;
  for(const auto& triangle : knot.tris) {
    vec3 face = normalize(cross(knot.positions[size_t(triangle[1])] - knot.positions[size_t(triangle[0])],
                                knot.positions[size_t(triangle[2])] - knot.positions[size_t(triangle[0])]));
    orientation += dot(face, knot.normals[size_t(triangle[0])]);
  }
  std::printf("Mean face-normal dot outward vertex normal: %.6f\n", orientation / double(knot.tris.size()));
  for(Split split : {Split::median, Split::sah}) {
    build_bvh(knot, split);
    Rng random(123, 7);
    for(int i = 0; i < 6000; ++i) {
      const vec3 origin{12 * random.next() - 6, 12 * random.next() - 6, 6 * random.next() - 13};
      const vec3 direction = normalize(vec3{2 * random.next() - 1, 2 * random.next() - 1, 2 * random.next() - 1});
      const Ray ray{origin, direction};
      const float limit = (i % 3 == 0) ? 2.0f : 1e30f;
      Hit brute, accelerated;
      const bool expected = intersect_mesh(ray, knot, limit, brute);
      const bool actual = intersect_bvh(ray, knot, limit, accelerated);
      require(expected == actual, "BVH/brute hit agreement");
      if(expected) {
        require(close(brute.t, accelerated.t, 2e-4f), "BVH/brute nearest distance");
        require(length(brute.n - accelerated.n) < 2e-3f, "BVH/brute shading normal");
      }
    }
  }
  Rng random(1234, 8);
  double mean_cosine = 0, surviving_weight = 0;
  const int draws = 100000;
  for(int i = 0; i < draws; ++i) {
    const float u1 = random.next(), u2 = random.next();
    const vec3 sample = cosine_sample_hemisphere(vec3{0, 1, 0}, u1, u2);
    require(close(length(sample), 1) && sample.y >= 0, "hemisphere support and unit length");
    mean_cosine += sample.y;
    vec3 throughput{0.2f, 0.2f, 0.2f};
    if(russian_roulette(throughput, 3, random)) surviving_weight += throughput.x;
  }
  require(std::fabs(mean_cosine / draws - 2.0 / 3.0) < 0.004, "cosine PDF has expected cosine 2/3");
  require(std::fabs(surviving_weight / draws - 0.2) < 0.004, "roulette preserves expected throughput");
  vec3 early{0.2f, 0.2f, 0.2f};
  const auto state = random.state;
  require(russian_roulette(early, 2, random) && random.state == state && close(early.x, 0.2f), "no early roulette or RNG draw");
  const PtScene cornell = cornell_box();
  Hit floor;
  floor.p = {278, 0, 278}; floor.n = {0, 1, 0}; floor.tri = 4;
  require(luminance(sample_light(floor, cornell, random)) > 0, "lamp sample reaches visible floor without self-shadow");
  floor.n = {0, -1, 0};
  require(close(luminance(sample_light(floor, cornell, random)), 0), "back-facing receiver gets no lamp contribution");
  PtOptions options;
  const vec3 centre = cornell.light.corner + (cornell.light.e1 + cornell.light.e2) * 0.5f;
  require(close(luminance(path_trace(Ray{centre + vec3{0, -0.1f, 0}, {0, 1, 0}}, cornell, random, options)), 15), "camera sees lamp front");
  require(close(luminance(path_trace(Ray{centre + vec3{0, 0.1f, 0}, {0, -1, 0}}, cornell, random, options)), 0), "lamp back remains dark");
  std::printf("PASS: %d checks, 12000 BVH/brute rays, 100000 sampling/roulette trials.\n", checks);
}

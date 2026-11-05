// Repeat the supplied sweep's primary-ray scene at 800 x 600 without editing framework source.
#include "student.h"
#include "core/bvh.h"
#include "core/cli.h"
#include "core/mesh.h"
#include "core/parallel.h"
#include <cstdio>

int main() {
  const int width = 800, height = 600, threads = thread_count(0);
  Scene scene;
  scene.meshes.push_back(make_torus_knot(256, 32));
  place(scene.meshes[0], 7, vec3{0, 0, -10});
  std::printf("Primary rays only, knot alone, 16384 triangles, %d x %d, %d threads\n", width, height, threads);
  for(int method = 0; method < 3; ++method) {
    const char* name[] = {"brute force", "bvh median", "bvh sah"};
    double build_ms = 0;
    if(method > 0) build_ms = build_bvh(scene.meshes[0], method == 1 ? Split::median : Split::sah).ms;
    scene.use_bvh = method > 0;
    for(int repeat = 1; repeat <= 3; ++repeat) {
      stats::reset();
      Timer timer;
      parallel_rows(height, threads, [&](int y) {
        for(int x = 0; x < width; ++x) {
          Hit hit;
          scene_intersect(camera_ray(x, y, width, height, PI / 3), scene, hit);
        }
      });
      const double ms = timer.ms();
      const auto counts = stats::totals();
      std::printf("%s repeat %d: build %.1f ms, render %.1f ms, tests/ray %.3f, nodes/ray %.3f\n",
                  name[method], repeat, build_ms, ms, double(counts.triangle_tests) / counts.rays,
                  double(counts.node_visits) / counts.rays);
    }
  }
}

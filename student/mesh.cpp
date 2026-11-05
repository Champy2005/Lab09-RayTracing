#include "student.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <limits>

#include "core/bvh.h"

namespace {
void store_hit(const Mesh& m, int triangle, float t, float u, float v, Hit& hit) {
  const auto& indices = m.tris[size_t(triangle)];
  hit.t = t;
  hit.tri = triangle;
  if(!m.normals.empty()) {
    hit.n = normalize(m.normals[size_t(indices[0])] * (1.0f - u - v)
                    + m.normals[size_t(indices[1])] * u
                    + m.normals[size_t(indices[2])] * v);
  } else {
    const vec3 e1 = m.positions[size_t(indices[1])] - m.positions[size_t(indices[0])];
    const vec3 e2 = m.positions[size_t(indices[2])] - m.positions[size_t(indices[0])];
    hit.n = normalize(cross(e1, e2));
  }
}
}

// TASK 2a, Equation 6: solve for ray distance and barycentric coordinates with Moller-Trumbore.
// Moller-Trumbore solves the ray/triangle system for distance t and the
// barycentric coordinates u and v. Accept both faces, but reject a nearly
// zero determinant, points outside the triangle, and distances at or below EPS.
bool ray_triangle(const Ray& r, const vec3& v0, const vec3& v1, const vec3& v2,
                  float& t, float& u, float& v) {
  const vec3 e1 = v1 - v0;
  const vec3 e2 = v2 - v0;
  const vec3 h = cross(r.d, e2);
  const float determinant = dot(e1, h);
  if(std::fabs(determinant) < 1e-8f) {
    return false;
  }
  const float inverse = 1.0f / determinant;
  const vec3 s = r.o - v0;
  const float candidate_u = dot(s, h) * inverse;
  if(candidate_u < 0.0f || candidate_u > 1.0f) {
    return false;
  }
  const vec3 q = cross(s, e1);
  const float candidate_v = dot(r.d, q) * inverse;
  if(candidate_v < 0.0f || candidate_u + candidate_v > 1.0f) {
    return false;
  }
  const float candidate_t = dot(e2, q) * inverse;
  if(candidate_t <= EPS) {
    return false;
  }
  t = candidate_t;
  u = candidate_u;
  v = candidate_v;
  return true;
}

// TASK 2b: brute-force closest-hit search, used by the Cornell box as well as Part II.
// Test every triangle and retain only hits closer than the current nearest.
// Count every attempted triangle test, including misses. The shared helper
// stores the original triangle ID and a normalized smooth or face normal.
bool intersect_mesh(const Ray& r, const Mesh& m, float t_max, Hit& hit) {
  bool found = false;
  float nearest = t_max;
  for(size_t triangle = 0; triangle < m.tris.size(); ++triangle) {
    const auto& indices = m.tris[triangle];
    float t = 0, u = 0, v = 0;
    count_triangle_test();
    if(ray_triangle(r, m.positions[size_t(indices[0])], m.positions[size_t(indices[1])],
                    m.positions[size_t(indices[2])], t, u, v) && t < nearest) {
      nearest = t;
      store_hit(m, int(triangle), t, u, v, hit);
      found = true;
    }
  }
  return found;
}

// TASK 2c, Equation 7: intersect the ray with the x, y, and z box slabs.
// Intersect the ray's distance intervals through the three axis-aligned slabs.
// The common interval must extend forward and begin no farther than t_max.
// Handle parallel axes explicitly: 0 * infinity would otherwise produce NaN.
bool ray_aabb(const Ray& r, const vec3& inv_d, const AABB& box, float t_max, float& t_entry) {
  float entry = -std::numeric_limits<float>::infinity();
  float exit = t_max;
  for(int axis = 0; axis < 3; ++axis) {
    if(r.d[axis] == 0.0f) {
      if(r.o[axis] < box.lo[axis] || r.o[axis] > box.hi[axis]) {
        return false;
      }
      continue;
    }
    float near_t = (box.lo[axis] - r.o[axis]) * inv_d[axis];
    float far_t = (box.hi[axis] - r.o[axis]) * inv_d[axis];
    if(near_t > far_t) {
      std::swap(near_t, far_t);
    }
    entry = std::max(entry, near_t);
    exit = std::min(exit, far_t);
    if(entry > exit) {
      return false;
    }
  }
  t_entry = entry;
  return exit > 0.0f && entry <= t_max;
}

// TASK 2d: visit nearer BVH children first, pruning boxes beyond the current closest triangle.
// Traverse the provided BVH with a depth-first stack. Prune boxes using the
// closest distance found so far, then test triangles only in reached leaves.
// Push the farther child first so the nearer child is processed next.
bool intersect_bvh(const Ray& r, const Mesh& m, float t_max, Hit& hit) {
  if(m.bvh.nodes.empty()) {
    return false;
  }
  const vec3 inv_d{1.0f / r.d.x, 1.0f / r.d.y, 1.0f / r.d.z};

  // One deferred sibling per tree level bounds the stack size; the supplied
  // builder caps tree depth at BVH_MAX_DEPTH.
  std::array<int, BVH_MAX_DEPTH + 2> stack{};
  int pending = 0;
  stack[size_t(pending++)] = 0;
  bool found = false;
  float nearest = t_max;
  while(pending > 0) {
    const int index = stack[size_t(--pending)];
    count_node_visit();
    const BVHNode& node = m.bvh.nodes[size_t(index)];
    float entry = 0;
    if(!ray_aabb(r, inv_d, node.box, nearest, entry)) {
      continue;
    }
    if(node.count > 0) {
      for(int i = node.first; i < node.first + node.count; ++i) {
        const int triangle = m.bvh.order[size_t(i)];
        const auto& indices = m.tris[size_t(triangle)];
        float t = 0, u = 0, v = 0;
        count_triangle_test();
        if(ray_triangle(r, m.positions[size_t(indices[0])], m.positions[size_t(indices[1])],
                        m.positions[size_t(indices[2])], t, u, v) && t < nearest) {
          nearest = t;
          store_hit(m, triangle, t, u, v, hit);
          found = true;
        }
      }
      continue;
    }

    // The builder places the left child immediately after its parent and stores
    // the right child's index explicitly. Compare entry distances to order them.
    int left = index + 1;
    int right = node.right;
    float left_entry = 0, right_entry = 0;
    const bool hit_left = ray_aabb(r, inv_d, m.bvh.nodes[size_t(left)].box, nearest, left_entry);
    const bool hit_right = ray_aabb(r, inv_d, m.bvh.nodes[size_t(right)].box, nearest, right_entry);
    if(hit_left && hit_right) {
      if(left_entry > right_entry) {
        std::swap(left, right);
      }
      stack[size_t(pending++)] = right;
      stack[size_t(pending++)] = left;
    } else if(hit_left) {
      stack[size_t(pending++)] = left;
    } else if(hit_right) {
      stack[size_t(pending++)] = right;
    }
  }
  return found;
}

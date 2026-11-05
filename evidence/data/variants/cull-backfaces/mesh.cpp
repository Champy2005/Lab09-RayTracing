#include "student.h" // Import mesh, hit, ray, vector, and instrumentation declarations.

#include <algorithm> // Provide min, max, and swap for interval and traversal ordering.
#include <array> // Provide a fixed-size traversal stack without allocating for every ray.
#include <cmath> // Provide fabs for the two-sided determinant test.
#include <limits> // Provide infinity for unbounded slab intervals.

#include "core/bvh.h" // Read the provided builder's maximum depth to size the stack safely.

namespace { // Keep the shared hit-writing helper private to this translation unit.
void store_hit(const Mesh& m, int triangle, float t, float u, float v, Hit& hit) { // Use identical hit data for brute force and BVH.
  const auto& indices = m.tris[size_t(triangle)]; // Look up the triangle's three vertex indices.
  hit.t = t; // Save the closest accepted distance.
  hit.tri = triangle; // Preserve the original triangle ID, also used for path-tracer materials.
  if(!m.normals.empty()) { // Interpolate smooth normals when the mesh supplies them.
    hit.n = normalize(m.normals[size_t(indices[0])] * (1.0f - u - v) // Weight the first normal by its barycentric coordinate.
                    + m.normals[size_t(indices[1])] * u // Weight the second normal by u.
                    + m.normals[size_t(indices[2])] * v); // Weight the third by v, then restore unit length.
  } else { // Without vertex normals, each triangle is a flat surface.
    const vec3 e1 = m.positions[size_t(indices[1])] - m.positions[size_t(indices[0])]; // First edge from vertex zero.
    const vec3 e2 = m.positions[size_t(indices[2])] - m.positions[size_t(indices[0])]; // Second edge from vertex zero.
    hit.n = normalize(cross(e1, e2)); // The winding determines the geometric face normal.
  } // End normal selection; scene_intersect or pt_intersect supplies hit.p later.
} // End store_hit.
} // End private helper namespace.

// TASK 2a, Equation 6: solve for ray distance and barycentric coordinates with Moller-Trumbore.
bool ray_triangle(const Ray& r, const vec3& v0, const vec3& v1, const vec3& v2, // Read the ray and three triangle vertices.
                  float& t, float& u, float& v) { // Output parameters are committed only after all hit checks pass.
  const vec3 e1 = v1 - v0; // First triangle edge.
  const vec3 e2 = v2 - v0; // Second triangle edge.
  const vec3 h = cross(r.d, e2); // Cross product used in Cramer's rule.
  const float determinant = dot(e1, h); // Its sign records the side from which the ray approaches.
  if(determinant < 1e-8f) { // Accept both windings; reject parallel rays and degenerate triangles.
    return false; // Dividing by a nearly zero determinant would be unstable.
  } // End determinant check.
  const float inverse = 1.0f / determinant; // Reuse one division for t, u, and v.
  const vec3 s = r.o - v0; // Ray-origin displacement from triangle vertex zero.
  const float candidate_u = dot(s, h) * inverse; // Barycentric weight of vertex one.
  if(candidate_u < 0.0f || candidate_u > 1.0f) { // This coordinate must lie on the triangle's unit interval.
    return false; // The ray crosses the plane outside the first pair of edges.
  } // End u check.
  const vec3 q = cross(s, e1); // Second cross product needed by Cramer's rule.
  const float candidate_v = dot(r.d, q) * inverse; // Barycentric weight of vertex two.
  if(candidate_v < 0.0f || candidate_u + candidate_v > 1.0f) { // The remaining weight 1-u-v must also be nonnegative.
    return false; // The crossing lies outside another triangle edge.
  } // End v check.
  const float candidate_t = dot(e2, q) * inverse; // Distance parameter along the ray to the triangle plane.
  if(candidate_t <= EPS) { // Reject intersections behind or too close to the origin.
    return false; // Avoid immediately hitting the surface from which a new ray starts.
  } // End forward-distance check.
  t = candidate_t; // Commit the valid ray distance.
  u = candidate_u; // Return the already-computed interpolation coordinate.
  v = candidate_v; // Return the second interpolation coordinate at no extra intersection cost.
  return true; // All three barycentric weights and the distance are valid.
} // End ray_triangle.

// TASK 2b: brute-force closest-hit search, used by the Cornell box as well as Part II.
bool intersect_mesh(const Ray& r, const Mesh& m, float t_max, Hit& hit) { // Accept hits strictly closer than t_max.
  bool found = false; // Start with no accepted triangle.
  float nearest = t_max; // Each hit tightens the distance limit for later candidates.
  for(size_t triangle = 0; triangle < m.tris.size(); ++triangle) { // Test every triangle, including ones behind an earlier hit.
    const auto& indices = m.tris[triangle]; // Retrieve the three indices into the position array.
    float t = 0, u = 0, v = 0; // Reserve the candidate distance and barycentric coordinates.
    count_triangle_test(); // Count exactly one test for this triangle, even on a miss.
    if(ray_triangle(r, m.positions[size_t(indices[0])], m.positions[size_t(indices[1])], // Test the first two vertices...
                    m.positions[size_t(indices[2])], t, u, v) && t < nearest) { // ...and third, keeping only a closer intersection.
      nearest = t; // Tighten the closest-hit bound.
      store_hit(m, int(triangle), t, u, v, hit); // Save its triangle ID and smooth or flat unit normal.
      found = true; // Remember that hit now contains a valid result.
    } // End candidate acceptance.
  } // End all-triangle loop.
  return found; // False leaves the caller's hit unused.
} // End intersect_mesh.

// TASK 2c, Equation 7: intersect the ray with the x, y, and z box slabs.
bool ray_aabb(const Ray& r, const vec3& inv_d, const AABB& box, float t_max, float& t_entry) { // inv_d caches 1/d.
  float entry = -std::numeric_limits<float>::infinity(); // Allow the ray origin to be inside the box.
  float exit = t_max; // Clip the box interval to the closest triangle or caller's limit.
  for(int axis = 0; axis < 3; ++axis) { // Intersect one interval for each coordinate axis.
    if(r.d[axis] == 0.0f) { // A parallel ray needs special handling to avoid 0 times infinity producing NaN.
      if(r.o[axis] < box.lo[axis] || r.o[axis] > box.hi[axis]) { // A parallel origin outside the slab never enters it.
        return false; // The entire box is missed.
      } // End outside-parallel-slab check.
      continue; // An origin inside a parallel slab adds no distance restriction.
    } // End parallel-axis handling.
    float near_t = (box.lo[axis] - r.o[axis]) * inv_d[axis]; // Distance to this axis's first plane.
    float far_t = (box.hi[axis] - r.o[axis]) * inv_d[axis]; // Distance to its opposite plane.
    if(near_t > far_t) { // Negative directions encounter the high plane first.
      std::swap(near_t, far_t); // Put this slab's distances into near/far order.
    } // End interval ordering.
    entry = std::max(entry, near_t); // We enter the box only after entering every slab.
    exit = std::min(exit, far_t); // We leave as soon as any slab is exited.
    if(entry > exit) { // Disjoint intervals cannot describe a point inside the box.
      return false; // Reject this box before examining more axes.
    } // End interval-overlap check.
  } // End slab loop.
  t_entry = entry; // Return the geometric entry distance, possibly negative for an interior origin.
  return exit > 0.0f && entry <= t_max; // The overlap must extend forward and begin within the distance limit.
} // End ray_aabb.

// TASK 2d: visit nearer BVH children first, pruning boxes beyond the current closest triangle.
bool intersect_bvh(const Ray& r, const Mesh& m, float t_max, Hit& hit) { // Traverse the tree built by core/bvh.cpp.
  if(m.bvh.nodes.empty()) { // An empty tree contains no triangles to intersect.
    return false; // Avoid reading a nonexistent root.
  } // End empty-tree check.
  const vec3 inv_d{1.0f / r.d.x, 1.0f / r.d.y, 1.0f / r.d.z}; // Reuse reciprocals for every box; ray_aabb handles zero directions.
  std::array<int, BVH_MAX_DEPTH + 2> stack{}; // A depth-first binary traversal needs at most one deferred sibling per level.
  int pending = 0; // Track the next free stack position.
  stack[size_t(pending++)] = 0; // Begin with the root node.
  bool found = false; // No closest triangle has been accepted yet.
  float nearest = t_max; // Initially use the caller's distance limit.
  while(pending > 0) { // Continue until every potentially useful node has been processed.
    const int index = stack[size_t(--pending)]; // Pop the most recently scheduled node.
    count_node_visit(); // Count each popped node once, including one subsequently pruned.
    const BVHNode& node = m.bvh.nodes[size_t(index)]; // Read this node's box and leaf/child metadata.
    float entry = 0; // Receive this box's entry distance.
    if(!ray_aabb(r, inv_d, node.box, nearest, entry)) { // Retest with the latest, possibly shorter, nearest distance.
      continue; // A miss or a farther box cannot improve the hit.
    } // End node pruning.
    if(node.count > 0) { // Positive count identifies a leaf containing an ordered triangle range.
      for(int i = node.first; i < node.first + node.count; ++i) { // Examine just this leaf's triangles.
        const int triangle = m.bvh.order[size_t(i)]; // Convert the builder's permutation back to the original triangle ID.
        const auto& indices = m.tris[size_t(triangle)]; // Get the triangle's three vertex indices.
        float t = 0, u = 0, v = 0; // Reserve this candidate's distance and interpolation coordinates.
        count_triangle_test(); // Count only triangles actually tested in reached leaves.
        if(ray_triangle(r, m.positions[size_t(indices[0])], m.positions[size_t(indices[1])], // Test two vertices...
                        m.positions[size_t(indices[2])], t, u, v) && t < nearest) { // ...and the third, rejecting farther hits.
          nearest = t; // Tighten all future node and triangle distance tests.
          store_hit(m, triangle, t, u, v, hit); // Produce the same kind of hit as brute force.
          found = true; // Remember that the return value should report a hit.
        } // End closest-leaf-hit update.
      } // End leaf triangle loop.
      continue; // Leaves have no children to schedule.
    } // End leaf handling.
    int left = index + 1; // The builder places the left subtree immediately after its parent.
    int right = node.right; // The right subtree has an explicit index because the left subtree has variable size.
    float left_entry = 0, right_entry = 0; // Compare entry distances to choose traversal order.
    const bool hit_left = ray_aabb(r, inv_d, m.bvh.nodes[size_t(left)].box, nearest, left_entry); // Test the left child.
    const bool hit_right = ray_aabb(r, inv_d, m.bvh.nodes[size_t(right)].box, nearest, right_entry); // Test the right child.
    if(hit_left && hit_right) { // Both children may contain a closer triangle.
      if(left_entry > right_entry) { // Arrange the two indices so left now denotes the nearer child.
        std::swap(left, right); // Only scheduling order changes; the tree itself is untouched.
      } // End near-child selection.
      stack[size_t(pending++)] = right; // Push the farther child first because the stack is last-in, first-out.
      stack[size_t(pending++)] = left; // The nearer child will be popped next and may shorten nearest.
    } else if(hit_left) { // Only the original left box is reachable.
      stack[size_t(pending++)] = left; // Schedule that child alone.
    } else if(hit_right) { // Only the original right box is reachable.
      stack[size_t(pending++)] = right; // Schedule that child alone.
    } // If neither box is hit, this branch needs no more work.
  } // End stack traversal.
  return found; // Return whether any triangle improved the caller's distance limit.
} // End intersect_bvh.

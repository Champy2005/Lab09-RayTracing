#include "student.h" // Import the scene, ray, RNG, vector, and student-function declarations.

#include <algorithm> // Provide max and clamp for cosines and roulette probabilities.
#include <cmath> // Provide sqrt, cos, and sin for hemisphere sampling.
#include <limits> // Provide infinity for unconstrained closest-hit queries.

// TASK 3a, Equation 11: lift a uniform disk sample to obtain density cos(theta)/pi.
vec3 cosine_sample_hemisphere(const vec3& n, float u1, float u2) { // n is a unit normal; u1 and u2 are independent uniforms.
  const float radius = std::sqrt(u1); // The square root accounts for the disk's area growing as radius squared.
  const float phi = 2.0f * PI * u2; // Uniformly choose the azimuth around the disk.
  const float x = radius * std::cos(phi); // First local tangent coordinate.
  const float y = radius * std::sin(phi); // Second local tangent coordinate.
  const float z = std::sqrt(std::max(0.0f, 1.0f - u1)); // Lift onto the upper unit hemisphere, protecting against roundoff.
  vec3 tangent, bitangent; // Reserve the other two orthonormal world-space basis vectors.
  make_basis(n, tangent, bitangent); // The provided robust routine uses n as the local z axis.
  return normalize(tangent * x + bitangent * y + n * z); // Rotate the sample into world space and preserve unit ray directions.
} // End cosine_sample_hemisphere.

// TASK 3b, Equation 12: one area-light sample estimates the directly arriving radiance.
vec3 sample_light(const Hit& hit, const PtScene& scene, Rng& rng) { // The hit normal has already been oriented toward the incident ray.
  const float u1 = rng.next(); // Draw the first lamp-area coordinate in a specified evaluation order.
  const float u2 = rng.next(); // Draw the independent second coordinate.
  const vec3 point = scene.light.corner + scene.light.e1 * u1 + scene.light.e2 * u2; // Uniformly sample the lamp parallelogram.
  const vec3 origin = hit.p + hit.n * EPS; // Begin the shadow ray slightly above the receiving surface.
  const vec3 to_light = point - origin; // Aim from the offset origin to prevent the lamp from shadowing itself.
  const float distance_squared = dot(to_light, to_light); // Use the same origin for the inverse-square geometry factor.
  if(distance_squared <= 0.0f) { // A zero-length segment has no valid unit direction.
    return vec3{0, 0, 0}; // Reject this degenerate sample.
  } // End segment-length check.
  const float distance = std::sqrt(distance_squared); // Convert squared distance to segment length.
  const vec3 direction = to_light / distance; // Normalize the direction used by both visibility and cosine tests.
  const float cos_surface = dot(hit.n, direction); // Receiver projection onto the shadow direction.
  const float cos_light = -dot(direction, scene.light.normal()); // Emitter projection; the lamp emits only from its downward face.
  if(cos_surface <= 0.0f || cos_light <= 0.0f) { // Either back-facing endpoint contributes no light.
    return vec3{0, 0, 0}; // Avoid an unnecessary visibility ray for a zero contribution.
  } // End cosine checks.
  Hit blocker; // Reserve a possible occluding triangle.
  if(pt_intersect(Ray{origin, direction}, scene, distance - EPS, blocker)) { // Stop before the sampled lamp point itself.
    return vec3{0, 0, 0}; // Visibility V is zero when another surface blocks the segment.
  } // End shadow check.
  const vec3 albedo = pt_material(scene, hit).albedo; // Read the receiver's diffuse reflectance, not its Whitted material.
  const float weight = cos_surface * cos_light * scene.light.area() / (PI * distance_squared); // BRDF 1/pi, geometry, and reciprocal area PDF.
  return albedo * scene.light.emission * weight; // Return rho/pi * Le * cos(theta_x)*cos(theta_l)/d^2 * A.
} // End sample_light.

// TASK 3c, Equation 13: randomly terminate weak paths and compensate every surviving weight.
bool russian_roulette(vec3& throughput, int bounce, Rng& rng) { // bounce is zero-based, so bounce 3 is the fourth surface.
  if(bounce < 3) { // Preserve the first three surfaces without any roulette.
    return true; // Early light transport is useful enough to keep unconditionally.
  } // End minimum-bounce check.
  const float q = std::clamp(1.0f - luminance(throughput), 0.05f, 0.95f); // Use accumulated path importance with bounded termination probability.
  if(rng.next() < q) { // Terminate with probability q.
    return false; // This path contributes no further bounces.
  } // End random termination.
  throughput /= 1.0f - q; // Weight survivors by inverse survival probability to preserve the expectation.
  return true; // Continue tracing this compensated path.
} // End russian_roulette.

// TASK 3d: a single Monte Carlo path accumulates direct illumination at each diffuse bounce.
vec3 path_trace(const Ray& r, const PtScene& scene, Rng& rng, const PtOptions& opt) { // The caller averages many such camera samples.
  Ray current = r; // Track the ray that reaches the next surface.
  vec3 throughput{1, 1, 1}; // Start with unit RGB transport weight from the camera.
  vec3 result{0, 0, 0}; // Accumulate radiance along this one path.
  for(int bounce = 0; bounce < opt.max_depth; ++bounce) { // A finite safety depth bounds work even with roulette disabled.
    Hit hit; // Reserve the next closest surface intersection.
    if(!pt_intersect(current, scene, std::numeric_limits<float>::infinity(), hit)) { // The Cornell scene has no luminous environment.
      break; // Escaping rays add no further light.
    } // End scene-miss handling.
    if(dot(hit.n, current.d) > 0.0f) { // Diffuse surfaces are shaded on the side from which the ray arrived.
      hit.n = -hit.n; // Make the normal face the incident ray before sampling its hemisphere.
    } // End normal orientation.
    const PtMaterial& material = pt_material(scene, hit); // Obtain this triangle's diffuse albedo and emitted radiance.
    if(std::max(material.emission.x, std::max(material.emission.y, material.emission.z)) > 0.0f) { // The only emissive surface is the lamp.
      if((bounce == 0 || !opt.nee) && dot(current.d, scene.light.normal()) < 0.0f) { // Count front-face emission once: directly visible or without NEE.
        result += throughput * material.emission; // Add emission weighted by every preceding bounce and roulette survival.
      } // End permitted-emission contribution.
      break; // The lamp is terminal, including its non-emitting back face.
    } // End lamp handling.
    if(opt.nee) { // Explicitly sample the lamp at every diffuse surface when NEE is enabled.
      result += throughput * sample_light(hit, scene, rng); // Add direct light; sample_light already includes this surface's albedo.
    } // End direct-light estimate.
    const float u1 = rng.next(); // Draw the bounce's radial sample first to make RNG consumption unambiguous.
    const float u2 = rng.next(); // Draw its azimuth sample second.
    const vec3 direction = cosine_sample_hemisphere(hit.n, u1, u2); // Importance sample the Lambert cosine factor.
    current = Ray{hit.p + hit.n * EPS, direction}; // Start the continuation ray on the visible side of the surface.
    throughput *= material.albedo; // Equation 10 cancels the cosine and pi, leaving only rho per bounce.
    if(opt.rr && !russian_roulette(throughput, bounce, rng)) { // Optionally terminate after updating accumulated throughput.
      break; // Direct light already accumulated at this surface remains in result.
    } // End roulette check.
  } // End surface-bounce loop.
  return result; // Return a linear-radiance estimate, before the caller averages and tone maps it.
} // End path_trace.

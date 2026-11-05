#include "student.h"

#include <algorithm>
#include <cmath>
#include <limits>

// TASK 3a, Equation 11: lift a uniform disk sample to obtain density cos(theta)/pi.
// Sample a uniform disk using radius sqrt(u1), then lift it onto the unit
// hemisphere. This produces density cos(theta)/pi. The basis vectors rotate
// the local sample so its hemisphere is centred on the surface normal n.
vec3 cosine_sample_hemisphere(const vec3& n, float u1, float u2) {
  const float radius = std::sqrt(u1);
  const float phi = 2.0f * PI * u2;
  const float x = radius * std::cos(phi);
  const float y = radius * std::sin(phi);
  const float z = std::sqrt(std::max(0.0f, 1.0f - u1));
  vec3 tangent, bitangent;
  make_basis(n, tangent, bitangent);
  return normalize(tangent * x + bitangent * y + n * z);
}

// TASK 3b, Equation 12: one area-light sample estimates the directly arriving radiance.
// Uniformly sample the area lamp and estimate Equation 12: albedo/pi times
// emission, both projected cosines, lamp area, visibility, and inverse distance
// squared. Use the offset origin consistently so the lamp cannot shadow itself.
vec3 sample_light(const Hit& hit, const PtScene& scene, Rng& rng) {
  const float u1 = rng.next();
  const float u2 = rng.next();
  const vec3 point = scene.light.corner + scene.light.e1 * u1 + scene.light.e2 * u2;
  const vec3 origin = hit.p + hit.n * EPS;
  const vec3 to_light = point - origin;
  const float distance_squared = dot(to_light, to_light);
  if(distance_squared <= 0.0f) {
    return vec3{0, 0, 0};
  }
  const float distance = std::sqrt(distance_squared);
  const vec3 direction = to_light / distance;
  const float cos_surface = dot(hit.n, direction);
  const float cos_light = -dot(direction, scene.light.normal());
  if(cos_surface <= 0.0f || cos_light <= 0.0f) {
    return vec3{0, 0, 0};
  }
  Hit blocker;
  if(pt_intersect(Ray{origin, direction}, scene, distance - EPS, blocker)) {
    return vec3{0, 0, 0};
  }
  const vec3 albedo = pt_material(scene, hit).albedo;
  const float weight = cos_surface * cos_light * scene.light.area() / (PI * distance_squared);
  return albedo * scene.light.emission * weight;
}

// TASK 3c, Equation 13: randomly terminate weak paths and compensate every surviving weight.
// Keep the first three surfaces. Thereafter choose termination probability
// from accumulated throughput, clamped to [0.05, 0.95]. Divide survivors by
// their survival probability to preserve the expected future contribution.
bool russian_roulette(vec3& throughput, int bounce, Rng& rng) {
  if(bounce < 3) {
    return true;
  }
  const float q = std::clamp(1.0f - luminance(throughput), 0.05f, 0.95f);
  if(rng.next() < q) {
    return false;
  }
  throughput /= 1.0f - q;
  return true;
}

// TASK 3d: a single Monte Carlo path accumulates direct illumination at each diffuse bounce.
// Follow one random diffuse path, accumulating direct light with the current
// throughput. Cosine sampling cancels the Lambert cosine/pi factors, leaving
// one albedo multiplication per bounce. Roulette compensates surviving paths.
vec3 path_trace(const Ray& r, const PtScene& scene, Rng& rng, const PtOptions& opt) {
  Ray current = r;
  vec3 throughput{1, 1, 1};
  vec3 result{0, 0, 0};
  for(int bounce = 0; bounce < opt.max_depth; ++bounce) {
    Hit hit;
    if(!pt_intersect(current, scene, std::numeric_limits<float>::infinity(), hit)) {
      break;
    }
    if(dot(hit.n, current.d) > 0.0f) {
      hit.n = -hit.n;
    }
    const PtMaterial& material = pt_material(scene, hit);

    // Record terminal emission before roulette. With NEE, only the camera may
    // directly count a lamp hit; later lamp hits would double-count sampled light.
    // The lamp emits only from its front face.
    if(std::max(material.emission.x, std::max(material.emission.y, material.emission.z)) > 0.0f) {
      if((bounce == 0 || !opt.nee) && dot(current.d, scene.light.normal()) < 0.0f) {
        result += throughput * material.emission;
      }
      break;
    }

    // sample_light already includes this surface's albedo. Add its contribution
    // before multiplying throughput by albedo for the next bounce.
    if(opt.nee) {
      result += throughput * sample_light(hit, scene, rng);
    }
    const float u1 = rng.next();
    const float u2 = rng.next();
    const vec3 direction = cosine_sample_hemisphere(hit.n, u1, u2);
    current = Ray{hit.p + hit.n * EPS, direction};
    throughput *= material.albedo;
    if(opt.rr && !russian_roulette(throughput, bounce, rng)) {
      break;
    }
  }
  return result;
}

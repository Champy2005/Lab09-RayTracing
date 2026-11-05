#include "student.h"

#include <algorithm>
#include <cmath>

// TASK 1a, Equation 2: send a pinhole-camera ray through the centre of this pixel.
// Convert the pixel centre to the camera plane at z = -1 using the vertical
// field of view. Scale x by the aspect ratio and flip screen y so +y is up.
// Normalize the direction so t represents distance for camera rays.
Ray camera_ray(int x, int y, int width, int height, float fov) {
  const float scale = std::tan(fov * 0.5f);
  const float aspect = float(width) / float(height);
  const float px = (2.0f * (float(x) + 0.5f) / float(width) - 1.0f) * scale * aspect;
  const float py = (1.0f - 2.0f * (float(y) + 0.5f) / float(height)) * scale;
  return Ray{vec3{0, 0, 0}, normalize(vec3{px, py, -1})};
}

// TASK 1b, Equation 3: solve |o + t*d - centre|^2 = radius^2 for the nearest forward hit.
// Substitute o + t*d into the sphere equation and solve the quadratic.
// Choose the nearest root above EPS; if the origin is inside the sphere,
// the near root is behind us and the far root gives the exit.
bool ray_sphere(const Ray& r, const Sphere& s, float& t) {
  const vec3 oc = r.o - s.center;
  const float a = dot(r.d, r.d);
  const float b = 2.0f * dot(r.d, oc);
  const float c = dot(oc, oc) - s.radius * s.radius;
  const float discriminant = b * b - 4.0f * a * c;
  if(a <= 0.0f || discriminant < 0.0f) {
    return false;
  }
  const float root = std::sqrt(discriminant);
  const float near_t = (-b - root) / (2.0f * a);
  const float far_t = (-b + root) / (2.0f * a);
  if(near_t > EPS) {
    t = near_t;
    return true;
  }
  if(far_t > EPS) {
    t = far_t;
    return true;
  }
  return false;
}

// TASK 1c, Equation 4: reverse only the component perpendicular to the surface.
// Subtract twice the normal component of d to reverse it while preserving
// the tangential component. The surface normal n must have unit length.
vec3 reflect(const vec3& d, const vec3& n) {
  return d - n * (2.0f * dot(d, n));
}

// TASK 1c, Equation 4: apply Snell's law at an air/material boundary in either direction.
// Apply Snell's law with eta = incoming index / outgoing index.
// The supplied normal points outward: on exit, flip it and reverse eta.
// A negative k means total internal reflection, so no transmitted ray exists.
bool refract(const vec3& d, const vec3& n, float ior, vec3& out) {
  vec3 normal = n;
  float cos_i = std::clamp(-dot(d, normal), -1.0f, 1.0f);
  float eta = 1.0f / ior;
  if(cos_i < 0.0f) {
    normal = -normal;
    cos_i = -cos_i;
    eta = ior;
  }
  const float k = 1.0f - eta * eta * (1.0f - cos_i * cos_i);
  if(k < 0.0f) {
    return false;
  }
  out = normalize(d * eta + normal * (eta * cos_i - std::sqrt(k)));
  return true;
}

// TASK 1d, Equation 5: progressively enable flat colour, Lambert, Phong, shadows, reflection, and refraction.
// Trace the closest surface and combine Lambert diffuse, Phong highlights,
// mirror reflection and Snell transmission using the four material weights.
// Stages 1-6 progressively enable these effects; recursion stops beyond MAX_DEPTH.
vec3 cast_ray(const Ray& r, const Scene& scene, int depth) {
  if(depth > MAX_DEPTH) {
    return scene.background;
  }
  Hit hit;
  if(!scene_intersect(r, scene, hit)) {
    return scene.background;
  }
  const Material& material = *hit.material;
  if(STAGE < 2) {
    return material.diffuse;
  }
  float diffuse = 0.0f;
  float specular = 0.0f;

  // For each point light, test visibility before adding Lambert and Phong light.
  // Offset shadow origins toward the outgoing side to avoid self-intersection.
  for(const Light& light : scene.lights) {
    const vec3 light_dir = normalize(light.position - hit.p);
    if(STAGE >= 4) {
      const vec3 origin = hit.p + hit.n * (dot(light_dir, hit.n) < 0.0f ? -EPS : EPS);
      const vec3 to_light = light.position - origin;
      const float distance = length(to_light);
      Hit blocker;
      if(scene_intersect(Ray{origin, to_light / distance}, scene, blocker) && blocker.t < distance) {
        continue;
      }
    }
    diffuse += light.intensity * std::max(0.0f, dot(light_dir, hit.n));
    if(STAGE >= 3) {
      const float alignment = std::max(0.0f, -dot(reflect(-light_dir, hit.n), r.d));
      specular += light.intensity * std::pow(alignment, material.specular_exponent);
    }
  }
  vec3 reflected{0, 0, 0};
  vec3 transmitted{0, 0, 0};

  // Keep the lesson's zero-weight recursive rays so its ray counts remain comparable.
  // Each secondary ray starts on the side of the surface toward which it travels.
  if(STAGE >= 5) {
    const vec3 direction = normalize(reflect(r.d, hit.n));
    const vec3 origin = hit.p + hit.n * (dot(direction, hit.n) < 0.0f ? -EPS : EPS);
    reflected = cast_ray(Ray{origin, direction}, scene, depth + 1);
  }
  if(STAGE >= 6) {
    vec3 direction;
    if(refract(r.d, hit.n, material.ior, direction)) {
      const vec3 origin = hit.p + hit.n * (dot(direction, hit.n) < 0.0f ? -EPS : EPS);
      transmitted = cast_ray(Ray{origin, direction}, scene, depth + 1);
    }
  }
  return material.diffuse * (diffuse * material.albedo[0])
       + vec3{1, 1, 1} * (specular * material.albedo[1])
       + reflected * material.albedo[2]
       + transmitted * material.albedo[3];
}

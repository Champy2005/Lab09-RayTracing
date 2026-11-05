#include "student.h" // Import the lab's vector, ray, scene, statistics, and function declarations.

#include <algorithm> // Provide clamp and max for bounded cosine values and lighting.
#include <cmath> // Provide tan, sqrt, and pow for camera geometry and shading.

// TASK 1a, Equation 2: send a pinhole-camera ray through the centre of this pixel.
Ray camera_ray(int x, int y, int width, int height, float fov) { // fov is the vertical field of view in radians.
  const float scale = std::tan(fov * 0.5f); // Half the image-plane height at distance one.
  const float aspect = float(width) / float(height); // Widen the image plane to preserve the image's aspect ratio.
  const float px = (2.0f * (float(x) + 0.5f) / float(width) - 1.0f) * scale * aspect; // Map the pixel centre to camera-space x.
  const float py = (1.0f - 2.0f * (float(y) + 0.5f) / float(height)) * scale; // Invert screen y so the top row points upward.
  return Ray{vec3{0, 0, 0}, normalize(vec3{px, py, -1})}; // Start at the eye and look through the plane z = -1.
} // End camera_ray.

// TASK 1b, Equation 3: solve |o + t*d - centre|^2 = radius^2 for the nearest forward hit.
bool ray_sphere(const Ray& r, const Sphere& s, float& t) { // Write t only when a valid sphere intersection exists.
  const vec3 oc = r.o - s.center; // Express the ray origin relative to the sphere centre.
  const float a = dot(r.d, r.d); // Keep the full quadratic so non-unit ray directions also work.
  const float b = 2.0f * dot(r.d, oc); // The linear coefficient has the direction's sign, including negative z.
  const float c = dot(oc, oc) - s.radius * s.radius; // Subtract the squared radius from the origin's squared distance.
  const float discriminant = b * b - 4.0f * a * c; // A negative discriminant means the line misses the sphere.
  if(a <= 0.0f || discriminant < 0.0f) { // Reject a zero direction or a quadratic with no real roots.
    return false; // There is no usable intersection.
  } // End invalid-quadratic check.
  const float root = std::sqrt(discriminant); // Compute the shared square-root term once.
  const float near_t = (-b - root) / (2.0f * a); // The smaller root is the sphere's entry point.
  const float far_t = (-b + root) / (2.0f * a); // The larger root is the exit point, needed inside glass.
  if(near_t > EPS) { // Prefer the entry if it lies beyond the self-intersection threshold.
    t = near_t; // Return the nearest valid distance along the ray.
    return true; // Report a hit.
  } // End near-root check.
  if(far_t > EPS) { // When the entry is behind us, the exit may still be ahead.
    t = far_t; // Return the exit distance for a ray starting inside the sphere.
    return true; // Report a hit.
  } // End far-root check.
  return false; // Both roots are behind or too close to the origin.
} // End ray_sphere.

// TASK 1c, Equation 4: reverse only the component perpendicular to the surface.
vec3 reflect(const vec3& d, const vec3& n) { // n must be a unit surface normal.
  return d - n * (2.0f * dot(d, n)); // Preserve the tangent component and negate the normal component.
} // End reflect.

// TASK 1c, Equation 4: apply Snell's law at an air/material boundary in either direction.
bool refract(const vec3& d, const vec3& n, float ior, vec3& out) { // n points out of the object; ior is its refractive index.
  vec3 normal = n; // Use a local normal so the caller's geometric normal stays unchanged.
  float cos_i = std::clamp(-dot(d, normal), -1.0f, 1.0f); // Measure the incoming cosine and protect against roundoff.
  float eta = 1.0f / ior; // Assume entry from air into the material first.
  if(cos_i < 0.0f) { // A direction aligned with the outward normal is leaving the object.
    normal = -normal; // Face the interface normal toward the incoming ray.
    cos_i = -cos_i; // Make the incidence cosine nonnegative after the flip.
    eta = ior; // Leaving material for air reverses the index ratio.
  } // End exit-side adjustment.
  const float k = 1.0f - eta * eta * (1.0f - cos_i * cos_i); // Snell's law gives the squared transmitted cosine.
  if(k < 0.0f) { // A negative value means the critical angle was exceeded.
    return false; // Total internal reflection permits no transmitted ray.
  } // End total-internal-reflection check.
  out = normalize(d * eta + normal * (eta * cos_i - std::sqrt(k))); // Build and normalize the transmitted direction.
  return true; // The caller may trace the transmitted ray.
} // End refract.

// TASK 1d, Equation 5: progressively enable flat colour, Lambert, Phong, shadows, reflection, and refraction.
vec3 cast_ray(const Ray& r, const Scene& scene, int depth) { // depth counts secondary-ray bounces from the camera.
  if(depth > MAX_DEPTH) { // Match the handout's strict greater-than depth cutoff.
    return scene.background; // The Whitted tracer uses sky colour beyond the recursion limit.
  } // End depth cutoff.
  Hit hit; // Reserve the closest intersection's position, normal, and material.
  if(!scene_intersect(r, scene, hit)) { // The framework counts this ray and checks every scene object.
    return scene.background; // A ray leaving the scene sees the sky immediately.
  } // End miss check.
  const Material& material = *hit.material; // Read the material selected by the closest-hit routine.
  if(STAGE < 2) { // Lesson 1 only identifies which object a camera ray sees.
    return material.diffuse; // Show each object's unlit diffuse colour.
  } // End flat-colour stage.
  float diffuse = 0.0f; // Accumulate Lambert illumination from visible point lights.
  float specular = 0.0f; // Accumulate white Phong highlights separately from the diffuse colour.
  for(const Light& light : scene.lights) { // Evaluate each of the three provided point lights.
    const vec3 light_dir = normalize(light.position - hit.p); // Direction from the hit toward this light.
    if(STAGE >= 4) { // Lesson 4 adds hard shadows by testing visibility to each lamp.
      const vec3 origin = hit.p + hit.n * (dot(light_dir, hit.n) < 0.0f ? -EPS : EPS); // Offset onto the outgoing ray's side.
      const vec3 to_light = light.position - origin; // Aim from the actual offset origin, not the unshifted surface.
      const float distance = length(to_light); // Measure the segment to the light from that same origin.
      Hit blocker; // Store a possible occluder, including objects behind the light.
      if(scene_intersect(Ray{origin, to_light / distance}, scene, blocker) && blocker.t < distance && blocker.material->albedo[3] == 0.0f) { // Only nearer geometry blocks the lamp.
        continue; // This light contributes neither Lambert nor Phong at a shadowed point.
      } // End visibility check.
    } // End shadow stage.
    diffuse += light.intensity * std::max(0.0f, dot(light_dir, hit.n)); // Equation 5: irradiance falls with the incident cosine.
    if(STAGE >= 3) { // Lesson 3 adds view-dependent specular highlights.
      const float alignment = std::max(0.0f, -dot(reflect(-light_dir, hit.n), r.d)); // Compare the reflected light with the viewing direction.
      specular += light.intensity * std::pow(alignment, material.specular_exponent); // A large exponent makes a narrow highlight.
    } // End specular stage.
  } // End light loop.
  vec3 reflected{0, 0, 0}; // Keep reflection black until that lesson is enabled.
  vec3 transmitted{0, 0, 0}; // Failed transmission also stays black, exposing the lab's dark-wedge limitation.
  if(STAGE >= 5) { // Lesson 5 adds a recursive mirror ray at every hit, even if its weight is zero.
    const vec3 direction = normalize(reflect(r.d, hit.n)); // Compute a unit reflected direction.
    const vec3 origin = hit.p + hit.n * (dot(direction, hit.n) < 0.0f ? -EPS : EPS); // Start on the reflected ray's side of the surface.
    reflected = cast_ray(Ray{origin, direction}, scene, depth + 1); // Trace one more bounce to find the reflected colour.
  } // End reflection stage.
  if(STAGE >= 6) { // Lesson 6 adds Snell refraction alongside reflection.
    vec3 direction; // refract writes this only if a real transmitted direction exists.
    if(refract(r.d, hit.n, material.ior, direction)) { // Total internal reflection leaves the transmission term at zero.
      const vec3 origin = hit.p + hit.n * (dot(direction, hit.n) < 0.0f ? -EPS : EPS); // Entry starts inside; exit starts outside.
      transmitted = cast_ray(Ray{origin, direction}, scene, depth + 1); // Trace the scene seen through the interface.
    } // End valid-transmission check.
  } // End refraction stage.
  return material.diffuse * (diffuse * material.albedo[0]) // Weight the coloured Lambert contribution.
       + vec3{1, 1, 1} * (specular * material.albedo[1]) // Add the white Phong contribution.
       + reflected * material.albedo[2] // Add the material's reflected fraction.
       + transmitted * material.albedo[3]; // Add its transmitted fraction without redistributing TIR energy.
} // End cast_ray.

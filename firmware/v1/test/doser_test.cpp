// Host tests for the weight-controlled doser with a simulated screw/pump and scale.
//
//   g++ -std=gnu++17 -Wall -Wextra -O1 -I firmware/v1/components/bakeplan
//       firmware/v1/components/bakeplan/doser.cpp firmware/v1/test/doser_test.cpp -o doser_test

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <random>

#include "doser.h"

using namespace surdeig;

static int failures = 0;
#define CHECK(cond, ...)                                     \
  do {                                                       \
    if (!(cond)) {                                           \
      failures++;                                            \
      std::printf("  FAIL %s:%d: ", __FILE__, __LINE__);     \
      std::printf(__VA_ARGS__);                              \
      std::printf("\n");                                     \
    }                                                        \
  } while (0)

// Screw or pump with variable flow, material in flight (afterflow), a delayed and noisy
// scale, an optional bridge in the hopper and a limited stock.
struct Plant {
  float flow = 3.0f;          // mean g/s
  float flow_var = 0.25f;     // slow variation (fraction)
  float in_flight_s = 0.25f;  // material falling when the screw stops
  float delay_s = 0.15f;      // scale reading delay
  float noise_g = 0.05f;
  float stock_g = 1e9f;
  float bridge_at_g = -1.0f;  // a bridge forms at this dosed weight ...
  bool bridged = false;       // ... and holds until the screw reverses
  float tare_offset = 1234.0f;

  float true_g = 0.0f;
  float slow = 0.0f;
  std::deque<std::pair<float, float>> falling;   // (arrival time, grams)
  std::deque<std::pair<float, float>> readings;  // (time, value)
  std::mt19937 rng{42};

  void step(float t, float dt, DoseCommand c) {
    std::normal_distribution<float> n01(0.0f, 1.0f);
    slow = 0.98f * slow + 0.2f * 0.14f * n01(rng);  // AR(1) around 0, std about flow_var
    if (bridge_at_g >= 0.0f && !bridged && true_g >= bridge_at_g) {
      bridged = true;
      bridge_at_g = -1.0f;
    }
    if (c.run && c.reverse) bridged = false;
    if (c.run && !c.reverse && !bridged && stock_g > 0.0f) {
      float q = flow * std::max(0.2f, 1.0f + flow_var * slow / 0.14f * 0.5f);
      float g = std::min(stock_g, q * dt);
      stock_g -= g;
      falling.emplace_back(t + in_flight_s, g);
    }
    while (!falling.empty() && falling.front().first <= t) {
      true_g += falling.front().second;
      falling.pop_front();
    }
    readings.emplace_back(t, true_g);
  }

  float reading(float t) {
    std::normal_distribution<float> n(0.0f, noise_g);
    float v = 0.0f;
    while (readings.size() > 1 && readings[1].first <= t - delay_s) readings.pop_front();
    if (!readings.empty()) v = readings.front().second;
    return tare_offset + v + n(rng);
  }
};

struct Result {
  DoseState state;
  float error_g;
  float time_s;
  int recoveries;
  int pulses;
  const char *fault;
};

static Result run(Plant plant, float target, DoseParams p, float max_s = 1200.0f) {
  Doser d;
  const float dt = 0.1f;
  float t = 0.0f;
  d.start(target, t, p);
  DoseCommand c;
  while (t < max_s) {
    plant.step(t, dt, c);
    c = d.update(t, plant.reading(t));
    if (!d.busy()) break;
    t += dt;
  }
  // let everything in flight land
  for (int i = 0; i < 30; i++) plant.step(t + i * dt, dt, DoseCommand());
  return {d.state(), plant.true_g - target, t, d.recoveries(), d.fine_pulses(), d.fault()};
}

static DoseParams flour_params() {
  DoseParams p;
  p.flow_guess_g_s = 3.0f;
  return p;
}

static DoseParams water_params() {
  DoseParams p;
  p.flow_guess_g_s = 6.5f;
  p.lag_s = 0.4f;
  p.reverse_s = 1.5f;   // pump runs backwards to empty the nozzle
  p.stall_s = 6.0f;
  return p;
}

static DoseParams salt_params() {
  DoseParams p;
  p.flow_guess_g_s = 0.6f;
  p.tolerance_g = 0.3f;
  p.stall_gain_g = 0.3f;
  p.max_pulse_s = 3.0f;
  return p;
}

static void test_flour() {
  std::printf("flour 0..560 g\n");
  for (float flow : {1.5f, 3.0f, 4.5f}) {
    Plant pl;
    pl.flow = flow;
    Result r = run(pl, 560.0f, flour_params());
    std::printf("  flow %.1f g/s: %s error %+.2f g in %.0f s, %d fine pulses\n", flow, dose_state_name(r.state),
                r.error_g, r.time_s, r.pulses);
    CHECK(r.state == DoseState::Done, "flour not done (%s)", r.fault);
    CHECK(std::fabs(r.error_g) <= 1.5f, "flour error %.2f g", r.error_g);
    CHECK(r.time_s < 560.0f / flow * 1.6f + 30.0f, "flour too slow: %.0f s", r.time_s);
  }
}

static void test_water_and_salt() {
  std::printf("water and salt\n");
  Plant w;
  w.flow = 6.7f;
  w.in_flight_s = 0.35f;
  w.flow_var = 0.05f;
  Result r = run(w, 422.0f, water_params());
  std::printf("  water 422 g: %s error %+.2f g in %.0f s\n", dose_state_name(r.state), r.error_g, r.time_s);
  CHECK(r.state == DoseState::Done && std::fabs(r.error_g) <= 1.2f, "water error %.2f", r.error_g);

  Plant s;
  s.flow = 0.5f;
  s.in_flight_s = 0.3f;
  s.flow_var = 0.3f;
  r = run(s, 11.2f, salt_params());
  std::printf("  salt 11.2 g: %s error %+.2f g in %.0f s, %d pulses\n", dose_state_name(r.state), r.error_g,
              r.time_s, r.pulses);
  CHECK(r.state == DoseState::Done && std::fabs(r.error_g) <= 0.5f, "salt error %.2f", r.error_g);
}

static void test_bridge_and_empty() {
  std::printf("bridge and empty hopper\n");
  Plant b;
  b.bridge_at_g = 200.0f;
  Result r = run(b, 560.0f, flour_params());
  std::printf("  bridge at 200 g: %s error %+.2f g, %d recoveries\n", dose_state_name(r.state), r.error_g,
              r.recoveries);
  CHECK(r.state == DoseState::Done && r.recoveries == 1, "bridge not handled (%s)", r.fault);
  CHECK(std::fabs(r.error_g) <= 1.5f, "bridge error %.2f", r.error_g);

  Plant e;
  e.stock_g = 300.0f;
  r = run(e, 560.0f, flour_params());
  std::printf("  empty after 300 g: %s (%s) after %.0f s\n", dose_state_name(r.state), r.fault, r.time_s);
  CHECK(r.state == DoseState::Fault, "empty hopper not detected");
  CHECK(r.time_s < 300.0f / 3.0f + 60.0f, "empty hopper detected late: %.0f s", r.time_s);
}

static void test_noisy_scale() {
  std::printf("noisy scale\n");
  Plant n;
  n.noise_g = 1.5f;
  Result r = run(n, 100.0f, flour_params());
  std::printf("  noise 1.5 g: %s (%s)\n", dose_state_name(r.state), r.fault);
  CHECK(r.state == DoseState::Fault, "noisy scale should not tare");
}

static void test_filter() {
  std::printf("filter\n");
  WeightFilter f;
  for (int i = 0; i < 20; i++) f.push(i * 0.1f, 100.0f + ((i % 2) ? 0.05f : -0.05f));
  CHECK(f.stable(1.0f, 0.15f), "filter should be stable");
  f.push(2.0f, 150.0f);  // single spike is removed by the median
  CHECK(std::fabs(f.latest() - 100.0f) < 0.2f, "median failed: %.2f", f.latest());
}

int main() {
  test_filter();
  test_flour();
  test_water_and_salt();
  test_bridge_and_empty();
  test_noisy_scale();
  if (failures) {
    std::printf("%d FAILURE(S)\n", failures);
    return 1;
  }
  std::printf("ALL PASSED\n");
  return 0;
}

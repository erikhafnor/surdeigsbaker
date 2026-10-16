// Whole-day simulation of a v1 bake: plan, levain, dough, folds, bulk, ready for shaping.
//
//   g++ -std=gnu++17 -Wall -Wextra -O2 -I firmware/v1/components/bakeplan
//       firmware/v1/components/bakeplan/{planner,doser,sequence,bake,sim}.cpp
//       firmware/v1/test/bake_test.cpp -o bake_test

#include <cmath>
#include <cstdio>
#include <functional>

#include "bake.h"
#include "sim.h"

using namespace surdeig;

static int failures = 0;
#define CHECK(cond, ...)                                 \
  do {                                                   \
    if (!(cond)) {                                       \
      failures++;                                        \
      std::printf("  FAIL %s:%d: ", __FILE__, __LINE__); \
      std::printf(__VA_ARGS__);                          \
      std::printf("\n");                                 \
    }                                                    \
  } while (0)

struct DayResult {
  bool started = false;
  bool ready = false;
  float ready_h = NAN;    // hours after start
  float target_h = NAN;
  float rise_fraction = NAN;
  float added[kIngredients] = {0, 0, 0};
  int dose_while_kneading = 0;
  int dose_closed_flap = 0;
  float knead_s = 0;
  float learned = NAN;
  std::string message;
  bool fault_seen = false;
};

// Hook for disturbances: called every step with (t_s, bake, sim, inputs) and may change inputs.
using Hook = std::function<void(float, Bake &, SimMachine &, Bake::Inputs &)>;

static DayResult run_day(float hours_until_ready, const SimParams &sp, bool cold = true, float prior = 1.0f,
                         Hook hook = nullptr, bool verbose = false) {
  DayResult r;
  BakeConfig cfg;
  Bake bake(cfg);
  SimMachine sim(sp, cfg);
  bake.set_empty_pan(sim.empty_pan_g());
  const float dt = 0.2f;
  float t = 0.0f;
  Bake::Outputs out;
  // Let the scale settle before start (the starter is weighed).
  for (; t < 5.0f; t += dt) {
    Bake::Inputs in;
    in.now_s = t;
    in.weight_g = sim.weight_g();
    in.room_c = sim.room_c();
    bake.update(in);
  }
  r.target_h = hours_until_ready;
  r.started = bake.start(t, hours_until_ready, cold, prior);
  r.message = bake.message();
  if (!r.started) return r;
  const float t0 = t;
  Stage last_stage = Stage::Idle;
  const char *last_status = "";
  while (t - t0 < (hours_until_ready + 6.0f) * 3600.0f) {
    sim.step(t, dt, out.machine, out.machine.quiet ? NAN : out.setpoint_c, bake.controller().stage(), bake.plan());
    Bake::Inputs in;
    in.now_s = t;
    in.weight_g = sim.weight_g();
    in.tof_mm = sim.tof_mm();
    in.dough_c = sim.dough_c();
    in.room_c = sim.room_c();
    if (hook) hook(t - t0, bake, sim, in);
    out = bake.update(in);
    if (bake.sequence().faulted()) r.fault_seen = true;
    if (verbose && (bake.controller().stage() != last_stage || std::string(bake.status()) != last_status)) {
      last_stage = bake.controller().stage();
      last_status = bake.status();
      std::printf("    %5.2f h  %-28s %5.1f °C  rise %5.1f %%\n", (t - t0) / 3600.0f, bake.status(), sim.dough_c(),
                  bake.rise_pct());
    }
    if (out.ready) {
      r.ready = true;
      r.ready_h = (t - t0) / 3600.0f;
      break;
    }
    t += dt;
  }
  r.rise_fraction = sim.true_rise_fraction();
  for (int i = 0; i < kIngredients; i++) r.added[i] = sim.added_g(Ingredient(i));
  r.dose_while_kneading = sim.dose_while_kneading();
  r.dose_closed_flap = sim.dose_with_closed_flap();
  r.knead_s = sim.knead_seconds();
  r.learned = bake.learned_activity();
  return r;
}

static void check_amounts(const DayResult &r, float starter_g) {
  DoughRecipe d;
  const float flour_total = 560.0f, sf = starter_g / 2.0f;
  const float want_flour = flour_total - sf;
  const float want_water = d.hydration * flour_total - sf;
  const float want_salt = d.salt_frac * flour_total;
  CHECK(std::fabs(r.added[1] - want_flour) <= 2.5f, "flour %.1f g, want %.1f", r.added[1], want_flour);
  CHECK(std::fabs(r.added[0] - want_water) <= 2.5f, "water %.1f g, want %.1f", r.added[0], want_water);
  CHECK(std::fabs(r.added[2] - want_salt) <= 0.5f, "salt %.2f g, want %.2f", r.added[2], want_salt);
}

static void test_typical_day() {
  std::printf("typical day: 07:00 → 18:00, 20 g cold starter\n");
  SimParams sp;
  DayResult r = run_day(11.0f, sp, true, 1.0f, nullptr, true);
  CHECK(r.started, "not started: %s", r.message.c_str());
  CHECK(r.ready, "never ready");
  std::printf("  ready after %.2f h (target %.1f), rise %.2f of target, kneaded %.0f s\n", r.ready_h, r.target_h,
              r.rise_fraction, r.knead_s);
  std::printf("  added: water %.1f g, flour %.1f g, salt %.2f g\n", r.added[0], r.added[1], r.added[2]);
  CHECK(std::fabs(r.ready_h - r.target_h) <= 0.5f, "off target by %.2f h", r.ready_h - r.target_h);
  CHECK(r.rise_fraction > 0.85f && r.rise_fraction < 1.15f, "rise %.2f", r.rise_fraction);
  CHECK(r.dose_while_kneading == 0, "dosed while kneading (%d)", r.dose_while_kneading);
  CHECK(r.dose_closed_flap == 0, "dosed with a closed flap (%d)", r.dose_closed_flap);
  CHECK(r.knead_s > 600.0f, "too little kneading: %.0f s", r.knead_s);
  CHECK(!std::isnan(r.learned), "no activity learned");
  check_amounts(r, sp.starter_g);
}

static void test_infeasible() {
  std::printf("infeasible: 1 tbsp cold starter at 07:00, ready at 17:00\n");
  SimParams sp;
  DayResult r = run_day(10.0f, sp);
  std::printf("  %s\n", r.message.c_str());
  CHECK(!r.started, "10 h should be too short for 20 g cold starter");
  sp.starter_g = 40.0f;
  r = run_day(10.0f, sp);
  std::printf("  with 40 g: %s (%s)\n", r.started ? "started" : "not started", r.message.c_str());
  CHECK(r.started && r.ready && std::fabs(r.ready_h - 10.0f) <= 0.6f, "40 g should make 17:00 (%.2f h)", r.ready_h);
}

static void test_starters() {
  std::printf("starter faster or slower than the model\n");
  for (float a : {0.8f, 1.25f}) {
    SimParams sp;
    sp.activity = a;
    DayResult r = run_day(12.0f, sp);
    std::printf("  activity %.2f: ready after %.2f h (target 12), rise %.2f, learned %.2f\n", a, r.ready_h,
                r.rise_fraction, r.learned);
    CHECK(r.ready, "never ready");
    CHECK(std::fabs(r.ready_h - 12.0f) <= 1.0f, "activity %.2f off by %.2f h", a, r.ready_h - 12.0f);
    CHECK(r.rise_fraction > 0.8f && r.rise_fraction < 1.25f, "rise %.2f", r.rise_fraction);
    // learning goes in the right direction
    CHECK((a > 1.0f) == (r.learned > 1.0f), "learned %.2f for true %.2f", r.learned, a);
  }
}

static void test_door_during_kneading() {
  std::printf("door opened for 60 s during kneading\n");
  SimParams sp;
  bool opened = false;
  float open_until = -1.0f;
  Hook hook = [&](float t, Bake &b, SimMachine &, Bake::Inputs &in) {
    if (!opened && std::string(b.sequence().status()) == "Elter") {
      opened = true;
      open_until = t + 60.0f;
    }
    if (opened && t < open_until) in.door_closed = false;
    if (opened && t >= open_until && b.sequence().waiting_for_confirm()) b.confirm();
  };
  DayResult ref = run_day(11.0f, sp);
  DayResult r = run_day(11.0f, sp, true, 1.0f, hook);
  std::printf("  kneaded %.0f s (without the pause %.0f s), ready after %.2f h\n", r.knead_s, ref.knead_s, r.ready_h);
  CHECK(opened, "kneading never seen");
  CHECK(std::fabs(r.knead_s - ref.knead_s) < 3.0f, "kneading time changed: %.0f vs %.0f", r.knead_s, ref.knead_s);
  CHECK(r.ready && std::fabs(r.ready_h - 11.0f) <= 0.6f, "door pause broke the plan");
}

static void test_flour_runs_out() {
  std::printf("flour runs out during the dough\n");
  SimParams sp;
  sp.stock_g[1] = 300.0f;  // enough for the levain, not for the dough
  bool refilled = false;
  Hook hook = [&](float, Bake &b, SimMachine &s, Bake::Inputs &) {
    if (b.sequence().faulted() && !refilled) {
      refilled = true;
      s.refill(Ingredient::Flour, 1500.0f);
      b.confirm();
    }
  };
  DayResult r = run_day(11.0f, sp, true, 1.0f, hook);
  std::printf("  fault seen: %s, refilled: %s, flour %.1f g, ready after %.2f h\n", r.fault_seen ? "yes" : "no",
              refilled ? "yes" : "no", r.added[1], r.ready_h);
  CHECK(refilled, "empty hopper not reported");
  CHECK(r.ready, "bake did not finish after refill");
  check_amounts(r, sp.starter_g);
}

static void test_pan_geometry() {
  std::printf("pan geometry\n");
  PanGeometry p;
  float v = p.volume_ml(50.0f);
  float h = p.height_for_volume(v);
  CHECK(std::fabs(h - 50.0f) < 0.05f, "height_for_volume %.2f", h);
  CHECK(v > 1000.0f && v < 1200.0f, "volume at 50 mm %.0f ml", v);
}

int main() {
  test_pan_geometry();
  test_typical_day();
  test_infeasible();
  test_starters();
  test_door_during_kneading();
  test_flour_runs_out();
  if (failures) {
    std::printf("%d FAILURE(S)\n", failures);
    return 1;
  }
  std::printf("ALL PASSED\n");
  return 0;
}

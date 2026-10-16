// Unit and closed-loop tests for the fermentation planner.
//
//   g++ -std=gnu++17 -Wall -O1 -I firmware/v1/components/bakeplan
//       firmware/v1/components/bakeplan/planner.cpp firmware/v1/test/planner_test.cpp
//       -o /tmp/planner_test && /tmp/planner_test
//
// The closed-loop test simulates a bake with a starter that is slower or faster than the
// model, a dough temperature that lags the setpoint and can never go below room
// temperature, folds that hide the rise for the first part of the bulk, and a noisy
// rise measurement.

#include "planner.h"

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

using namespace bakeplan;

static int failures = 0;

#define CHECK(cond, ...)                                \
  do {                                                  \
    if (!(cond)) {                                      \
      std::printf("FAIL %s:%d: ", __FILE__, __LINE__); \
      std::printf(__VA_ARGS__);                         \
      std::printf("\n");                                \
      failures++;                                       \
    }                                                   \
  } while (0)

static bool near(float a, float b, float tol) { return std::fabs(a - b) <= tol; }

static const char *clock(float h) {
  static char buf[4][8];
  static int n = 0;
  char *b = buf[n++ % 4];
  float hh = std::fmod(h, 24.0f);
  int hours = static_cast<int>(hh);
  int minutes = static_cast<int>(std::round((hh - hours) * 60.0f));
  if (minutes == 60) { hours = (hours + 1) % 24; minutes = 0; }
  std::snprintf(b, 8, "%02d:%02d", hours, minutes);
  return b;
}

// ---------------------------------------------------------------- unit tests

static void test_rate_table() {
  ModelParams p;
  CHECK(near(speed_factor(24.0f, p), 1.0f, 1e-5f), "factor at 24 C");
  CHECK(near(speed_factor(22.0f, p), 0.818f, 1e-3f), "factor at 22 C");
  CHECK(speed_factor(15.0f, p) < speed_factor(16.0f, p), "extrapolates below the table");
  for (float t = 16; t <= 29.5f; t += 0.7f) {
    CHECK(speed_factor(t + 0.5f, p) > speed_factor(t, p), "monotonic at %.1f", t);
    CHECK(near(temp_for_factor(speed_factor(t, p), p), t, 0.02f), "inverse at %.1f", t);
  }
  CHECK(near(bulk_rise_target(25.0f, p), 40.0f, 0.01f), "rise target 25 C");
  CHECK(near(bulk_rise_target(23.0f, p), 57.5f, 0.01f), "rise target 23 C");
}

static void test_model_matches_research_tables() {
  ModelParams p;
  // docs/forskning/v1-gjaeringsmodell.md: levain x2, fridge-cold starter, 1:2.5:2.5 (D = 6).
  float t24 = levain_eq_h(6.0f, true, p) / speed_factor(24.0f, p);
  float t28 = levain_eq_h(6.0f, true, p) / speed_factor(28.0f, p);
  CHECK(near(t24, 8.7f, 0.3f), "levain 1:2.5:2.5 at 24 C: %.2f h", t24);
  CHECK(near(t28, 6.9f, 0.3f), "levain 1:2.5:2.5 at 28 C: %.2f h", t28);
  // Bulk to +30 % with s = 21 %: 5.0 h at 24 C.
  float b24 = bulk_eq_h(21.0f, 100.0f, 30.0f, p) / speed_factor(24.0f, p);
  CHECK(near(b24, 5.0f, 0.3f), "bulk at 24 C: %.2f h", b24);
}

static void test_plan_typical_day() {
  ModelParams p;
  Recipe r;  // 20 g fridge-cold starter, 560 g flour
  float earliest, latest;
  feasible_window(21.0f, 1.0f, r, p, &earliest, &latest);
  std::printf("  07:00 start, 20 g cold starter, room 21 C: earliest %s, latest %s\n", clock(7 + earliest),
              clock(7 + latest));
  // Research: with a tablespoon of cold starter the earliest is about 18:00.
  CHECK(7 + earliest > 16.5f && 7 + earliest < 19.5f, "earliest %s", clock(7 + earliest));

  Plan target17 = make_plan(10.0f, 21.0f, 1.0f, r, p);
  std::printf("  ready 17:00 with 20 g cold: %s\n", target17.reason.c_str());

  Recipe two_spoons = r;
  two_spoons.starter_g = 40.0f;
  feasible_window(21.0f, 1.0f, two_spoons, p, &earliest, &latest);
  std::printf("  40 g cold starter: earliest %s\n", clock(7 + earliest));
  Recipe fed = r;
  fed.cold_starter = false;
  feasible_window(21.0f, 1.0f, fed, p, &earliest, &latest);
  std::printf("  20 g starter fed the evening before: earliest %s\n", clock(7 + earliest));

  Plan evening = make_plan(13.0f, 21.0f, 1.0f, r, p);  // ready 20:00
  std::printf("  ready 20:00 with 20 g cold: %s\n", evening.reason.c_str());
  CHECK(evening.feasible, "20:00 should be feasible");
  CHECK(near(evening.total_h, 13.0f, 0.02f), "total %.2f", evening.total_h);
  CHECK(evening.temp_c >= 21.0f && evening.temp_c <= 28.0f, "temp %.2f", evening.temp_c);
  CHECK(evening.pff >= p.pff_min - 1e-3f && evening.pff <= p.pff_max + 1e-3f, "pff %.3f", evening.pff);
  CHECK(near(evening.levain_flour_g, 0.5f * r.starter_g * (evening.dilution - 1.0f), 1e-3f), "levain flour");
}

static void test_plan_limits() {
  ModelParams p;
  Recipe r;
  Plan early = make_plan(4.0f, 21.0f, 1.0f, r, p);
  CHECK(!early.feasible, "4 h should be too early");
  CHECK(early.reason.find("too early") != std::string::npos, "reason: %s", early.reason.c_str());
  Plan late = make_plan(40.0f, 21.0f, 1.0f, r, p);
  CHECK(!late.feasible, "40 h should be too late");
  CHECK(late.reason.find("too late") != std::string::npos, "reason: %s", late.reason.c_str());
  Plan hot = make_plan(9.0f, 29.0f, 1.0f, r, p);
  if (hot.feasible) CHECK(hot.temp_c >= 29.0f - 1e-3f, "hot temp %.2f", hot.temp_c);
  std::printf("  hot kitchen 29 C, 9 h: %s\n", hot.reason.c_str());
  // A huge starter still gives a plan (closest allowed dilution).
  Recipe big = r;
  big.starter_g = 150.0f;
  Plan bigp = make_plan(9.0f, 21.0f, 1.0f, big, p);
  std::printf("  150 g starter, 9 h: %s\n", bigp.reason.c_str());
}

static void test_activity_estimate() {
  ModelParams p;
  float target = 5.0f, elapsed = 2.0f, a_true = 1.3f;
  float rise = std::pow(elapsed * a_true / target, kRiseShape);
  float est = activity_from_rise(rise, elapsed, target, 1.0f, p);
  CHECK(near(est, a_true, 0.01f), "activity estimate %.3f", est);
  CHECK(near(activity_from_rise(0.1f, elapsed, target, 0.9f, p), 0.9f, 1e-6f), "too early keeps prior");
  CHECK(near(activity_from_rise(NAN, elapsed, target, 0.9f, p), 0.9f, 1e-6f), "NaN keeps prior");
}

static void test_temp_to_finish() {
  ModelParams p;
  float eta;
  float t = temp_to_finish_in(4.0f, 4.0f, 20.0f, p, &eta);
  CHECK(near(t, 24.0f, 0.02f) && near(eta, 4.0f, 0.02f), "24 C: %.2f %.2f", t, eta);
  t = temp_to_finish_in(4.0f, 20.0f, 21.0f, p, &eta);  // would need cooling: room temperature
  CHECK(near(t, 21.0f, 1e-3f) && eta < 20.0f, "clamp low: %.2f eta %.2f", t, eta);
  t = temp_to_finish_in(4.0f, 1.0f, 21.0f, p, &eta);  // impossible: maximum
  CHECK(near(t, 28.0f, 1e-3f) && eta > 1.0f, "clamp high: %.2f eta %.2f", t, eta);
}

// ---------------------------------------------------------------- closed-loop simulation

struct SimResult {
  bool started = false;
  float ready_h = NAN;
  float error_h = NAN;
  float first_warning_h = NAN;  // when off_target(0.75) first became true
  float min_temp = 99, max_temp = 0;
  float true_rise_at_finish = NAN;  // 1.0 = exactly the target rise
  float learned_activity = NAN;
  float late_risk_h = 0.0f;  // what the plan told the user at start
};

static uint32_t rng_state = 12345;
static float noise() {  // roughly uniform in [-1, 1]
  rng_state = rng_state * 1664525u + 1013904223u;
  return ((rng_state >> 8) & 0xFFFF) / 32767.5f - 1.0f;
}

static SimResult simulate(float a_true, bool measure, float room_c, float target_h, const Recipe &recipe,
                          float prior = 1.0f, float noise_frac = 0.06f) {
  const bool measure_levain = false;  // the levain is a thin layer the ToF sensor cannot see
  ModelParams p;
  Controller c(p);
  SimResult r;
  const float t0 = 7.0f;
  r.started = c.start(t0, target_h, room_c, recipe, prior);
  if (!r.started) return r;
  r.late_risk_h = c.plan().late_risk_h;
  const float rise_target = c.plan().rise_target_pct / 100.0f;

  const float dt = 1.0f / 60.0f;
  float dough_c = room_c;
  // Truth: activity-weighted equivalent hours since the levain was fed / the dough was mixed.
  float lev_true = 0.0f, bulk_true = 0.0f;
  float lev_need = c.levain_target_eq_h(), bulk_need = c.bulk_target_eq_h();  // in activity-1 units
  float rise_at_baseline = NAN;  // true overall rise when the post-fold baseline was taken
  float busy_until = NAN, folds_done_at = NAN;
  Request busy = Request::None;

  for (float now = t0; now < t0 + 36.0f; now += dt) {
    float sp = c.setpoint_c();
    float goal = std::isnan(sp) ? room_c : std::max(sp, room_c);
    float tau = goal >= dough_c ? 0.6f : 1.5f;
    dough_c += (goal - dough_c) * dt / tau;
    r.min_temp = std::min(r.min_temp, dough_c);
    r.max_temp = std::max(r.max_temp, dough_c);

    Stage st = c.stage();
    float inc = dt * speed_factor(dough_c, p) * a_true;
    if (st == Stage::Levain) lev_true += inc;
    if (st == Stage::Dough || st == Stage::Bulk) bulk_true += inc;
    float rise_true = rise_target * std::pow(std::min(1.5f, bulk_true / bulk_need), kRiseShape);

    Measurement m;
    m.room_c = room_c;
    m.dough_c = dough_c;
    if (measure && st == Stage::Levain && measure_levain) {
      m.rise_pct = 100.0f * std::pow(std::min(1.3f, lev_true / lev_need), kRiseShape) * (1.0f + noise_frac * noise());
    } else if (measure && st == Stage::Bulk && c.measuring() && !std::isnan(rise_at_baseline)) {
      float rel = (1.0f + rise_true) / (1.0f + rise_at_baseline) - 1.0f;
      m.rise_pct = 100.0f * rel * (1.0f + noise_frac * noise());
    }
    c.tick(now, m);
    if (!std::isnan(folds_done_at) && now >= folds_done_at) {
      c.folds_done(now);
      rise_at_baseline = rise_true;
      folds_done_at = NAN;
    }
    if (std::isnan(r.first_warning_h) && c.off_target(0.75f)) r.first_warning_h = now;

    if (busy == Request::None) {
      Request q = c.request();
      if (q == Request::DoseLevain) {
        busy = q;
        busy_until = now + p.levain_dosing_h;
      } else if (q == Request::MakeDough) {
        busy = q;
        busy_until = now + p.dough_steps_h;
      } else if (q == Request::Finish) {
        c.finished(now);
        r.ready_h = now;
        r.true_rise_at_finish = rise_true / rise_target;
        r.learned_activity = c.activity();
        break;
      }
    } else if (now >= busy_until) {
      if (busy == Request::DoseLevain) {
        c.levain_dosed(now);
      } else if (busy == Request::MakeDough) {
        c.dough_done(now);
        folds_done_at = now + p.fold_time_h;
      }
      busy = Request::None;
    }
  }
  r.error_h = r.ready_h - target_h;
  return r;
}

static void run_closed_loop(float target, float room, const Recipe &recipe, bool strict) {
  const float actives[] = {0.6f, 0.85f, 1.0f, 1.15f, 1.6f};
  std::printf("  closed loop, start 07:00, ready %s, room %.0f C, starter %.0f g %s:\n", clock(target), room,
              recipe.starter_g, recipe.cold_starter ? "cold" : "fed");
  std::printf("    activity | with sensor: error  rise  warned | model only: error  rise\n");
  for (float a : actives) {
    SimResult with = simulate(a, true, room, target, recipe);
    SimResult without = simulate(a, false, room, target, recipe);
    std::printf("    %8.2f |      %+6.2f h  %4.2f  %s | %+6.2f h  %4.2f   (plan late risk %.1f h)\n", a,
                with.error_h, with.true_rise_at_finish,
                std::isnan(with.first_warning_h) ? "  -  " : clock(with.first_warning_h), without.error_h,
                without.true_rise_at_finish, with.late_risk_h);
    CHECK(with.started, "start a=%.2f", a);
    CHECK(with.min_temp >= room - 0.01f, "never below room");
    CHECK(with.max_temp <= 29.3f, "never above 29 C (%.2f)", with.max_temp);
    // Quality: the dough is finished at the right rise. A very fast starter with a big
    // inoculum can overshoot a little, because the rise is only visible after the folds.
    bool typical = a >= 0.85f && a <= 1.15f;
    CHECK(with.true_rise_at_finish >= (typical ? 0.95f : 0.9f) &&
              with.true_rise_at_finish <= (typical ? 1.15f : 1.35f),
          "a=%.2f rise at finish %.2f", a, with.true_rise_at_finish);
    // Timing: a typical starter hits the target. Others are either on time, early (the user is
    // told when it is ready) or late with a warning well before the target.
    bool hit = std::fabs(with.error_h) <= (typical ? 0.65f : 0.5f);
    if (strict && typical) {
      CHECK(hit, "a=%.2f error %.2f h with sensor", a, with.error_h);
    } else {
      bool early = with.error_h < 0.0f;
      bool warned = !std::isnan(with.first_warning_h) && with.first_warning_h <= target - 1.5f;
      bool told_at_start = with.late_risk_h > 0.5f;  // "little margin" message when planning
      CHECK(hit || early || warned || told_at_start, "a=%.2f: late %.2f h without early warning (%.1f)", a, with.error_h,
            with.first_warning_h);
    }
  }
}

static void test_closed_loop() {
  ModelParams p;
  Recipe r;
  float earliest, latest;
  feasible_window(21.0f, 1.0f, r, p, &earliest, &latest);
  float mid = 7.0f + 0.5f * (earliest + std::min(latest, earliest + 8.0f));
  run_closed_loop(mid, 21.0f, r, true);
  run_closed_loop(7.0f + earliest + 0.3f, 21.0f, r, false);
  Recipe two = r;
  two.starter_g = 40.0f;
  run_closed_loop(17.0f, 21.0f, two, false);
}

static void test_learning_across_bakes() {
  ModelParams p;
  Recipe r;
  float earliest, latest;
  feasible_window(21.0f, 1.0f, r, p, &earliest, &latest);
  const float target = 7.0f + 0.5f * (earliest + std::min(latest, earliest + 8.0f));
  const float actives[] = {0.7f, 1.4f};
  std::printf("  learning the starter over four bakes, ready %s:\n", clock(target));
  for (float a : actives) {
    float history = NAN;
    std::printf("    activity %.2f:", a);
    SimResult last;
    for (int bake = 0; bake < 4; bake++) {
      float prior = std::isnan(history) ? 1.0f : history;
      // If the wish is no longer possible with this starter, the user takes the earliest + 30 min.
      float e2, l2, t = target;
      feasible_window(21.0f, prior, r, p, &e2, &l2);
      if (t < 7.0f + e2) t = 7.0f + e2 + 0.5f;
      last = simulate(a, true, 21.0f, t, r, prior);
      history = update_activity_history(history, last.learned_activity, p);
      std::printf("  bake %d error %+5.2f h rise %.2f (learned %.2f)", bake + 1, last.error_h, last.true_rise_at_finish,
                  last.learned_activity);
    }
    std::printf("\n");
    CHECK(std::fabs(last.error_h) <= 0.5f, "after learning a=%.2f error %.2f h", a, last.error_h);
    CHECK(last.true_rise_at_finish >= 0.95f && last.true_rise_at_finish <= 1.15f, "after learning rise %.2f",
          last.true_rise_at_finish);
  }
}

int main() {
  std::printf("planner tests\n");
  test_rate_table();
  test_model_matches_research_tables();
  test_plan_typical_day();
  test_plan_limits();
  test_activity_estimate();
  test_temp_to_finish();
  test_closed_loop();
  test_learning_across_bakes();
  if (failures == 0) {
    std::printf("ALL PASSED\n");
    return 0;
  }
  std::printf("%d FAILURE(S)\n", failures);
  return 1;
}

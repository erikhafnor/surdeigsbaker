// Fermentation planner for Surdeigsbaker v1.
//
// Pure C++ (no ESPHome dependencies) so it can be unit tested on the host:
//   g++ -std=gnu++17 -I firmware/v1/components/bakeplan
//       firmware/v1/components/bakeplan/planner.cpp firmware/v1/test/planner_test.cpp
//
// Model (see docs/forskning/v1-gjaeringsmodell.md):
//   * Fermentation speed r(T) relative to 24 °C comes from a table that blends the
//     Gänzle (1998) cardinal models for sourdough yeast and lactic acid bacteria with
//     baker data. It flattens out above ~27 °C.
//   * Work is counted in "reference doublings": one doubling takes k_ref_h hours at
//     24 °C and k_ref_h / r(T) hours at T.
//   * Levain to x2:  N_L = L + 1.6 * log2(D), D = levain mass / starter mass,
//                    L = 1.4 for a fridge-cold starter, 0.4 for a fed one.
//   * Bulk (from mixing the dough) to rise R:
//                    N_B = max(1.2, 3.3 + 1.6 * log2(20 / s) + log2(R / 30)),
//                    s = levain mass / main-dough flour in %.
//   * A starter "activity" factor a (1 = like the model) scales all speeds. It is
//     learned online from the measured rise.
//   * The machine can only heat, so temperatures are clamped to [room, t_max].
//   * The plan picks the levain dilution and one temperature for levain and bulk so
//     the temperature lands in the middle of what the machine can do. That leaves room
//     to speed up or slow down when the real starter differs from the model.

#pragma once

#include <cmath>
#include <string>

namespace surdeig {

constexpr int kMaxDilutions = 4;
constexpr int kRateTablePoints = 15;

struct ModelParams {
  // Reference doubling time at 24 °C (hours).
  float k_ref_h = 1.57f;
  // Speed r(T) relative to 24 °C, at 16, 17, ..., 30 °C.
  float rate_table[kRateTablePoints] = {0.40f, 0.45f, 0.50f, 0.565f, 0.643f, 0.727f, 0.818f, 0.908f,
                                        1.000f, 1.083f, 1.163f, 1.217f, 1.256f, 1.28f, 1.30f};
  float rate_table_t0_c = 16.0f;

  // Levain model.
  float levain_lag_cold = 1.4f;  // doublings of lag for a starter straight from the fridge
  float levain_lag_fed = 0.4f;   // ... for a starter fed the evening before
  float levain_slope = 1.6f;     // doublings per halving of the inoculum
  // Dilutions the machine may choose: D = levain mass / starter mass (equal flour and water).
  float dilutions[kMaxDilutions] = {3.5f, 6.0f, 11.0f, 0.0f};  // 1:1.25:1.25, 1:2.5:2.5, 1:5:5
  int num_dilutions = 3;
  // Allowed share of the total flour that goes through the levain (prefermented flour).
  float pff_min = 0.04f;
  float pff_max = 0.20f;
  float pff_pref = 0.10f;  // about the reference recipe

  // Bulk model.
  float bulk_base = 3.3f;
  float bulk_slope = 1.6f;
  float bulk_min_doublings = 1.2f;
  // Target bulk rise R (%) by bulk temperature: warmer dough is stopped earlier because it
  // keeps fermenting (The Sourdough Journey). Interpolated, then scaled by rise_scale.
  float rise_t[6] = {21.0f, 22.0f, 24.0f, 25.0f, 27.0f, 28.0f};
  float rise_r[6] = {75.0f, 65.0f, 50.0f, 40.0f, 30.0f, 28.0f};
  float rise_scale = 1.0f;

  // Fixed machine steps in real hours.
  float levain_dosing_h = 0.1f;  // weigh starter, dose and mix the levain
  float dough_steps_h = 1.1f;    // dose, mix, fermentolyse 40 min, salt, knead (inside the bulk clock)
  float fold_time_h = 1.17f;     // folds after kneading; the rise is measured after them
  float min_measured_h = 1.0f;   // the plan keeps at least this much measured bulk for feedback

  // Temperatures. The lower limit is normally the room: the machine slows fermentation
  // only by switching the heat off.
  float t_min_c = 16.0f;
  float t_max_c = 28.0f;         // bulk maximum (little gain above this)
  float t_max_levain_c = 29.0f;  // the levain may run a bit warmer to catch up
  float t_pref_c = 0.0f;         // 0 = middle of [max(t_min, room), t_max]

  // The levain feeding may be delayed (starter waits in the vessel) to reach late targets.
  float max_start_delay_h = 4.0f;

  float activity_min = 0.4f;
  float activity_max = 2.5f;
};

// The recipe quantities the plan needs.
struct Recipe {
  float starter_g = 20.0f;       // weighed by the machine
  float total_flour_g = 560.0f;  // all flour including the levain
  bool cold_starter = true;      // straight from the fridge
};

// Speed relative to 24 °C (interpolated table).
float speed_factor(float temp_c, const ModelParams &p);
// Inverse of speed_factor on the rising part of the table.
float temp_for_factor(float factor, const ModelParams &p);
// Temperature range the machine can hold in a room at room_c.
float lowest_temp(float room_c, const ModelParams &p);
float highest_temp(float room_c, const ModelParams &p);

// Target bulk rise (%) for a bulk temperature.
float bulk_rise_target(float temp_c, const ModelParams &p);

// Work in equivalent hours at 24 °C (activity 1).
float levain_eq_h(float dilution, bool cold_starter, const ModelParams &p);
float bulk_eq_h(float levain_g, float main_flour_g, float rise_pct, const ModelParams &p);

struct Plan {
  bool feasible = false;
  float dilution = 0.0f;        // D
  float temp_c = 0.0f;          // levain and bulk temperature
  float start_delay_h = 0.0f;   // wait before dosing the levain
  float levain_h = 0.0f;        // levain duration (real hours)
  float bulk_h = 0.0f;          // bulk duration incl. dough steps (real hours)
  float total_h = 0.0f;         // from now until ready for shaping
  float earliest_h = 0.0f;      // feasible window from now, for the UI
  float latest_h = 0.0f;
  float levain_flour_g = 0.0f;  // grams to dose onto the starter
  float levain_water_g = 0.0f;
  float pff = 0.0f;             // prefermented flour share
  float rise_target_pct = 0.0f;
  float levain_eq_h = 0.0f;
  float bulk_eq_h = 0.0f;
  // How late the bake would be with a starter 20 % slower than expected, even at maximum
  // temperature. Above ~0.5 h the user is told at start that the plan has little margin.
  float late_risk_h = 0.0f;
  std::string reason;           // short explanation (English, for logs)
};

// Total hours from now to ready for shaping for one choice.
float total_hours(float dilution, float temp_c, float delay_h, float activity, const Recipe &r,
                  const ModelParams &p);

// Shortest bulk the machine accepts: dough steps + folds + measured part.
inline float min_bulk_h(const ModelParams &p) { return p.dough_steps_h + p.fold_time_h + p.min_measured_h; }

// Earliest and latest reachable times (hours from now).
void feasible_window(float room_c, float activity, const Recipe &r, const ModelParams &p,
                     float *earliest_h, float *latest_h);

// Plan a bake that should be ready for shaping `available_h` hours from now.
Plan make_plan(float available_h, float room_c, float activity, const Recipe &r, const ModelParams &p);

// Tracks progress of one fermentation step in equivalent hours at 24 °C.
class StepTracker {
 public:
  void start(float target_eq_h);
  void advance(float dt_h, float temp_c, const ModelParams &p);
  float elapsed_eq_h() const { return elapsed_eq_h_; }
  float target_eq_h() const { return target_eq_h_; }
  float progress(float activity) const;
  float remaining_h(float temp_c, float activity, const ModelParams &p) const;

 private:
  float target_eq_h_ = 1.0f;
  float elapsed_eq_h_ = 0.0f;
};

// Shape of the measured rise within a step: rise_fraction = x^kRiseShape, x = model progress.
constexpr float kRiseShape = 1.5f;
// Below this measured rise fraction the activity estimate is too noisy to use.
constexpr float kMinRiseForActivity = 0.2f;

float activity_from_rise(float rise_fraction, float elapsed_eq_h, float target_eq_h, float prior,
                         const ModelParams &p);

// Activity from the bulk rise measured after the folds. The dough has risen
// R * x^kRiseShape overall (x = progress), but the sensor only sees the rise relative to
// the baseline taken at equivalent time e_f:  rel = (1 + R x^k) / (1 + R x_f^k) - 1,
// with x = e * a / need and x_f = e_f * a / need. Solved for a by bisection.
float activity_from_bulk_rise(float rel_rise, float e_h, float e_f_h, float need_eq_h, float rise_target,
                              float prior, const ModelParams &p);
// Relative rise after the baseline that corresponds to the overall target, for activity a.
float bulk_rel_target(float a, float e_f_h, float need_eq_h, float rise_target);
float blend_activity(float prior, float measured, float weight_measured, const ModelParams &p);

// The starter behaves much the same from bake to bake. After each bake the machine stores
// the learned activity and uses it as the prior next time (exponential moving average).
float update_activity_history(float history, float learned, const ModelParams &p, float weight_new = 0.5f);

// Temperature that makes `remaining_eq_h` fit in `hours_left`, clamped to [room, hi_c]
// (hi_c defaults to t_max_c). *eta_h receives the resulting real hours left.
float temp_to_finish_in(float remaining_eq_h, float hours_left, float room_c, const ModelParams &p,
                        float *eta_h, float hi_c = NAN);

// ---------------------------------------------------------------- closed-loop controller

enum class Stage { Idle, Delay, Levain, Dough, Bulk, Ready };

// What the controller wants the machine to do next. The machine performs the physical
// steps (dosing, mixing, kneading, folds) and reports back with levain_dosed(),
// dough_done() and folds_done(). The bulk clock starts when the dough is mixed
// (MakeDough). The bulk rise is measured from a new baseline after the last fold,
// because folding knocks some gas out of the dough.
enum class Request { None, DoseLevain, MakeDough, Finish };

struct Measurement {
  float room_c = NAN;   // room temperature
  float dough_c = NAN;  // dough (vessel wall) temperature, used to advance the model
  // Measured rise in % relative to the current baseline: the levain right after dosing, or
  // the dough right after the last fold. NaN if unknown.
  float rise_pct = NAN;
};

class Controller {
 public:
  explicit Controller(const ModelParams &p = ModelParams()) : p_(p) {}
  void set_params(const ModelParams &p) { p_ = p; }
  const ModelParams &params() const { return p_; }

  // Plan a bake that should be ready for shaping at target_h (absolute hours, same clock
  // as now_h). Returns false (and stays Idle) if the target cannot be reached; plan()
  // then holds the feasible window.
  bool start(float now_h, float target_h, float room_c, const Recipe &recipe, float activity_prior = 1.0f);
  void abort();

  // Call regularly (e.g. every minute).
  void tick(float now_h, const Measurement &m);

  // Events from the machine.
  void levain_dosed(float now_h);
  void dough_done(float now_h);
  void folds_done(float now_h);  // call right after dough_done() if there are no folds
  void finished(float now_h);

  Stage stage() const { return stage_; }
  Request request() const { return request_; }
  float setpoint_c() const { return setpoint_c_; }  // NaN = heat off
  float eta_h() const { return eta_h_; }            // absolute time ready for shaping
  float target_h() const { return target_h_; }
  float activity() const { return activity_; }
  const Plan &plan() const { return plan_; }
  bool off_target(float tolerance_h) const;
  bool measuring() const { return stage_ == Stage::Levain || (stage_ == Stage::Bulk && bulk_measured_); }
  // Target for the rise measured from the post-fold baseline (%), with the learned activity.
  // Smaller than the plan's overall target because part of the rise happened before the baseline.
  float measured_rise_target_pct() const;
  float levain_target_eq_h() const { return levain_tracker_.target_eq_h(); }
  float bulk_target_eq_h() const { return bulk_tracker_.target_eq_h(); }
  // Progress 0..1 of the current fermentation step (model with learned activity).
  float step_progress() const;

 private:
  void update_setpoint(float now_h);

  ModelParams p_;
  Stage stage_ = Stage::Idle;
  Request request_ = Request::None;
  Plan plan_;
  StepTracker levain_tracker_;
  StepTracker bulk_tracker_;
  float target_h_ = 0.0f;
  float start_h_ = 0.0f;
  float stage_start_h_ = 0.0f;
  float last_tick_h_ = NAN;
  float room_c_ = 20.0f;
  float activity_ = 1.0f;
  float setpoint_c_ = NAN;
  float eta_h_ = 0.0f;
  bool bulk_measured_ = false;
  float bulk_baseline_eq_h_ = 0.0f;  // bulk equivalent hours when the post-fold baseline was taken
};

}  // namespace surdeig

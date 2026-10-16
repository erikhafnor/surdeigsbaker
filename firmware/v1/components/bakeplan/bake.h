// One bake from start to "ready for shaping" (Surdeigsbaker v1).
//
// Bake ties the fermentation Controller (planner.h) to the work Sequence (sequence.h),
// turns the ToF distance into a rise in %, and keeps the user-facing state. The ESPHome
// component is a thin shell around it. Pure C++, tested in firmware/v1/test/bake_test.cpp.

#pragma once

#include <cmath>
#include <string>

#include "planner.h"
#include "sequence.h"

namespace surdeig {

// Inside of the bread pan, as a tapered rounded rectangle (mm). Defaults: Panasonic XL,
// see form: in hardware/spec/v1.yaml.
struct PanGeometry {
  float bottom_w = 167.0f, bottom_d = 127.0f;
  float top_w = 177.0f, top_d = 137.0f;
  float height = 148.5f;
  float corner_r = 26.5f;
  float area_mm2(float h) const;
  float volume_ml(float h) const;          // from the bottom up to height h
  float height_for_volume(float ml) const;
};

struct BakeConfig {
  ModelParams model;
  Recipe recipe;
  DoughRecipe dough;
  PanGeometry pan;
  float tof_to_bottom_mm = 186.0f;  // ToF reading with an empty pan (sensor window to the inside bottom)
  float dough_density = 1.05f;      // g/ml right after mixing
  float tick_s = 10.0f;             // how often the Controller is ticked
  float height_tau_s = 180.0f;      // smoothing of the ToF height (the surface is uneven, the sensor noisy)
  float motion_blank_s = 30.0f;     // ignore the ToF while the blade turns and this long after
  float min_starter_g = 5.0f;
  float max_starter_g = 200.0f;
};

enum class BakeState { Idle, Planned, Working, Fermenting, Ready, Failed };

class Bake {
 public:
  struct Inputs {
    float now_s = 0.0f;
    float weight_g = NAN;   // raw scale reading (the empty pan is not tared away)
    float tof_mm = NAN;
    float dough_c = NAN;
    float room_c = NAN;
    bool door_closed = true;
    bool estop_ok = true;
  };
  struct Outputs {
    MachineOut machine;
    float setpoint_c = NAN;  // NaN = heat off
    bool ready = false;      // dough is ready for shaping (alarm)
  };

  explicit Bake(const BakeConfig &c = BakeConfig()) : cfg_(c), ctl_(c.model) { seq_.set_recipe(c.dough); }
  BakeConfig &config() { return cfg_; }
  Sequence &sequence() { return seq_; }
  const Sequence &sequence() const { return seq_; }
  const Controller &controller() const { return ctl_; }

  // Weight of the empty pan in the holder (raw scale reading). Stored by the user once.
  void set_empty_pan(float raw_g) { empty_pan_g_ = raw_g; }
  float empty_pan() const { return empty_pan_g_; }

  // Start a bake that should be ready `hours_until_ready` from now. The starter is weighed:
  // the latest stable reading minus the empty pan. Without an empty-pan reference the
  // fallback starter weight is used. Returns false if the plan is not feasible; message()
  // then explains and plan() holds the window.
  bool start(float now_s, float hours_until_ready, bool cold_starter, float activity_prior,
             float fallback_starter_g = 20.0f);
  void abort();
  void confirm() { seq_.confirm(); }
  void shaped();  // the user took the dough out

  Outputs update(const Inputs &in);

  BakeState state() const { return state_; }
  const char *state_name() const;
  const Plan &plan() const { return ctl_.plan(); }
  float starter_g() const { return cfg_.recipe.starter_g; }
  float eta_hours(float now_s) const;     // hours from now until ready (NaN if idle)
  float rise_pct() const { return rise_pct_; }
  float dough_height_mm() const { return height_mm_; }
  float activity() const { return ctl_.activity(); }
  // The activity to keep for the next bake (valid once the bake is ready).
  float learned_activity() const { return learned_; }
  bool has_learned() const { return !std::isnan(learned_); }
  const std::string &message() const { return message_; }
  const char *status() const;
  std::string plan_summary() const;
  float stable_weight() const { return stable_w_; }

 private:
  float hours(float now_s) const { return now_s / 3600.0f; }
  void set_message(const std::string &m) { message_ = m; }

  BakeConfig cfg_;
  Controller ctl_;
  Sequence seq_;
  BakeState state_ = BakeState::Idle;
  float empty_pan_g_ = NAN;
  float stable_w_ = NAN;
  float last_room_c_ = NAN;
  WeightFilter wf_;
  float last_tick_s_ = -1e9f;
  float baseline_ml_ = NAN;
  float rise_pct_ = NAN;
  float height_mm_ = NAN;      // smoothed dough height
  float height_t_s_ = NAN;     // time of the last height sample
  float motion_until_s_ = -1e9f;
  float last_knead_ = 0.0f;
  float dough_g_ = 0.0f;
  float learned_ = NAN;
  bool levain_started_ = false;
  bool dough_started_ = false;
  bool bulk_measuring_ = false;
  std::string message_;
};

}  // namespace surdeig

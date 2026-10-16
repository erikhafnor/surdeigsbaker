// Dosing by weight for Surdeigsbaker v1 (flour screw, salt screw, water pump).
//
// Pure C++ (no ESPHome dependencies), unit tested on the host with
// firmware/v1/test/doser_test.cpp.
//
// Strategy (docs/forskning/v1-dosering.md, after OpenPowder and smart-grind-by-weight):
//   1. Tare when the scale is stable.
//   2. Coarse: run until net + flow * lag reaches coarse_fraction of the target.
//   3. Settle, then fine pulses sized from the learned flow (fine_gain of what is missing),
//      until the net weight is within tolerance. Flour cannot be taken out again, so the
//      doser always aims a little low.
//   4. If the weight does not rise while running, the screw is reversed briefly (bridge in
//      the hopper) and dosing continues. After max_recoveries the doser gives up: the
//      container is empty or blocked.
//
// The caller must keep the kneading motor, the fan and the heater off while a dose runs,
// so the readings are quiet.

#pragma once

#include <cmath>
#include <cstdint>

namespace surdeig {

struct DoseParams {
  float flow_guess_g_s = 3.0f;   // first guess of the flow (learned while running)
  float coarse_fraction = 0.92f;
  float lag_s = 0.35f;           // reading delay + afterflow: stop this much early
  float settle_s = 1.5f;         // wait after stopping before reading
  float stable_window_s = 1.0f;  // the scale is stable when the spread over this window ...
  float stable_sd_g = 0.15f;     // ... is below this standard deviation
  float tare_timeout_s = 20.0f;
  float tolerance_g = 0.8f;      // done when net >= target - tolerance
  float max_overshoot_g = 4.0f;  // more than this is reported
  float fine_gain = 0.6f;        // a fine pulse aims at this share of what is missing
  float min_pulse_s = 0.15f;
  float max_pulse_s = 4.0f;
  int max_fine_pulses = 40;
  float stall_s = 10.0f;         // running this long with less than stall_gain_g ...
  float stall_gain_g = 1.0f;     // ... means nothing comes out
  int max_recoveries = 3;
  float reverse_s = 1.0f;        // reverse the screw this long to break a bridge
  float timeout_s = 900.0f;
};

enum class DoseState : uint8_t { Idle, Taring, Coarse, Settling, Fine, Recovering, Done, Fault };

const char *dose_state_name(DoseState s);

// What the actuator should do right now.
struct DoseCommand {
  bool run = false;
  bool reverse = false;
};

// Rolling window of recent weight readings with a 3-point median on the input.
class WeightFilter {
 public:
  static constexpr int kMax = 64;
  void reset();
  void push(float t_s, float grams);
  float mean() const;
  float sd() const;
  float latest() const { return latest_; }
  bool stable(float window_s, float max_sd) const;
  float span_s() const;

 private:
  float t_[kMax] = {};
  float w_[kMax] = {};
  int n_ = 0;
  int head_ = 0;
  float raw_[3] = {NAN, NAN, NAN};
  int raw_n_ = 0;
  float latest_ = NAN;
  float window_s_ = 1.0f;
  friend class Doser;
};

class Doser {
 public:
  // Start a new dose. The flow learned in earlier doses of the same ingredient is kept
  // unless reset_flow is true.
  void start(float target_g, float now_s, const DoseParams &p, bool reset_flow = false);
  void abort();
  // Feed every new reading (any rate, 10 Hz is typical). Returns the actuator command.
  DoseCommand update(float now_s, float grams);

  DoseState state() const { return state_; }
  bool busy() const { return state_ != DoseState::Idle && state_ != DoseState::Done && state_ != DoseState::Fault; }
  bool done() const { return state_ == DoseState::Done; }
  bool failed() const { return state_ == DoseState::Fault; }
  float target_g() const { return target_g_; }
  float dosed_g() const { return net_g_; }        // last settled (or running) net weight
  float flow_g_s() const { return flow_g_s_; }
  bool overshoot() const { return net_g_ > target_g_ + p_.max_overshoot_g; }
  int recoveries() const { return recoveries_; }
  int fine_pulses() const { return fine_pulses_; }
  const char *fault() const { return fault_; }

 private:
  void enter(DoseState s, float now_s);
  void fail(const char *why, float now_s);
  bool start_recovery(float now_s, DoseCommand *cmd);

  DoseParams p_;
  WeightFilter f_;
  DoseState state_ = DoseState::Idle;
  float target_g_ = 0.0f;
  float tare_g_ = 0.0f;
  float net_g_ = 0.0f;
  float start_s_ = 0.0f;
  float state_s_ = 0.0f;
  float flow_g_s_ = NAN;
  float run_start_s_ = 0.0f;
  float run_start_net_ = 0.0f;
  float pulse_s_ = 0.0f;
  float pulse_start_net_ = 0.0f;
  float mark_s_ = 0.0f;     // stall detection: last time the weight rose by stall_gain_g
  float mark_net_ = 0.0f;
  int recoveries_ = 0;
  int fine_pulses_ = 0;
  int no_gain_pulses_ = 0;
  bool after_pulse_ = false;
  const char *fault_ = "";
};

}  // namespace surdeig

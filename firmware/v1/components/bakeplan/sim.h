// Simulated Surdeigsbaker v1 for host tests and the ESPHome simulation build.
//
// The plant: dosing actuators with a flow and material in flight, flaps that must be open,
// stocks that can run out, a noisy scale (much noisier while the blade turns), the dough
// temperature following the heat with a lag, and the dough rising with a "true" starter
// activity that the controller does not know.

#pragma once

#include <cmath>
#include <cstdint>
#include <deque>

#include "bake.h"

namespace surdeig {

struct SimParams {
  float activity = 1.0f;       // true starter activity relative to the model
  float room_c = 21.0f;
  float tau_h = 0.6f;          // dough temperature lag
  float flow_g_s[kIngredients] = {6.7f, 3.0f, 0.5f};
  float in_flight_s = 0.3f;
  float noise_g = 0.05f;
  float motor_noise_g = 3.0f;  // scale noise while the blade turns
  float tare_g = 2600.0f;      // platform, holder, motor and pan on the load cell
  float starter_g = 20.0f;
  float tof_noise_mm = 1.0f;
  float stock_g[kIngredients] = {1000.0f, 1500.0f, 400.0f};
  uint32_t seed = 7;
};

class SimMachine {
 public:
  SimMachine(const SimParams &p, const BakeConfig &c);
  // Advance by dt with the machine outputs and the controller's view of the stage.
  void step(float now_s, float dt_s, const MachineOut &out, float setpoint_c, Stage stage, const Plan &plan);

  float weight_g();
  float tof_mm();
  float dough_c() const { return dough_c_; }
  float room_c() const { return p_.room_c; }
  void refill(Ingredient i, float g) { p_.stock_g[int(i)] += g; }

  // Truth for the tests.
  float added_g(Ingredient i) const { return added_[int(i)]; }
  float true_rise_fraction() const;  // overall bulk rise / planned target (1 = on target)
  int dose_while_kneading() const { return dose_while_kneading_; }
  int dose_with_closed_flap() const { return dose_closed_flap_; }
  float knead_seconds() const { return knead_s_; }
  float empty_pan_g() const { return p_.tare_g; }

 private:
  float uniform();
  float gauss();

  SimParams p_;
  BakeConfig c_;
  uint64_t rng_;
  float dough_c_;
  float added_[kIngredients] = {0, 0, 0};
  std::deque<std::pair<float, float>> falling_[kIngredients];
  float knead_ = 0.0f;
  float knead_s_ = 0.0f;
  int dose_while_kneading_ = 0;
  int dose_closed_flap_ = 0;
  bool bulk_ = false;
  float bulk_eq_ = 0.0f;  // true equivalent hours of bulk at 24 °C (activity 1)
  float need_eq_ = 1.0f;
  float rise_target_ = 0.5f;
  float last_now_s_ = 0.0f;
};

}  // namespace surdeig

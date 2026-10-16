#include "sim.h"

#include <algorithm>

namespace surdeig {

SimMachine::SimMachine(const SimParams &p, const BakeConfig &c) : p_(p), c_(c), rng_(p.seed * 2654435761u + 1) {
  dough_c_ = p.room_c;
}

float SimMachine::uniform() {
  rng_ = rng_ * 6364136223846793005ULL + 1442695040888963407ULL;
  return float((rng_ >> 40) & 0xFFFFFF) / float(0x1000000);
}

float SimMachine::gauss() {
  float u1 = std::max(1e-6f, uniform()), u2 = uniform();
  return std::sqrt(-2.0f * std::log(u1)) * std::cos(6.2831853f * u2);
}

void SimMachine::step(float now_s, float dt_s, const MachineOut &out, float setpoint_c, Stage stage,
                      const Plan &plan) {
  last_now_s_ = now_s;
  knead_ = out.knead;
  if (std::fabs(out.knead) > 0.01f) knead_s_ += dt_s;

  // Dosing.
  const int i = int(out.dose_ing);
  if (out.dose_run && !out.dose_reverse) {
    if (std::fabs(out.knead) > 0.01f) dose_while_kneading_++;
    bool open = out.dose_ing == Ingredient::Water || (out.dose_ing == Ingredient::Flour && out.flap_flour_open) ||
                (out.dose_ing == Ingredient::Salt && out.flap_salt_open);
    if (!open) {
      dose_closed_flap_++;
    } else if (p_.stock_g[i] > 0.0f) {
      float q = p_.flow_g_s[i] * (1.0f + 0.1f * gauss());
      float g = std::min(p_.stock_g[i], std::max(0.0f, q) * dt_s);
      p_.stock_g[i] -= g;
      falling_[i].emplace_back(now_s + p_.in_flight_s, g);
    }
  }
  for (auto &f : falling_)
    while (!f.empty() && f.front().first <= now_s) {
      added_[&f - falling_] += f.front().second;
      f.pop_front();
    }

  // Dough temperature: heat if there is a setpoint, never below the room.
  const float target = (std::isnan(setpoint_c) || out.quiet) ? p_.room_c : std::max(p_.room_c, setpoint_c);
  dough_c_ += (target - dough_c_) * std::min(1.0f, dt_s / 3600.0f / p_.tau_h);

  // Fermentation truth. The bulk clock starts when the controller starts the dough stage.
  if (!bulk_ && (stage == Stage::Dough || stage == Stage::Bulk)) {
    bulk_ = true;
    bulk_eq_ = 0.0f;
    need_eq_ = std::max(0.1f, plan.bulk_eq_h);
    rise_target_ = plan.rise_target_pct / 100.0f;
  }
  if (bulk_) bulk_eq_ += dt_s / 3600.0f * speed_factor(dough_c_, c_.model) * p_.activity;
}

float SimMachine::true_rise_fraction() const {
  if (!bulk_) return 0.0f;
  return std::pow(std::max(0.0f, bulk_eq_ / need_eq_), kRiseShape);
}

float SimMachine::weight_g() {
  float noise = std::fabs(knead_) > 0.01f ? p_.motor_noise_g : p_.noise_g;
  return p_.tare_g + p_.starter_g + added_[0] + added_[1] + added_[2] + noise * gauss();
}

float SimMachine::tof_mm() {
  const float mass = p_.starter_g + added_[0] + added_[1] + added_[2];
  float ml = mass / c_.dough_density;
  if (bulk_) ml *= 1.0f + rise_target_ * true_rise_fraction();
  const float h = c_.pan.height_for_volume(ml);
  float noise = p_.tof_noise_mm * gauss();
  if (std::fabs(knead_) > 0.01f) noise *= 10.0f;
  return c_.tof_to_bottom_mm - h + noise;
}

}  // namespace surdeig

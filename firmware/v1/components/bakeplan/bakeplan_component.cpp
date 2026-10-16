#include "bakeplan_component.h"

#include <cmath>

#include "esphome/core/hal.h"
#include "esphome/core/helpers.h"
#include "esphome/core/log.h"

namespace esphome {
namespace bakeplan {

static const char *const TAG = "bakeplan";
static const float kSimStepS = 0.2f;  // simulation sub-step (the doser needs short steps)

void BakeplanComponent::set_recipe(float total_flour_g, float hydration, float salt_frac) {
  cfg_.recipe.total_flour_g = total_flour_g;
  cfg_.dough.hydration = hydration;
  cfg_.dough.salt_frac = salt_frac;
}

void BakeplanComponent::set_simulation(float time_scale, float activity) {
  simulate_ = true;
  time_scale_ = time_scale;
  sim_activity_ = activity;
}

void BakeplanComponent::setup() {
  pref_ = global_preferences->make_preference<Persist>(fnv1_hash("surdeigsbaker_bakeplan_v1"));
  if (!pref_.load(&persist_)) persist_ = Persist();
  if (std::isnan(persist_.activity) || persist_.activity < 0.3f || persist_.activity > 3.0f) persist_.activity = 1.0f;
  bake_ = Bake(cfg_);
  if (simulate_) {
    ::surdeig::SimParams sp;
    sp.activity = sim_activity_;
    sim_ = std::unique_ptr<::surdeig::SimMachine>(new ::surdeig::SimMachine(sp, cfg_));
    persist_.empty_pan = sim_->empty_pan_g();
  }
  bake_.set_empty_pan(persist_.empty_pan);
  last_ms_ = millis();
}

void BakeplanComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "Surdeigsbaker bake program:");
  ESP_LOGCONFIG(TAG, "  Flour %.0f g, hydration %.0f %%, salt %.1f %%", cfg_.recipe.total_flour_g,
                cfg_.dough.hydration * 100.0f, cfg_.dough.salt_frac * 100.0f);
  ESP_LOGCONFIG(TAG, "  ToF to the bottom of the pan: %.0f mm", cfg_.tof_to_bottom_mm);
  ESP_LOGCONFIG(TAG, "  Starter activity from earlier bakes: %.2f (%u bakes)", persist_.activity,
                (unsigned) persist_.bakes);
  if (std::isnan(persist_.empty_pan)) {
    ESP_LOGCONFIG(TAG, "  Empty pan: not stored (press 'Lagre tom form')");
  } else {
    ESP_LOGCONFIG(TAG, "  Empty pan: %.1f g (raw)", persist_.empty_pan);
  }
  if (sim_) ESP_LOGCONFIG(TAG, "  SIMULATION: time x%.0f, starter activity %.2f", time_scale_, sim_activity_);
}

static float state_or_nan(sensor::Sensor *s) { return (s != nullptr && s->has_state()) ? s->state : NAN; }

Bake::Inputs BakeplanComponent::read_inputs() {
  Bake::Inputs in;
  in.now_s = now_s_;
  in.weight_g = state_or_nan(weight_);
  in.tof_mm = state_or_nan(distance_);
  in.dough_c = state_or_nan(dough_t_);
  in.room_c = state_or_nan(room_t_);
  in.door_closed = door_ == nullptr || (door_->has_state() && door_->state);
  in.estop_ok = estop_ == nullptr || (estop_->has_state() && estop_->state);
  return in;
}

void BakeplanComponent::loop() {
  const uint32_t ms = millis();
  const uint32_t dms = ms - last_ms_;
  if (dms < 100) return;  // 10 Hz is enough (the scale gives 10 readings per second)
  last_ms_ = ms;

  if (!sim_) {
    now_acc_s_ += dms / 1000.0;
    now_s_ = float(now_acc_s_);
    last_ = bake_.update(read_inputs());
  } else {
    // Simulation: run the machine model in short sub-steps, publish the end state.
    double target = now_acc_s_ + dms / 1000.0 * time_scale_;
    while (now_acc_s_ < target) {
      now_acc_s_ += kSimStepS;
      now_s_ = float(now_acc_s_);
      const float sp = last_.machine.quiet ? NAN : last_.setpoint_c;
      sim_->step(now_s_, kSimStepS, last_.machine, sp, bake_.controller().stage(), bake_.plan());
      Bake::Inputs in;
      in.now_s = now_s_;
      in.weight_g = sim_->weight_g();
      in.tof_mm = sim_->tof_mm();
      in.dough_c = sim_->dough_c();
      in.room_c = sim_->room_c();
      last_ = bake_.update(in);
      if (last_.ready) break;
    }
  }
  publish(last_);
}

void BakeplanComponent::publish(const Bake::Outputs &o) {
  const MachineOut &m = o.machine;
  const bool all = first_publish_;
  first_publish_ = false;
  if (all || m.knead != last_out_.knead) knead_cb_.call(m.knead);
  if (all || m.dose_ing != last_out_.dose_ing || m.dose_run != last_out_.dose_run ||
      m.dose_reverse != last_out_.dose_reverse) {
    if (!all && m.dose_ing != last_out_.dose_ing && last_out_.dose_run)
      dose_cb_.call(::surdeig::ingredient_name(last_out_.dose_ing), false, false);
    dose_cb_.call(::surdeig::ingredient_name(m.dose_ing), m.dose_run, m.dose_reverse);
  }
  if (all || m.flap_flour_open != last_out_.flap_flour_open) flap_cb_.call("mel", m.flap_flour_open);
  if (all || m.flap_salt_open != last_out_.flap_salt_open) flap_cb_.call("salt", m.flap_salt_open);
  if (all || m.quiet != last_out_.quiet) quiet_cb_.call(m.quiet);
  const bool sp_changed = std::isnan(o.setpoint_c) != std::isnan(last_sp_) ||
                          (!std::isnan(o.setpoint_c) && std::fabs(o.setpoint_c - last_sp_) >= 0.05f);
  if (all || sp_changed) {
    last_sp_ = o.setpoint_c;
    setpoint_cb_.call(o.setpoint_c);
  }
  last_out_ = m;

  if (bake_.message() != last_message_) {
    last_message_ = bake_.message();
    ESP_LOGI(TAG, "%s", last_message_.c_str());
    message_cb_.call(last_message_);
  }
  const std::string st = bake_.status();
  if (st != last_status_) {
    last_status_ = st;
    if (sim_) {
      ESP_LOGI(TAG, "[%5.2f h] %s", now_s_ / 3600.0f, st.c_str());
    } else {
      ESP_LOGI(TAG, "%s", st.c_str());
    }
    status_cb_.call(st);
  }
  if (o.ready && !ready_sent_) {
    ready_sent_ = true;
    if (bake_.has_learned()) {
      persist_.activity = ::surdeig::update_activity_history(persist_.activity, bake_.learned_activity(),
                                                              bake_.controller().params());
      persist_.bakes++;
      save();
    }
    ESP_LOGI(TAG, "Ready for shaping. Learned starter activity %.2f, kept for next time: %.2f",
             bake_.learned_activity(), persist_.activity);
    ready_cb_.call();
  }
}

void BakeplanComponent::save() {
  if (!pref_.save(&persist_)) ESP_LOGW(TAG, "Could not save the learned values");
}

void BakeplanComponent::start(float hours, bool cold_starter) {
  if (running()) {
    ESP_LOGW(TAG, "A bake is already running");
    return;
  }
  ready_sent_ = false;
  if (sim_) {  // let the simulated scale settle before weighing the starter
    for (int i = 0; i < 30; i++) {
      now_acc_s_ += kSimStepS;
      now_s_ = float(now_acc_s_);
      Bake::Inputs in;
      in.now_s = now_s_;
      in.weight_g = sim_->weight_g();
      in.room_c = sim_->room_c();
      bake_.update(in);
    }
  }
  bool ok = bake_.start(now_s_, hours, cold_starter, persist_.activity);
  ESP_LOGI(TAG, "Start (%.1f h, %s starter, %.0f g): %s", hours, cold_starter ? "cold" : "fed", bake_.starter_g(),
           ok ? "planned" : "not possible");
  if (ok) ESP_LOGI(TAG, "%s", bake_.plan_summary().c_str());
  publish(last_);
}

void BakeplanComponent::abort() {
  bake_.abort();
  last_ = Bake::Outputs();
  publish(last_);
}

void BakeplanComponent::confirm() { bake_.confirm(); }

void BakeplanComponent::shaped() {
  bake_.shaped();
  publish(last_);
}

void BakeplanComponent::store_empty_pan() {
  const float w = sim_ ? sim_->empty_pan_g() : bake_.stable_weight();
  if (std::isnan(w)) {
    ESP_LOGW(TAG, "The scale is not stable, empty pan not stored");
    return;
  }
  persist_.empty_pan = w;
  bake_.set_empty_pan(w);
  save();
  ESP_LOGI(TAG, "Empty pan stored: %.1f g (raw)", w);
}

bool BakeplanComponent::running() const {
  const BakeState s = bake_.state();
  return s == BakeState::Planned || s == BakeState::Working || s == BakeState::Fermenting;
}

float BakeplanComponent::net_weight_g() const {
  const float w = bake_.stable_weight();
  if (std::isnan(w) || std::isnan(persist_.empty_pan)) return NAN;
  return w - persist_.empty_pan;
}

}  // namespace bakeplan
}  // namespace esphome

#pragma once

#include <memory>
#include <string>
#include <utility>

#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/core/automation.h"
#include "esphome/core/component.h"
#include "esphome/core/preferences.h"

#include "bake.h"
#include "sim.h"

namespace esphome {
namespace bakeplan {

using ::surdeig::Bake;
using ::surdeig::BakeConfig;
using ::surdeig::BakeState;
using ::surdeig::Ingredient;
using ::surdeig::MachineOut;

class BakeplanComponent : public Component {
 public:
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::LATE; }

  void set_weight_sensor(sensor::Sensor *s) { weight_ = s; }
  void set_distance_sensor(sensor::Sensor *s) { distance_ = s; }
  void set_dough_temperature_sensor(sensor::Sensor *s) { dough_t_ = s; }
  void set_room_temperature_sensor(sensor::Sensor *s) { room_t_ = s; }
  void set_door_sensor(binary_sensor::BinarySensor *s) { door_ = s; }
  void set_emergency_stop_sensor(binary_sensor::BinarySensor *s) { estop_ = s; }
  void set_tof_to_bottom(float mm) { cfg_.tof_to_bottom_mm = mm; }
  void set_recipe(float total_flour_g, float hydration, float salt_frac);
  void set_simulation(float time_scale, float activity);

  template<typename F> void add_on_knead_callback(F &&cb) { knead_cb_.add(std::forward<F>(cb)); }
  template<typename F> void add_on_dose_callback(F &&cb) { dose_cb_.add(std::forward<F>(cb)); }
  template<typename F> void add_on_flap_callback(F &&cb) { flap_cb_.add(std::forward<F>(cb)); }
  template<typename F> void add_on_setpoint_callback(F &&cb) { setpoint_cb_.add(std::forward<F>(cb)); }
  template<typename F> void add_on_quiet_callback(F &&cb) { quiet_cb_.add(std::forward<F>(cb)); }
  template<typename F> void add_on_message_callback(F &&cb) { message_cb_.add(std::forward<F>(cb)); }
  template<typename F> void add_on_status_callback(F &&cb) { status_cb_.add(std::forward<F>(cb)); }
  template<typename F> void add_on_ready_callback(F &&cb) { ready_cb_.add(std::forward<F>(cb)); }

  // Actions.
  void start(float hours, bool cold_starter);
  void abort();
  void confirm();
  void shaped();
  void store_empty_pan();

  // For lambdas in YAML (display, template sensors).
  bool running() const;
  std::string status() const { return bake_.status(); }
  std::string state_name() const { return bake_.state_name(); }
  std::string message() const { return bake_.message(); }
  std::string plan_summary() const { return bake_.plan_summary(); }
  float eta_hours() const { return bake_.eta_hours(now_s_); }
  float rise_pct() const { return bake_.rise_pct(); }
  float dough_height_mm() const { return bake_.dough_height_mm(); }
  float activity() const { return bake_.activity(); }
  float activity_history() const { return persist_.activity; }
  float starter_g() const { return bake_.starter_g(); }
  float net_weight_g() const;
  float dosed_g(int ingredient) const { return bake_.sequence().dosed_g(Ingredient(ingredient)); }
  float setpoint_c() const { return last_.setpoint_c; }
  bool quiet() const { return last_out_.quiet; }
  bool waiting_for_confirm() const { return bake_.sequence().waiting_for_confirm(); }
  int bakes() const { return persist_.bakes; }
  bool simulated() const { return sim_ != nullptr; }
  float sim_hours() const { return now_s_ / 3600.0f; }

 protected:
  struct Persist {
    float activity = 1.0f;     // learned starter activity (moving average over bakes)
    float empty_pan = NAN;     // raw scale reading with the empty pan in place
    uint32_t bakes = 0;
  };

  void publish(const Bake::Outputs &o);
  void save();
  Bake::Inputs read_inputs();

  BakeConfig cfg_;
  Bake bake_;
  Persist persist_;
  ESPPreferenceObject pref_;
  sensor::Sensor *weight_{nullptr};
  sensor::Sensor *distance_{nullptr};
  sensor::Sensor *dough_t_{nullptr};
  sensor::Sensor *room_t_{nullptr};
  binary_sensor::BinarySensor *door_{nullptr};
  binary_sensor::BinarySensor *estop_{nullptr};

  std::unique_ptr<::surdeig::SimMachine> sim_;
  bool simulate_{false};
  float time_scale_{1.0f};
  float sim_activity_{1.0f};

  double now_acc_s_{0.0};
  uint32_t last_ms_{0};
  float now_s_{0.0f};
  Bake::Outputs last_;
  MachineOut last_out_;
  bool first_publish_{true};
  bool ready_sent_{false};
  float last_sp_{-1000.0f};
  std::string last_message_;
  std::string last_status_;

  CallbackManager<void(float)> knead_cb_;
  CallbackManager<void(std::string, bool, bool)> dose_cb_;
  CallbackManager<void(std::string, bool)> flap_cb_;
  CallbackManager<void(float)> setpoint_cb_;
  CallbackManager<void(bool)> quiet_cb_;
  CallbackManager<void(std::string)> message_cb_;
  CallbackManager<void(std::string)> status_cb_;
  CallbackManager<void()> ready_cb_;
};

template<typename... Ts> class StartAction : public Action<Ts...> {
 public:
  explicit StartAction(BakeplanComponent *parent) : parent_(parent) {}
  TEMPLATABLE_VALUE(float, hours)
  TEMPLATABLE_VALUE(bool, cold_starter)
  void play(const Ts &...x) override { this->parent_->start(this->hours_.value(x...), this->cold_starter_.value(x...)); }

 protected:
  BakeplanComponent *parent_;
};

template<typename... Ts> class AbortAction : public Action<Ts...> {
 public:
  explicit AbortAction(BakeplanComponent *parent) : parent_(parent) {}
  void play(const Ts &...x) override { this->parent_->abort(); }

 protected:
  BakeplanComponent *parent_;
};

template<typename... Ts> class ConfirmAction : public Action<Ts...> {
 public:
  explicit ConfirmAction(BakeplanComponent *parent) : parent_(parent) {}
  void play(const Ts &...x) override { this->parent_->confirm(); }

 protected:
  BakeplanComponent *parent_;
};

template<typename... Ts> class ShapedAction : public Action<Ts...> {
 public:
  explicit ShapedAction(BakeplanComponent *parent) : parent_(parent) {}
  void play(const Ts &...x) override { this->parent_->shaped(); }

 protected:
  BakeplanComponent *parent_;
};

template<typename... Ts> class StoreEmptyPanAction : public Action<Ts...> {
 public:
  explicit StoreEmptyPanAction(BakeplanComponent *parent) : parent_(parent) {}
  void play(const Ts &...x) override { this->parent_->store_empty_pan(); }

 protected:
  BakeplanComponent *parent_;
};

}  // namespace bakeplan
}  // namespace esphome

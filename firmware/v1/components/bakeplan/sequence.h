// Step sequence for the physical work of a bake (Surdeigsbaker v1).
//
// The fermentation Controller (planner.h) decides *when* to build the levain and the dough.
// The Sequence does the work: dosing by weight, mixing, the fermentolyse rest, salt and
// brine water, kneading and the folds. It reports back with events that the caller passes
// on to the Controller (levain_dosed, dough_done, folds_done).
//
// Pure C++ (no ESPHome). Tested with firmware/v1/test/sequence_test.cpp.

#pragma once

#include <cmath>
#include <cstdint>
#include <vector>

#include "doser.h"
#include "planner.h"

namespace surdeig {

enum class Ingredient : uint8_t { Water = 0, Flour = 1, Salt = 2 };
constexpr int kIngredients = 3;
const char *ingredient_name(Ingredient i);  // Norwegian: "vann", "mel", "salt"

// Recipe ratios that are not part of the fermentation plan.
struct DoughRecipe {
  float hydration = 0.77f;            // all water / all flour (incl. starter and levain)
  float salt_frac = 0.02f;            // salt / all flour
  float brine_water_per_salt = 4.0f;  // water dosed onto the salt (12 g salt + 48 g water)
  float starter_hydration = 1.0f;     // water / flour in the starter
  int flour_portions = 3;             // the main flour is dosed in portions with mixing between
};

struct LevainAmounts {
  float water_g = 0.0f;
  float flour_g = 0.0f;
};

struct DoughAmounts {
  float water_g = 0.0f;        // main water (before the flour)
  float flour_g = 0.0f;        // main flour
  float salt_g = 0.0f;
  float brine_water_g = 0.0f;  // water dosed onto the salt after the fermentolyse
};

LevainAmounts levain_amounts(const Plan &plan);
DoughAmounts dough_amounts(const Recipe &r, const Plan &plan, const DoughRecipe &d);

// Motor speeds are fractions of full PWM (direction by sign).
struct KneadParams {
  float mix_speed = 0.35f;        // about 100 rpm at the blade
  float knead_speed = 0.75f;      // about 200 rpm
  float fold_speed = 0.30f;
  float levain_mix_s = 60.0f;
  float mix_after_water_s = 10.0f;
  float mix_per_portion_s = 20.0f;
  float combine_s = 240.0f;       // slow mixing after the last flour
  float fermentolyse_s = 2400.0f;  // 40 min rest before salt
  float salt_mix_s = 180.0f;      // slow mixing after salt and brine water
  float knead_s = 480.0f;         // 8 min
  int folds = 3;
  float first_fold_s = 600.0f;    // after kneading
  float fold_interval_s = 1800.0f;
  int fold_strokes = 4;
  float fold_on_s = 1.2f;
  float fold_off_s = 2.0f;
  float baseline_wait_s = 300.0f;  // after the last fold, before the rise baseline (lets the ToF settle)
  float flap_s = 0.6f;            // time for a flap to open or close
  float pump_back_s = 1.5f;       // pump runs backwards after water to empty the nozzle
  float quiet_before_s = 2.0f;    // motor, fan and heater off before a dose starts
};

enum class StepKind : uint8_t { Dose, Mix, Rest, Fold, Event };
enum class Event : uint8_t { None, LevainDosed, DoughDone, FoldsDone };

struct Step {
  StepKind kind = StepKind::Rest;
  Ingredient ing = Ingredient::Water;
  float grams = 0.0f;
  float speed = 0.0f;
  float duration_s = 0.0f;
  float on_s = 0.0f;   // pulse pattern for mixing (0 = continuous)
  float off_s = 0.0f;
  bool alternate = false;
  int strokes = 0;
  Event event = Event::None;
  const char *label = "";
};

struct MachineIn {
  float now_s = 0.0f;
  float weight_g = NAN;   // raw scale reading (any offset)
  bool door_closed = true;
  bool estop_ok = true;
};

struct MachineOut {
  Ingredient dose_ing = Ingredient::Water;
  bool dose_run = false;
  bool dose_reverse = false;
  bool flap_flour_open = false;
  bool flap_salt_open = false;
  float knead = 0.0f;  // -1 .. 1
  bool quiet = false;  // weighing: keep the heater, the fan and the motor off
};

class Sequence {
 public:
  Sequence();
  void set_dose_params(Ingredient i, const DoseParams &p) { dp_[int(i)] = p; }
  const DoseParams &dose_params(Ingredient i) const { return dp_[int(i)]; }
  void set_knead_params(const KneadParams &k) { kp_ = k; }
  const KneadParams &knead_params() const { return kp_; }
  void set_recipe(const DoughRecipe &d) { recipe_ = d; }

  void start_levain(const LevainAmounts &a, float now_s);
  void start_dough(const DoughAmounts &a, float now_s);
  void abort();
  // Resume after the door was opened during motion, or retry after a dosing fault.
  void confirm();

  MachineOut update(const MachineIn &in);
  Event take_event();

  bool busy() const { return idx_ < steps_.size(); }
  bool faulted() const { return fault_[0] != 0; }
  const char *fault() const { return fault_; }
  bool waiting_for_confirm() const { return wait_confirm_; }
  const char *status() const { return status_; }
  int step_index() const { return int(idx_); }
  int step_count() const { return int(steps_.size()); }
  float dosed_g(Ingredient i) const { return dosed_[int(i)]; }
  float planned_g(Ingredient i) const { return planned_[int(i)]; }
  const Doser &doser(Ingredient i) const { return doser_[int(i)]; }

 private:
  enum class DosePhase : uint8_t { Quiet, Opening, Dosing, Closing, PumpBack };
  void begin(float now_s);
  void next(float now_s);
  void adjust_salt_step(Step &s);
  bool motion(const Step &s) const;
  MachineOut run_dose(Step &s, const MachineIn &in);
  void bank_dose(const Step &s, float grams);
  MachineOut run_pattern(const Step &s, float t);

  DoseParams dp_[kIngredients];
  KneadParams kp_;
  DoughRecipe recipe_;
  Doser doser_[kIngredients];
  std::vector<Step> steps_;
  size_t idx_ = 0;
  float step_start_s_ = 0.0f;  // start of the step (shifted forward while paused)
  float paused_at_s_ = NAN;
  bool wait_confirm_ = false;
  DosePhase dose_phase_ = DosePhase::Quiet;
  float phase_start_s_ = 0.0f;
  float dose_remaining_g_ = 0.0f;
  float step_dosed_ = 0.0f;   // grams dosed so far in the current dose step
  float dosed_[kIngredients] = {0, 0, 0};
  float planned_[kIngredients] = {0, 0, 0};
  float flour_planned_main_ = 0.0f;
  float water_planned_main_ = 0.0f;
  float flour_dosed_main_ = 0.0f;
  float water_dosed_main_ = 0.0f;
  Event pending_ = Event::None;
  const char *fault_ = "";
  const char *status_ = "Klar";
  float last_now_s_ = 0.0f;
};

}  // namespace surdeig

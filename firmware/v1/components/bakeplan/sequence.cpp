#include "sequence.h"

#include <algorithm>
#include <string>

namespace surdeig {

const char *ingredient_name(Ingredient i) {
  switch (i) {
    case Ingredient::Water: return "vann";
    case Ingredient::Flour: return "mel";
    case Ingredient::Salt: return "salt";
  }
  return "?";
}

LevainAmounts levain_amounts(const Plan &plan) {
  LevainAmounts a;
  a.water_g = plan.levain_water_g;
  a.flour_g = plan.levain_flour_g;
  return a;
}

DoughAmounts dough_amounts(const Recipe &r, const Plan &plan, const DoughRecipe &d) {
  DoughAmounts a;
  const float starter_flour = r.starter_g / (1.0f + d.starter_hydration);
  const float starter_water = r.starter_g - starter_flour;
  const float total_water = d.hydration * r.total_flour_g;
  a.salt_g = d.salt_frac * r.total_flour_g;
  a.brine_water_g = d.brine_water_per_salt * a.salt_g;
  a.flour_g = std::max(0.0f, r.total_flour_g - starter_flour - plan.levain_flour_g);
  a.water_g = std::max(0.0f, total_water - starter_water - plan.levain_water_g - a.brine_water_g);
  return a;
}

// ---------------------------------------------------------------- building the steps

static Step dose(Ingredient i, float g, const char *label) {
  Step s;
  s.kind = StepKind::Dose;
  s.ing = i;
  s.grams = g;
  s.label = label;
  return s;
}

static Step mix(float speed, float duration_s, float on_s, float off_s, bool alternate, const char *label) {
  Step s;
  s.kind = StepKind::Mix;
  s.speed = speed;
  s.duration_s = duration_s;
  s.on_s = on_s;
  s.off_s = off_s;
  s.alternate = alternate;
  s.label = label;
  return s;
}

static Step rest(float duration_s, const char *label) {
  Step s;
  s.kind = StepKind::Rest;
  s.duration_s = duration_s;
  s.label = label;
  return s;
}

static Step fold(float speed, int strokes, float on_s, float off_s, const char *label) {
  Step s;
  s.kind = StepKind::Fold;
  s.speed = speed;
  s.strokes = strokes;
  s.on_s = on_s;
  s.off_s = off_s;
  s.duration_s = strokes * (on_s + off_s);
  s.alternate = true;
  s.label = label;
  return s;
}

static Step event(Event e) {
  Step s;
  s.kind = StepKind::Event;
  s.event = e;
  return s;
}

Sequence::Sequence() {
  DoseParams w, f, s;
  w.flow_guess_g_s = 6.5f;
  w.lag_s = 0.4f;
  w.reverse_s = 1.5f;
  w.stall_s = 6.0f;
  f.flow_guess_g_s = 3.0f;
  s.flow_guess_g_s = 0.6f;
  s.tolerance_g = 0.3f;
  s.stall_gain_g = 0.3f;
  s.max_pulse_s = 3.0f;
  dp_[int(Ingredient::Water)] = w;
  dp_[int(Ingredient::Flour)] = f;
  dp_[int(Ingredient::Salt)] = s;
}

void Sequence::start_levain(const LevainAmounts &a, float now_s) {
  steps_.clear();
  steps_.push_back(dose(Ingredient::Water, a.water_g, "Doserer vann til levainen"));
  steps_.push_back(dose(Ingredient::Flour, a.flour_g, "Doserer mel til levainen"));
  steps_.push_back(mix(kp_.mix_speed, kp_.levain_mix_s, 3.0f, 2.0f, true, "Blander levainen"));
  steps_.push_back(event(Event::LevainDosed));
  for (float &v : dosed_) v = 0.0f;
  planned_[int(Ingredient::Water)] = a.water_g;
  planned_[int(Ingredient::Flour)] = a.flour_g;
  planned_[int(Ingredient::Salt)] = 0.0f;
  flour_planned_main_ = water_planned_main_ = flour_dosed_main_ = water_dosed_main_ = 0.0f;
  begin(now_s);
}

void Sequence::start_dough(const DoughAmounts &a, float now_s) {
  steps_.clear();
  steps_.push_back(dose(Ingredient::Water, a.water_g, "Doserer vann"));
  steps_.push_back(mix(kp_.mix_speed, kp_.mix_after_water_s, 0.0f, 0.0f, false, "Rører ut levainen"));
  const int n = std::max(1, recipe_.flour_portions);
  for (int i = 0; i < n; i++) {
    steps_.push_back(dose(Ingredient::Flour, a.flour_g / n, "Doserer mel"));
    steps_.push_back(mix(kp_.mix_speed, kp_.mix_per_portion_s, 0.0f, 0.0f, false, "Blander inn melet"));
  }
  steps_.push_back(mix(kp_.mix_speed, kp_.combine_s, 20.0f, 3.0f, true, "Blander deigen"));
  steps_.push_back(rest(kp_.fermentolyse_s, "Fermentolyse"));
  steps_.push_back(dose(Ingredient::Salt, a.salt_g, "Doserer salt"));
  steps_.push_back(dose(Ingredient::Water, a.brine_water_g, "Doserer vann til saltet"));
  steps_.push_back(mix(kp_.mix_speed, kp_.salt_mix_s, 20.0f, 3.0f, true, "Blander inn saltet"));
  steps_.push_back(mix(kp_.knead_speed, kp_.knead_s, 45.0f, 3.0f, false, "Elter"));
  steps_.push_back(event(Event::DoughDone));
  static const char *const kFoldLabels[] = {"Bretter (1)", "Bretter (2)", "Bretter (3)", "Bretter (4)",
                                            "Bretter (5)", "Bretter (6)"};
  for (int i = 0; i < kp_.folds; i++) {
    steps_.push_back(rest(i == 0 ? kp_.first_fold_s : kp_.fold_interval_s, "Hviler mellom brettingene"));
    steps_.push_back(fold(kp_.fold_speed, kp_.fold_strokes, kp_.fold_on_s, kp_.fold_off_s, kFoldLabels[std::min(i, 5)]));
  }
  steps_.push_back(rest(kp_.baseline_wait_s, "Venter før hevemålingen"));
  steps_.push_back(event(Event::FoldsDone));
  for (float &v : dosed_) v = 0.0f;
  planned_[int(Ingredient::Water)] = a.water_g + a.brine_water_g;
  planned_[int(Ingredient::Flour)] = a.flour_g;
  planned_[int(Ingredient::Salt)] = a.salt_g;
  flour_planned_main_ = a.flour_g;
  water_planned_main_ = a.water_g;
  flour_dosed_main_ = water_dosed_main_ = 0.0f;
  begin(now_s);
}

void Sequence::begin(float now_s) {
  idx_ = 0;
  fault_ = "";
  wait_confirm_ = false;
  paused_at_s_ = NAN;
  pending_ = Event::None;
  step_start_s_ = now_s;
  step_dosed_ = 0.0f;
  dose_phase_ = DosePhase::Quiet;
  phase_start_s_ = now_s;
  status_ = steps_.empty() ? "Klar" : steps_[0].label;
}

void Sequence::abort() {
  for (auto &d : doser_) d.abort();
  steps_.clear();
  idx_ = 0;
  wait_confirm_ = false;
  fault_ = "";
  status_ = "Avbrutt";
}

void Sequence::confirm() {
  if (!busy()) return;
  if (faulted()) {  // retry the rest of a failed dose
    fault_ = "";
    dose_phase_ = DosePhase::Quiet;
    phase_start_s_ = last_now_s_;
  }
  wait_confirm_ = false;
}

Event Sequence::take_event() {
  Event e = pending_;
  pending_ = Event::None;
  return e;
}

bool Sequence::motion(const Step &s) const { return s.kind == StepKind::Mix || s.kind == StepKind::Fold || s.kind == StepKind::Dose; }

void Sequence::next(float now_s) {
  idx_++;
  step_dosed_ = 0.0f;
  step_start_s_ = now_s;
  dose_phase_ = DosePhase::Quiet;
  phase_start_s_ = now_s;
  if (idx_ < steps_.size()) {
    if (steps_[idx_].kind == StepKind::Dose && steps_[idx_].ing == Ingredient::Salt) adjust_salt_step(steps_[idx_]);
    status_ = steps_[idx_].label;
  } else {
    status_ = "Ferdig";
  }
}

// Salt and brine water follow the flour and water that actually went in.
void Sequence::adjust_salt_step(Step &s) {
  const float extra_flour = flour_dosed_main_ - flour_planned_main_;
  const float missing_water = water_planned_main_ - water_dosed_main_;
  s.grams = std::max(0.0f, s.grams + recipe_.salt_frac * extra_flour);
  if (idx_ + 1 < steps_.size() && steps_[idx_ + 1].kind == StepKind::Dose && steps_[idx_ + 1].ing == Ingredient::Water) {
    Step &w = steps_[idx_ + 1];
    w.grams = std::max(0.0f, w.grams + recipe_.hydration * extra_flour + missing_water);
  }
}

MachineOut Sequence::update(const MachineIn &in) {
  MachineOut out;
  last_now_s_ = in.now_s;
  if (!busy()) return out;
  const float now = in.now_s;
  if (!in.estop_ok) {
    abort();
    fault_ = "Nødstopp";
    status_ = "Nødstopp trykket inn";
    return out;
  }
  Step &s = steps_[idx_];

  // Door open during motion: stop, freeze the step clock and wait for a confirmation.
  const bool door_blocks = motion(s) && !in.door_closed;
  if (door_blocks || wait_confirm_ || faulted()) {
    if (door_blocks) wait_confirm_ = true;
    if (std::isnan(paused_at_s_)) paused_at_s_ = now;
    if (s.kind == StepKind::Dose && dose_phase_ == DosePhase::Dosing && doser_[int(s.ing)].busy()) {
      bank_dose(s, std::max(0.0f, doser_[int(s.ing)].dosed_g()));  // keep what is already in
      doser_[int(s.ing)].abort();
      dose_phase_ = DosePhase::Quiet;
    }
    if (s.kind == StepKind::Dose) out.quiet = true;
    return out;
  }
  if (!std::isnan(paused_at_s_)) {  // resume: shift the clocks by the pause
    const float paused = now - paused_at_s_;
    step_start_s_ += paused;
    phase_start_s_ += paused;
    paused_at_s_ = NAN;
    if (s.kind == StepKind::Dose) {  // the doser restarts (with a new tare) for what is missing
      dose_phase_ = DosePhase::Quiet;
      phase_start_s_ = now;
    }
  }
  const float t = now - step_start_s_;

  switch (s.kind) {
    case StepKind::Dose:
      out = run_dose(s, in);
      break;
    case StepKind::Mix:
    case StepKind::Fold:
      out = run_pattern(s, t);
      if (t >= s.duration_s) next(now);
      break;
    case StepKind::Rest:
      if (t >= s.duration_s) next(now);
      break;
    case StepKind::Event:
      pending_ = s.event;
      next(now);
      break;
  }
  return out;
}

MachineOut Sequence::run_pattern(const Step &s, float t) {
  MachineOut out;
  if (s.on_s <= 0.0f) {
    out.knead = s.speed;
    return out;
  }
  const float period = s.on_s + s.off_s;
  const int k = int(t / period);
  const float in_period = t - k * period;
  if (in_period < s.on_s) out.knead = (s.alternate && (k % 2)) ? -s.speed : s.speed;
  return out;
}

void Sequence::bank_dose(const Step &s, float g) {
  dosed_[int(s.ing)] += g;
  step_dosed_ += g;
  if (s.ing == Ingredient::Flour && flour_planned_main_ > 0) flour_dosed_main_ += g;
  if (s.ing == Ingredient::Water && idx_ == 0 && water_planned_main_ > 0) water_dosed_main_ += g;
}

MachineOut Sequence::run_dose(Step &s, const MachineIn &in) {
  MachineOut out;
  out.quiet = true;
  out.dose_ing = s.ing;
  const int i = int(s.ing);
  const float now = in.now_s;
  const float in_phase = now - phase_start_s_;
  const bool has_flap = s.ing != Ingredient::Water;

  auto set_flap = [&](bool open) {
    if (s.ing == Ingredient::Flour) out.flap_flour_open = open;
    if (s.ing == Ingredient::Salt) out.flap_salt_open = open;
  };

  switch (dose_phase_) {
    case DosePhase::Quiet:
      if (in_phase >= kp_.quiet_before_s) {
        dose_remaining_g_ = std::max(0.0f, s.grams - step_dosed_);
        dose_phase_ = has_flap ? DosePhase::Opening : DosePhase::Dosing;
        phase_start_s_ = now;
        if (!has_flap) doser_[i].start(dose_remaining_g_, now, dp_[i]);
      }
      break;
    case DosePhase::Opening:
      set_flap(true);
      if (in_phase >= kp_.flap_s) {
        dose_phase_ = DosePhase::Dosing;
        phase_start_s_ = now;
        doser_[i].start(dose_remaining_g_, now, dp_[i]);
      }
      break;
    case DosePhase::Dosing: {
      set_flap(true);
      DoseCommand c = doser_[i].update(now, in.weight_g);
      out.dose_run = c.run;
      out.dose_reverse = c.reverse;
      if (doser_[i].done()) {
        bank_dose(s, doser_[i].dosed_g());
        dose_phase_ = has_flap ? DosePhase::Closing : DosePhase::PumpBack;
        phase_start_s_ = now;
        out.dose_run = false;
      } else if (doser_[i].failed()) {
        bank_dose(s, std::max(0.0f, doser_[i].dosed_g()));
        fault_ = s.ing == Ingredient::Water ? "Vannet kommer ikke ut. Fyll tanken og trykk Fortsett."
                 : s.ing == Ingredient::Flour ? "Melet kommer ikke ut. Sjekk beholderen og trykk Fortsett."
                                              : "Saltet kommer ikke ut. Sjekk saltboksen og trykk Fortsett.";
        if (std::string(doser_[i].fault()) == "scale not stable")
          fault_ = "Vekta er urolig. Sjekk at ingenting berører formen, og trykk Fortsett.";
        status_ = fault_;
        out.dose_run = false;
      }
      break;
    }
    case DosePhase::Closing:
      if (in_phase >= kp_.flap_s) next(now);
      break;
    case DosePhase::PumpBack:
      out.dose_run = in_phase < kp_.pump_back_s;
      out.dose_reverse = true;
      if (in_phase >= kp_.pump_back_s) next(now);
      break;
  }
  return out;
}

}  // namespace surdeig

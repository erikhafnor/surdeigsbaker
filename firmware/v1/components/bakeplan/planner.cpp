#include "planner.h"

#include <algorithm>
#include <cmath>
#include <cstdio>

namespace surdeig {

namespace {

float clampf(float v, float lo, float hi) { return std::max(lo, std::min(hi, v)); }

float log2f_safe(float x) { return std::log2(std::max(1e-6f, x)); }

float levain_mass_g(float dilution, const Recipe &r) { return r.starter_g * dilution; }

// Flour in the levain including the starter's own flour (starter at 100 % hydration).
float prefermented_flour_g(float dilution, const Recipe &r) { return 0.5f * r.starter_g * dilution; }

float main_flour_g(float dilution, const Recipe &r) {
  return std::max(50.0f, r.total_flour_g - prefermented_flour_g(dilution, r));
}

bool dilution_allowed(float dilution, const Recipe &r, const ModelParams &p) {
  float pff = prefermented_flour_g(dilution, r) / std::max(1.0f, r.total_flour_g);
  return pff >= p.pff_min - 1e-4f && pff <= p.pff_max + 1e-4f;
}

// If no dilution satisfies the PFF limits (e.g. a very large or very small starter), use the
// one closest to the range so the machine can still bake.
int closest_dilution(const Recipe &r, const ModelParams &p) {
  int best = 0;
  float best_err = 1e9f;
  for (int i = 0; i < p.num_dilutions; i++) {
    float pff = prefermented_flour_g(p.dilutions[i], r) / std::max(1.0f, r.total_flour_g);
    float err = pff < p.pff_min ? p.pff_min - pff : (pff > p.pff_max ? pff - p.pff_max : 0.0f);
    if (err < best_err) {
      best_err = err;
      best = i;
    }
  }
  return best;
}

template<typename F> void for_each_dilution(const Recipe &r, const ModelParams &p, F f) {
  bool any = false;
  for (int i = 0; i < p.num_dilutions; i++) {
    if (dilution_allowed(p.dilutions[i], r, p)) {
      f(p.dilutions[i]);
      any = true;
    }
  }
  if (!any) f(p.dilutions[closest_dilution(r, p)]);
}

float bulk_eq_for(float dilution, float temp_c, const Recipe &r, const ModelParams &p) {
  return bulk_eq_h(levain_mass_g(dilution, r), main_flour_g(dilution, r), bulk_rise_target(temp_c, p), p);
}

// Temperature in [lo, hi] where total_hours(...) == available_h (total falls with temperature).
float solve_temp(float dilution, float available_h, float lo, float hi, float activity, const Recipe &r,
                 const ModelParams &p) {
  for (int i = 0; i < 60; i++) {
    float mid = 0.5f * (lo + hi);
    if (total_hours(dilution, mid, 0.0f, activity, r, p) > available_h)
      lo = mid;  // too slow: needs warmer
    else
      hi = mid;
  }
  return 0.5f * (lo + hi);
}

// Hottest temperature in [lo, hi] at which the bulk still lasts min_bulk_h(). Warmer than this
// the dough would be ready before the rise can be measured.
float bulk_temp_cap(float dilution, float lo, float hi, float activity, const Recipe &r, const ModelParams &p) {
  auto bulk_time = [&](float t) { return bulk_eq_for(dilution, t, r, p) / (activity * speed_factor(t, p)); };
  if (bulk_time(hi) >= min_bulk_h(p)) return hi;
  if (bulk_time(lo) <= min_bulk_h(p)) return lo;
  for (int i = 0; i < 50; i++) {
    float mid = 0.5f * (lo + hi);
    if (bulk_time(mid) >= min_bulk_h(p))
      lo = mid;
    else
      hi = mid;
  }
  return lo;
}

}  // namespace

float speed_factor(float temp_c, const ModelParams &p) {
  const float t0 = p.rate_table_t0_c;
  const float t_end = t0 + (kRateTablePoints - 1);
  if (temp_c <= t0) return p.rate_table[0] * std::pow(3.0f, (temp_c - t0) / 10.0f);  // Q10 ~3 when cold
  if (temp_c >= t_end) return p.rate_table[kRateTablePoints - 1];                      // flat when warm
  float x = temp_c - t0;
  int i = static_cast<int>(x);
  float f = x - i;
  return p.rate_table[i] * (1.0f - f) + p.rate_table[i + 1] * f;
}

float temp_for_factor(float factor, const ModelParams &p) {
  float lo = p.rate_table_t0_c - 10.0f;
  float hi = p.rate_table_t0_c + (kRateTablePoints - 1);
  if (factor >= speed_factor(hi, p)) return hi;
  if (factor <= speed_factor(lo, p)) return lo;
  for (int i = 0; i < 50; i++) {
    float mid = 0.5f * (lo + hi);
    if (speed_factor(mid, p) < factor)
      lo = mid;
    else
      hi = mid;
  }
  return 0.5f * (lo + hi);
}

float lowest_temp(float room_c, const ModelParams &p) { return std::max(p.t_min_c, room_c); }

float highest_temp(float room_c, const ModelParams &p) {
  // If the room is warmer than t_max the dough simply sits at room temperature.
  return std::max(p.t_max_c, lowest_temp(room_c, p));
}

float bulk_rise_target(float temp_c, const ModelParams &p) {
  float r;
  if (temp_c <= p.rise_t[0]) {
    r = p.rise_r[0];
  } else if (temp_c >= p.rise_t[5]) {
    r = p.rise_r[5];
  } else {
    r = p.rise_r[5];
    for (int i = 0; i < 5; i++) {
      if (temp_c <= p.rise_t[i + 1]) {
        float f = (temp_c - p.rise_t[i]) / (p.rise_t[i + 1] - p.rise_t[i]);
        r = p.rise_r[i] + f * (p.rise_r[i + 1] - p.rise_r[i]);
        break;
      }
    }
  }
  return r * p.rise_scale;
}

float levain_eq_h(float dilution, bool cold_starter, const ModelParams &p) {
  float lag = cold_starter ? p.levain_lag_cold : p.levain_lag_fed;
  return p.k_ref_h * (lag + p.levain_slope * log2f_safe(dilution));
}

float bulk_eq_h(float levain_g, float main_flour_g, float rise_pct, const ModelParams &p) {
  float s = 100.0f * levain_g / std::max(1.0f, main_flour_g);
  float n = p.bulk_base + p.bulk_slope * log2f_safe(20.0f / s) + log2f_safe(rise_pct / 30.0f);
  return p.k_ref_h * std::max(p.bulk_min_doublings, n);
}

float total_hours(float dilution, float temp_c, float delay_h, float activity, const Recipe &r,
                  const ModelParams &p) {
  float speed = activity * speed_factor(temp_c, p);
  float levain = levain_eq_h(dilution, r.cold_starter, p) / speed;
  float bulk = std::max(min_bulk_h(p), bulk_eq_for(dilution, temp_c, r, p) / speed);
  return delay_h + p.levain_dosing_h + levain + bulk;
}

void feasible_window(float room_c, float activity, const Recipe &r, const ModelParams &p,
                     float *earliest_h, float *latest_h) {
  const float lo = lowest_temp(room_c, p);
  const float hi = highest_temp(room_c, p);
  float earliest = 1e9f, latest = 0.0f;
  for_each_dilution(r, p, [&](float d) {
    float cap = bulk_temp_cap(d, lo, hi, activity, r, p);
    earliest = std::min(earliest, total_hours(d, cap, 0.0f, activity, r, p));
    latest = std::max(latest, total_hours(d, lo, p.max_start_delay_h, activity, r, p));
  });
  *earliest_h = earliest;
  *latest_h = latest;
}

Plan make_plan(float available_h, float room_c, float activity, const Recipe &r, const ModelParams &p) {
  Plan best;
  feasible_window(room_c, activity, r, p, &best.earliest_h, &best.latest_h);
  const float lo = lowest_temp(room_c, p);
  const float hi = highest_temp(room_c, p);
  const float pref = p.t_pref_c > 0.0f ? p.t_pref_c : 0.5f * (lo + hi);
  float best_score = 1e9f;

  for_each_dilution(r, p, [&](float d) {
    const float cap = bulk_temp_cap(d, lo, hi, activity, r, p);
    const float fastest = total_hours(d, cap, 0.0f, activity, r, p);
    const float slowest = total_hours(d, lo, 0.0f, activity, r, p);
    float temp, delay = 0.0f, score;
    if (available_h < fastest) {
      return;  // not possible even at maximum temperature
    } else if (available_h <= slowest) {
      temp = solve_temp(d, available_h, lo, cap, activity, r, p);
      score = std::fabs(temp - pref);
    } else {
      delay = available_h - slowest;
      if (delay > p.max_start_delay_h) return;  // too slow even when waiting
      temp = lo;
      score = std::fabs(temp - pref) + 1.0f + 0.5f * delay;  // waiting is a last resort
    }
    // Prefer a levain close to the reference recipe and plenty of measured bulk for feedback.
    const float speed0 = activity * speed_factor(temp, p);
    const float measured = bulk_eq_for(d, temp, r, p) / speed0 - p.dough_steps_h - p.fold_time_h;
    const float pff = prefermented_flour_g(d, r) / std::max(1.0f, r.total_flour_g);
    score += std::fabs(pff - p.pff_pref) / 0.05f;
    if (measured < 2.0f) score += 1.5f * (2.0f - measured);
    if (score < best_score) {
      best_score = score;
      const float speed = activity * speed_factor(temp, p);
      best.feasible = true;
      best.dilution = d;
      best.temp_c = temp;
      best.start_delay_h = delay;
      best.levain_eq_h = levain_eq_h(d, r.cold_starter, p);
      best.rise_target_pct = bulk_rise_target(temp, p);
      best.bulk_eq_h = bulk_eq_for(d, temp, r, p);
      best.levain_h = best.levain_eq_h / speed;
      best.bulk_h = std::max(min_bulk_h(p), best.bulk_eq_h / speed);
      best.total_h = total_hours(d, temp, delay, activity, r, p);
      best.levain_flour_g = 0.5f * r.starter_g * (d - 1.0f);
      best.levain_water_g = best.levain_flour_g;
      best.pff = prefermented_flour_g(d, r) / std::max(1.0f, r.total_flour_g);
      const float slow = 0.8f * activity;
      best.late_risk_h = std::max(0.0f, total_hours(d, bulk_temp_cap(d, lo, hi, slow, r, p), delay, slow, r, p) -
                                            available_h);
    }
  });

  char buf[200];
  if (best.feasible) {
    std::snprintf(buf, sizeof(buf),
                  "levain 1:%.2g:%.2g, %.1f C, delay %.1f h, levain %.1f h, bulk %.1f h to +%.0f %%, pff %.0f %%, "
                  "late risk %.1f h",
                  0.5f * (best.dilution - 1.0f), 0.5f * (best.dilution - 1.0f), best.temp_c, best.start_delay_h,
                  best.levain_h, best.bulk_h, best.rise_target_pct, 100.0f * best.pff, best.late_risk_h);
  } else if (available_h < best.earliest_h) {
    std::snprintf(buf, sizeof(buf), "too early: earliest is %.1f h from now", best.earliest_h);
  } else {
    std::snprintf(buf, sizeof(buf), "too late: latest is %.1f h from now", best.latest_h);
  }
  best.reason = buf;
  return best;
}

void StepTracker::start(float target_eq_h) {
  target_eq_h_ = std::max(0.01f, target_eq_h);
  elapsed_eq_h_ = 0.0f;
}

void StepTracker::advance(float dt_h, float temp_c, const ModelParams &p) {
  if (dt_h > 0.0f) elapsed_eq_h_ += dt_h * speed_factor(temp_c, p);
}

float StepTracker::progress(float activity) const {
  return clampf(elapsed_eq_h_ * activity / target_eq_h_, 0.0f, 1.0f);
}

float StepTracker::remaining_h(float temp_c, float activity, const ModelParams &p) const {
  float rem_eq = std::max(0.0f, target_eq_h_ / activity - elapsed_eq_h_);
  return rem_eq / speed_factor(temp_c, p);
}

float activity_from_rise(float rise_fraction, float elapsed_eq_h, float target_eq_h, float prior,
                         const ModelParams &p) {
  if (!(rise_fraction >= kMinRiseForActivity) || elapsed_eq_h <= 0.0f) return prior;  // also catches NaN
  float x = std::pow(clampf(rise_fraction, 0.0f, 1.2f), 1.0f / kRiseShape);
  float a = x * target_eq_h / elapsed_eq_h;
  return clampf(a, p.activity_min, p.activity_max);
}

float bulk_rel_target(float a, float e_f_h, float need_eq_h, float rise_target) {
  float x_f = clampf(e_f_h * a / need_eq_h, 0.0f, 0.95f);
  return (1.0f + rise_target) / (1.0f + rise_target * std::pow(x_f, kRiseShape)) - 1.0f;
}

float activity_from_bulk_rise(float rel_rise, float e_h, float e_f_h, float need_eq_h, float rise_target,
                              float prior, const ModelParams &p) {
  // Too little rise to tell noise from signal.
  if (!(rel_rise >= 0.04f) || e_h <= e_f_h + 1e-3f || need_eq_h <= 0.0f) return prior;
  // Monotonic in a because e_h > e_f_h, so bisection is safe. (No clamping of x here: that
  // would break monotonicity.)
  auto rel_for = [&](float a) {
    float x = e_h * a / need_eq_h;
    float x_f = e_f_h * a / need_eq_h;
    return (1.0f + rise_target * std::pow(x, kRiseShape)) / (1.0f + rise_target * std::pow(x_f, kRiseShape)) - 1.0f;
  };
  float lo = p.activity_min, hi = p.activity_max;
  if (rel_rise <= rel_for(lo)) return lo;
  if (rel_rise >= rel_for(hi)) return hi;
  for (int i = 0; i < 40; i++) {
    float mid = std::sqrt(lo * hi);
    if (rel_for(mid) < rel_rise)
      lo = mid;
    else
      hi = mid;
  }
  return std::sqrt(lo * hi);
}

float blend_activity(float prior, float measured, float weight_measured, const ModelParams &p) {
  float w = clampf(weight_measured, 0.0f, 1.0f);
  float a = std::exp((1.0f - w) * std::log(prior) + w * std::log(measured));
  return clampf(a, p.activity_min, p.activity_max);
}

float update_activity_history(float history, float learned, const ModelParams &p, float weight_new) {
  if (!(history > 0.0f)) return clampf(learned, p.activity_min, p.activity_max);
  return blend_activity(history, learned, weight_new, p);
}

float temp_to_finish_in(float remaining_eq_h, float hours_left, float room_c, const ModelParams &p,
                        float *eta_h, float hi_c) {
  const float lo = lowest_temp(room_c, p);
  const float hi = std::isnan(hi_c) ? highest_temp(room_c, p) : std::max(hi_c, lo);
  float temp;
  if (remaining_eq_h <= 0.0f) {
    temp = lo;
  } else if (hours_left <= 0.05f) {
    temp = hi;
  } else {
    temp = clampf(temp_for_factor(remaining_eq_h / hours_left, p), lo, hi);
  }
  if (eta_h != nullptr) *eta_h = std::max(0.0f, remaining_eq_h) / speed_factor(temp, p);
  return temp;
}

// ---------------------------------------------------------------- Controller

bool Controller::start(float now_h, float target_h, float room_c, const Recipe &recipe,
                       float activity_prior) {
  room_c_ = std::isnan(room_c) ? 20.0f : room_c;
  activity_ = clampf(activity_prior, p_.activity_min, p_.activity_max);
  plan_ = make_plan(target_h - now_h, room_c_, activity_, recipe, p_);
  if (!plan_.feasible) {
    stage_ = Stage::Idle;
    request_ = Request::None;
    return false;
  }
  target_h_ = target_h;
  start_h_ = now_h;
  stage_start_h_ = now_h;
  last_tick_h_ = now_h;
  setpoint_c_ = NAN;
  bulk_measured_ = false;
  bulk_baseline_eq_h_ = 0.0f;
  levain_tracker_.start(plan_.levain_eq_h);
  bulk_tracker_.start(plan_.bulk_eq_h);
  eta_h_ = now_h + plan_.total_h;
  stage_ = Stage::Delay;
  request_ = plan_.start_delay_h > 0.01f ? Request::None : Request::DoseLevain;
  return true;
}

void Controller::abort() {
  stage_ = Stage::Idle;
  request_ = Request::None;
  setpoint_c_ = NAN;
}

void Controller::levain_dosed(float now_h) {
  stage_ = Stage::Levain;
  request_ = Request::None;
  stage_start_h_ = now_h;
  last_tick_h_ = now_h;
  update_setpoint(now_h);
}

void Controller::dough_done(float now_h) {
  if (stage_ != Stage::Dough) return;
  stage_ = Stage::Bulk;
  request_ = Request::None;
  stage_start_h_ = now_h;
  bulk_measured_ = false;
  update_setpoint(now_h);
}

void Controller::folds_done(float now_h) {
  if (stage_ != Stage::Bulk || bulk_measured_) return;
  // The sensor takes a new baseline now; remember how far the bulk had come.
  bulk_baseline_eq_h_ = bulk_tracker_.elapsed_eq_h();
  bulk_measured_ = true;
  update_setpoint(now_h);
}

float Controller::measured_rise_target_pct() const {
  if (!bulk_measured_) return plan_.rise_target_pct;
  return 100.0f * bulk_rel_target(activity_, bulk_baseline_eq_h_, bulk_tracker_.target_eq_h(),
                                  plan_.rise_target_pct / 100.0f);
}

void Controller::finished(float now_h) {
  stage_ = Stage::Ready;
  request_ = Request::None;
  setpoint_c_ = NAN;
  eta_h_ = now_h;
}

bool Controller::off_target(float tolerance_h) const {
  if (stage_ == Stage::Idle || stage_ == Stage::Ready) return false;
  return std::fabs(eta_h_ - target_h_) > tolerance_h;
}

float Controller::step_progress() const {
  switch (stage_) {
    case Stage::Levain:
      return levain_tracker_.progress(activity_);
    case Stage::Dough:
    case Stage::Bulk:
      return bulk_tracker_.progress(activity_);
    case Stage::Ready:
      return 1.0f;
    default:
      return 0.0f;
  }
}

void Controller::update_setpoint(float now_h) {
  float hours_left = target_h_ - now_h;
  float eta_left = 0.0f;
  switch (stage_) {
    case Stage::Delay: {
      setpoint_c_ = NAN;
      float wait = std::max(0.0f, plan_.start_delay_h - (now_h - start_h_));
      float speed = activity_ * speed_factor(plan_.temp_c, p_);
      eta_h_ = now_h + wait + p_.levain_dosing_h + levain_tracker_.target_eq_h() / speed +
               bulk_tracker_.target_eq_h() / speed;
      break;
    }
    case Stage::Levain: {
      // One temperature for the rest of the levain and the whole bulk keeps both in the middle.
      float rem_lev = std::max(0.0f, levain_tracker_.target_eq_h() / activity_ - levain_tracker_.elapsed_eq_h());
      float bulk_eq = bulk_tracker_.target_eq_h() / activity_;
      setpoint_c_ = temp_to_finish_in(rem_lev + bulk_eq, hours_left, room_c_, p_, &eta_left);
      if (eta_left > hours_left + 0.02f) {
        // Late even with the bulk at maximum: run the rest of the levain warmer.
        float bulk_time = bulk_eq / speed_factor(highest_temp(room_c_, p_), p_);
        float eta_lev = 0.0f;
        setpoint_c_ = temp_to_finish_in(rem_lev, hours_left - bulk_time, room_c_, p_, &eta_lev, p_.t_max_levain_c);
        eta_left = eta_lev + bulk_time;
      }
      eta_h_ = now_h + eta_left;
      break;
    }
    case Stage::Dough:
    case Stage::Bulk: {
      float rem = std::max(0.0f, bulk_tracker_.target_eq_h() / activity_ - bulk_tracker_.elapsed_eq_h());
      setpoint_c_ = temp_to_finish_in(rem, hours_left, room_c_, p_, &eta_left);
      eta_h_ = now_h + eta_left;
      break;
    }
    default:
      setpoint_c_ = NAN;
      break;
  }
}

void Controller::tick(float now_h, const Measurement &m) {
  if (stage_ == Stage::Idle || stage_ == Stage::Ready) return;
  if (!std::isnan(m.room_c)) room_c_ = m.room_c;
  float dt = std::isnan(last_tick_h_) ? 0.0f : std::max(0.0f, now_h - last_tick_h_);
  last_tick_h_ = now_h;
  // Advance the model at the measured dough temperature (fallback: setpoint, then room).
  float temp = !std::isnan(m.dough_c) ? m.dough_c : (!std::isnan(setpoint_c_) ? setpoint_c_ : room_c_);

  switch (stage_) {
    case Stage::Delay:
      if (request_ == Request::None && now_h - start_h_ >= plan_.start_delay_h) request_ = Request::DoseLevain;
      break;

    case Stage::Levain: {
      levain_tracker_.advance(dt, temp, p_);
      const float frac = m.rise_pct / 100.0f;  // levain target is x2 (+100 %)
      float est = activity_from_rise(frac, levain_tracker_.elapsed_eq_h(), levain_tracker_.target_eq_h(),
                                     activity_, p_);
      activity_ = blend_activity(activity_, est, std::min(0.3f, dt / 0.5f), p_);
      float model_progress = levain_tracker_.elapsed_eq_h() / levain_tracker_.target_eq_h();  // activity 1
      bool measured_done = !std::isnan(frac) && frac >= 1.0f && model_progress >= 0.4f;
      bool model_done = std::isnan(frac) && levain_tracker_.progress(activity_) >= 1.0f;
      bool overdue = model_progress >= 2.5f;  // far slower than any plausible starter
      if (request_ == Request::None && (measured_done || model_done || overdue)) {
        if (measured_done) {
          // Exact activity for this starter today: carry most of it into the bulk.
          float a = clampf(levain_tracker_.target_eq_h() / levain_tracker_.elapsed_eq_h(), p_.activity_min,
                           p_.activity_max);
          activity_ = blend_activity(activity_, a, 0.7f, p_);
        }
        request_ = Request::MakeDough;
        stage_ = Stage::Dough;  // the bulk clock starts when the dough is mixed
        stage_start_h_ = now_h;
      }
      break;
    }

    case Stage::Dough:
      bulk_tracker_.advance(dt, temp, p_);  // the dough ferments while it is dosed, rested and kneaded
      break;

    case Stage::Bulk: {
      bulk_tracker_.advance(dt, temp, p_);
      if (!bulk_measured_) break;  // folds still going on: the model runs, the sensor is ignored
      const float rel = m.rise_pct / 100.0f;
      const float e = bulk_tracker_.elapsed_eq_h(), need = bulk_tracker_.target_eq_h();
      float est = activity_from_bulk_rise(rel, e, bulk_baseline_eq_h_, need, plan_.rise_target_pct / 100.0f,
                                          activity_, p_);
      activity_ = blend_activity(activity_, est, std::min(0.3f, dt / 0.5f), p_);
      float model_progress = e / need;  // activity 1
      bool measured_done = !std::isnan(rel) && rel >= 0.02f && model_progress >= 0.4f &&
                           rel >= bulk_rel_target(activity_, bulk_baseline_eq_h_, need, plan_.rise_target_pct / 100.0f);
      bool model_done = std::isnan(rel) && bulk_tracker_.progress(activity_) >= 1.0f;
      bool overdue = model_progress >= 2.5f;
      if (request_ == Request::None && (measured_done || model_done || overdue)) request_ = Request::Finish;
      break;
    }

    default:
      break;
  }
  update_setpoint(now_h);
}

}  // namespace surdeig

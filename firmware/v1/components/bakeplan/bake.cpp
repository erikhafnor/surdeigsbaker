#include "bake.h"

#include <algorithm>
#include <cstdio>

namespace surdeig {

// Norwegian number formatting: one decimal with a comma ("7,5").
static std::string n1(float v) {
  char buf[24];
  std::snprintf(buf, sizeof(buf), "%.1f", v);
  for (char *c = buf; *c; c++)
    if (*c == '.') *c = ',';
  return buf;
}

// ---------------------------------------------------------------- pan

float PanGeometry::area_mm2(float h) const {
  const float k = std::max(0.0f, std::min(1.0f, h / height));
  const float w = bottom_w + (top_w - bottom_w) * k;
  const float d = bottom_d + (top_d - bottom_d) * k;
  return w * d - (4.0f - float(M_PI)) * corner_r * corner_r;
}

float PanGeometry::volume_ml(float h) const {
  h = std::max(0.0f, std::min(h, height));
  // The area is quadratic in h: Simpson's rule is exact.
  return (area_mm2(0.0f) + 4.0f * area_mm2(h / 2.0f) + area_mm2(h)) * h / 6.0f / 1000.0f;
}

float PanGeometry::height_for_volume(float ml) const {
  float lo = 0.0f, hi = height;
  for (int i = 0; i < 40; i++) {
    float mid = 0.5f * (lo + hi);
    (volume_ml(mid) < ml ? lo : hi) = mid;
  }
  return 0.5f * (lo + hi);
}

// ---------------------------------------------------------------- bake

const char *Bake::state_name() const {
  switch (state_) {
    case BakeState::Idle: return "Klar";
    case BakeState::Planned: return "Venter";
    case BakeState::Working: return "Arbeider";
    case BakeState::Fermenting: return "Hever";
    case BakeState::Ready: return "Klar for forming";
    case BakeState::Failed: return "Stoppet";
  }
  return "?";
}

const char *Bake::status() const {
  if (state_ == BakeState::Working || seq_.busy()) {
    if (seq_.waiting_for_confirm()) return "Døra ble åpnet. Lukk døra og trykk Fortsett.";
    if (seq_.faulted()) return seq_.fault();
    return seq_.status();
  }
  switch (ctl_.stage()) {
    case Stage::Delay: return "Venter med å mate surdeigen";
    case Stage::Levain: return "Levainen hever";
    case Stage::Dough: return "Deigen blandes";
    case Stage::Bulk: return bulk_measuring_ ? "Deigen hever" : "Bretting";
    case Stage::Ready: return "Deigen er klar for forming";
    default: return state_name();
  }
}

bool Bake::start(float now_s, float hours_until_ready, bool cold_starter, float activity_prior,
                 float fallback_starter_g) {
  float starter = fallback_starter_g;
  if (!std::isnan(empty_pan_g_) && !std::isnan(stable_w_)) starter = stable_w_ - empty_pan_g_;
  if (starter < cfg_.min_starter_g || starter > cfg_.max_starter_g) {
    char buf[160];
    std::snprintf(buf, sizeof(buf), "Fant %.0f g surdeig i formen. Legg i 1–2 ss (15–40 g) og prøv igjen.", starter);
    set_message(buf);
    state_ = BakeState::Idle;
    return false;
  }
  cfg_.recipe.starter_g = starter;
  cfg_.recipe.cold_starter = cold_starter;
  const float now_h = hours(now_s);
  const float room = std::isnan(last_room_c_) ? 21.0f : last_room_c_;
  bool ok = ctl_.start(now_h, now_h + hours_until_ready, room, cfg_.recipe, activity_prior);
  const Plan &p = ctl_.plan();
  char buf[220];
  if (!ok) {
    std::snprintf(buf, sizeof(buf),
                  "Ikke mulig med %.0f g surdeig: tidligst om %s t, senest om %s t. Velg en annen tid, "
                  "eller bruk mer eller matet surdeig.",
                  starter, n1(p.earliest_h).c_str(), n1(p.latest_h).c_str());
    set_message(buf);
    state_ = BakeState::Idle;
    return false;
  }
  if (p.late_risk_h > 0.5f) {
    std::snprintf(buf, sizeof(buf),
                  "Planen har liten margin: er surdeigen tregere enn vanlig, kan deigen bli opptil %s t forsinket.",
                  n1(p.late_risk_h).c_str());
    set_message(buf);
  } else {
    set_message("Planen er lagt.");
  }
  levain_started_ = dough_started_ = bulk_measuring_ = false;
  baseline_ml_ = rise_pct_ = NAN;
  learned_ = NAN;
  dough_g_ = starter;
  last_tick_s_ = -1e9f;
  state_ = BakeState::Planned;
  return true;
}

void Bake::abort() {
  seq_.abort();
  ctl_.abort();
  state_ = BakeState::Idle;
  set_message("Avbrutt.");
}

void Bake::shaped() {
  if (state_ == BakeState::Ready) {
    state_ = BakeState::Idle;
    set_message("God baking!");
  }
}

std::string Bake::plan_summary() const {
  const Plan &p = ctl_.plan();
  if (!p.feasible) return "";
  char buf[200];
  const std::string r = n1((p.dilution - 1.0f) / 2.0f);
  std::snprintf(buf, sizeof(buf), "Levain 1:%s:%s (%.0f g mel, %.0f g vann), %s °C, levain %s t, deig %s t til +%.0f %%",
                r.c_str(), r.c_str(), p.levain_flour_g, p.levain_water_g, n1(p.temp_c).c_str(), n1(p.levain_h).c_str(),
                n1(p.bulk_h).c_str(), p.rise_target_pct);
  return buf;
}

float Bake::eta_hours(float now_s) const {
  if (state_ == BakeState::Idle || state_ == BakeState::Failed) return NAN;
  if (state_ == BakeState::Ready) return 0.0f;
  return ctl_.eta_h() - hours(now_s);
}

Bake::Outputs Bake::update(const Inputs &in) {
  Outputs out;
  wf_.push(in.now_s, in.weight_g);
  if (wf_.stable(1.0f, 0.3f)) stable_w_ = wf_.mean();
  if (!std::isnan(in.room_c)) last_room_c_ = in.room_c;

  if (state_ == BakeState::Idle || state_ == BakeState::Failed) return out;
  if (!in.estop_ok) {
    seq_.abort();
    ctl_.abort();
    state_ = BakeState::Failed;
    set_message("Nødstoppen ble trykket inn. Bakingen er stoppet.");
    return out;
  }
  if (state_ == BakeState::Ready) {
    out.ready = true;
    return out;
  }

  // Rise: ToF distance → dough height (smoothed, not while the blade turns) → volume → %
  // above the current baseline.
  if (std::fabs(last_knead_) > 0.01f) motion_until_s_ = in.now_s + cfg_.motion_blank_s;
  if (!std::isnan(in.tof_mm) && in.now_s >= motion_until_s_) {
    const float h = cfg_.tof_to_bottom_mm - in.tof_mm;
    if (std::isnan(height_mm_) || std::isnan(height_t_s_) || in.now_s - height_t_s_ > 600.0f) {
      height_mm_ = h;
    } else {
      const float a = std::min(1.0f, (in.now_s - height_t_s_) / cfg_.height_tau_s);
      height_mm_ += a * (h - height_mm_);
    }
    height_t_s_ = in.now_s;
  } else if (in.now_s < motion_until_s_) {
    height_t_s_ = NAN;  // restart the smoothing after the blade has stopped
  }
  float rise = NAN;
  if (bulk_measuring_ && !std::isnan(height_mm_) && !std::isnan(baseline_ml_) && baseline_ml_ > 1.0f)
    rise = 100.0f * (cfg_.pan.volume_ml(height_mm_) / baseline_ml_ - 1.0f);
  rise_pct_ = rise;

  // Work in progress.
  MachineIn m;
  m.now_s = in.now_s;
  m.weight_g = in.weight_g;
  m.door_closed = in.door_closed;
  m.estop_ok = in.estop_ok;
  out.machine = seq_.update(m);
  last_knead_ = out.machine.knead;
  switch (seq_.take_event()) {
    case Event::LevainDosed:
      ctl_.levain_dosed(hours(in.now_s));
      dough_g_ += seq_.dosed_g(Ingredient::Water) + seq_.dosed_g(Ingredient::Flour);
      break;
    case Event::DoughDone:
      ctl_.dough_done(hours(in.now_s));
      dough_g_ += seq_.dosed_g(Ingredient::Water) + seq_.dosed_g(Ingredient::Flour) + seq_.dosed_g(Ingredient::Salt);
      break;
    case Event::FoldsDone: {
      ctl_.folds_done(hours(in.now_s));
      // Baseline: the measured height if there is one, else the volume from the weight.
      float ml = !std::isnan(height_mm_) && height_mm_ > 5.0f ? cfg_.pan.volume_ml(height_mm_)
                                                                : dough_g_ / cfg_.dough_density;
      baseline_ml_ = ml;
      bulk_measuring_ = true;
      break;
    }
    default:
      break;
  }

  // Fermentation control.
  if (in.now_s - last_tick_s_ >= cfg_.tick_s) {
    last_tick_s_ = in.now_s;
    Measurement meas;
    meas.room_c = in.room_c;
    meas.dough_c = in.dough_c;
    meas.rise_pct = rise;
    ctl_.tick(hours(in.now_s), meas);
  }
  const Request r = ctl_.request();
  if (r == Request::DoseLevain && !levain_started_ && !seq_.busy()) {
    levain_started_ = true;
    seq_.start_levain(levain_amounts(ctl_.plan()), in.now_s);
  } else if (r == Request::MakeDough && !dough_started_ && !seq_.busy()) {
    dough_started_ = true;
    seq_.start_dough(dough_amounts(cfg_.recipe, ctl_.plan(), cfg_.dough), in.now_s);
  } else if (r == Request::Finish) {
    ctl_.finished(hours(in.now_s));
    learned_ = ctl_.activity();
    state_ = BakeState::Ready;
    set_message("Deigen er klar for forming.");
    out.ready = true;
    return out;
  }

  state_ = seq_.busy() ? BakeState::Working
           : (ctl_.stage() == Stage::Delay ? BakeState::Planned : BakeState::Fermenting);
  // Heat follows the plan. The caller keeps the heater off while machine.quiet is set.
  out.setpoint_c = ctl_.setpoint_c();
  return out;
}

}  // namespace surdeig

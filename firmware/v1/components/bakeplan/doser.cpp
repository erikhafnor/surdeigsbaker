#include "doser.h"

#include <algorithm>

namespace surdeig {

const char *dose_state_name(DoseState s) {
  switch (s) {
    case DoseState::Idle: return "idle";
    case DoseState::Taring: return "taring";
    case DoseState::Coarse: return "coarse";
    case DoseState::Settling: return "settling";
    case DoseState::Fine: return "fine";
    case DoseState::Recovering: return "recovering";
    case DoseState::Done: return "done";
    case DoseState::Fault: return "fault";
  }
  return "?";
}

// ---------------------------------------------------------------- filter

void WeightFilter::reset() {
  n_ = 0;
  head_ = 0;
  raw_n_ = 0;
  latest_ = NAN;
}

void WeightFilter::push(float t_s, float grams) {
  if (std::isnan(grams)) return;
  raw_[raw_n_ % 3] = grams;
  raw_n_++;
  float v = grams;
  if (raw_n_ >= 3) {  // median of the last three readings removes single spikes
    float a = raw_[0], b = raw_[1], c = raw_[2];
    v = std::max(std::min(a, b), std::min(std::max(a, b), c));
  }
  latest_ = v;
  t_[head_] = t_s;
  w_[head_] = v;
  head_ = (head_ + 1) % kMax;
  if (n_ < kMax) n_++;
}

float WeightFilter::span_s() const {
  if (n_ < 2) return 0.0f;
  int newest = (head_ - 1 + kMax) % kMax;
  int oldest = (head_ - n_ + kMax) % kMax;
  return t_[newest] - t_[oldest];
}

static void window_stats(const float *t, const float *w, int n, int head, int kmax, float window_s, float *mean,
                         float *sd, int *count) {
  int newest = (head - 1 + kmax) % kmax;
  float t_end = t[newest];
  double s = 0, s2 = 0;
  int k = 0;
  for (int i = 0; i < n; i++) {
    int idx = (head - 1 - i + 2 * kmax) % kmax;
    if (t_end - t[idx] > window_s) break;
    s += w[idx];
    s2 += double(w[idx]) * w[idx];
    k++;
  }
  *count = k;
  *mean = k ? float(s / k) : NAN;
  double var = k > 1 ? (s2 - s * s / k) / (k - 1) : 0.0;
  *sd = float(std::sqrt(std::max(0.0, var)));
}

float WeightFilter::mean() const {
  float m, s;
  int k;
  window_stats(t_, w_, n_, head_, kMax, window_s_, &m, &s, &k);
  return m;
}

float WeightFilter::sd() const {
  float m, s;
  int k;
  window_stats(t_, w_, n_, head_, kMax, window_s_, &m, &s, &k);
  return s;
}

bool WeightFilter::stable(float window_s, float max_sd) const {
  if (n_ < 4 || span_s() < window_s * 0.9f) return false;
  float m, s;
  int k;
  window_stats(t_, w_, n_, head_, kMax, window_s, &m, &s, &k);
  return k >= 4 && s <= max_sd;
}

// ---------------------------------------------------------------- doser

void Doser::start(float target_g, float now_s, const DoseParams &p, bool reset_flow) {
  p_ = p;
  f_.reset();
  f_.window_s_ = p.stable_window_s;
  target_g_ = std::max(0.0f, target_g);
  tare_g_ = 0.0f;
  net_g_ = 0.0f;
  start_s_ = now_s;
  recoveries_ = 0;
  fine_pulses_ = 0;
  no_gain_pulses_ = 0;
  after_pulse_ = false;
  fault_ = "";
  if (reset_flow || std::isnan(flow_g_s_)) flow_g_s_ = p.flow_guess_g_s;
  enter(target_g_ > 0.0f ? DoseState::Taring : DoseState::Done, now_s);
}

void Doser::abort() {
  if (busy()) state_ = DoseState::Idle;
}

void Doser::enter(DoseState s, float now_s) {
  state_ = s;
  state_s_ = now_s;
}

void Doser::fail(const char *why, float now_s) {
  fault_ = why;
  enter(DoseState::Fault, now_s);
}

bool Doser::start_recovery(float now_s, DoseCommand *cmd) {
  if (++recoveries_ > p_.max_recoveries) {
    fail("nothing comes out", now_s);
    return false;
  }
  enter(DoseState::Recovering, now_s);
  cmd->run = true;
  cmd->reverse = true;
  return true;
}

DoseCommand Doser::update(float now_s, float grams) {
  DoseCommand cmd;
  f_.push(now_s, grams);
  if (!busy()) return cmd;
  if (now_s - start_s_ > p_.timeout_s) {
    fail("timeout", now_s);
    return cmd;
  }
  const float in_state = now_s - state_s_;
  const float w = f_.latest();
  if (state_ != DoseState::Taring && !std::isnan(w)) net_g_ = w - tare_g_;

  switch (state_) {
    case DoseState::Taring:
      if (f_.stable(p_.stable_window_s, p_.stable_sd_g)) {
        tare_g_ = f_.mean();
        net_g_ = 0.0f;
        run_start_s_ = now_s;
        run_start_net_ = 0.0f;
        mark_s_ = now_s;
        mark_net_ = 0.0f;
        enter(DoseState::Coarse, now_s);
        cmd.run = true;
      } else if (in_state > p_.tare_timeout_s) {
        fail("scale not stable", now_s);
      }
      break;

    case DoseState::Coarse: {
      // Learn the flow while running (after a short start-up).
      const float t_run = now_s - run_start_s_;
      if (t_run > 2.0f && net_g_ - run_start_net_ > 2.0f) {
        const float q = (net_g_ - run_start_net_) / t_run;
        flow_g_s_ = 0.8f * flow_g_s_ + 0.2f * q;
      }
      if (net_g_ - mark_net_ >= p_.stall_gain_g) {
        mark_s_ = now_s;
        mark_net_ = net_g_;
      }
      if (net_g_ + flow_g_s_ * p_.lag_s >= p_.coarse_fraction * target_g_) {
        enter(DoseState::Settling, now_s);
        break;
      }
      if (now_s - mark_s_ > p_.stall_s) {
        start_recovery(now_s, &cmd);
        break;
      }
      cmd.run = true;
      break;
    }

    case DoseState::Recovering:
      if (in_state < p_.reverse_s) {
        cmd.run = true;
        cmd.reverse = true;
      } else {
        mark_s_ = now_s;
        mark_net_ = net_g_;
        run_start_s_ = now_s;
        run_start_net_ = net_g_;
        after_pulse_ = false;
        enter(DoseState::Coarse, now_s);
        cmd.run = true;
      }
      break;

    case DoseState::Settling: {
      const bool quiet = f_.stable(std::min(p_.stable_window_s, in_state), p_.stable_sd_g * 2.0f);
      if (in_state < p_.settle_s || (!quiet && in_state < p_.settle_s + 4.0f)) break;
      net_g_ = f_.mean() - tare_g_;
      if (after_pulse_) {
        after_pulse_ = false;
        const float gain = net_g_ - pulse_start_net_;
        if (gain < 0.1f) {
          if (++no_gain_pulses_ >= 5) {  // pulses give nothing: treat it like a stall
            no_gain_pulses_ = 0;
            start_recovery(now_s, &cmd);
            break;
          }
        } else {
          no_gain_pulses_ = 0;
          if (pulse_s_ >= 0.3f) {
            const float q = gain / pulse_s_;
            flow_g_s_ = std::min(5.0f * p_.flow_guess_g_s,
                                 std::max(0.2f * p_.flow_guess_g_s, 0.7f * flow_g_s_ + 0.3f * q));
          }
        }
      }
      const float missing = target_g_ - net_g_;
      if (missing <= p_.tolerance_g) {
        enter(DoseState::Done, now_s);
        break;
      }
      if (fine_pulses_ >= p_.max_fine_pulses) {
        fail("too many fine pulses", now_s);
        break;
      }
      pulse_s_ = std::min(p_.max_pulse_s, std::max(p_.min_pulse_s, p_.fine_gain * missing / flow_g_s_));
      pulse_start_net_ = net_g_;
      after_pulse_ = true;
      fine_pulses_++;
      enter(DoseState::Fine, now_s);
      cmd.run = true;
      break;
    }

    case DoseState::Fine:
      if (in_state < pulse_s_) {
        cmd.run = true;
      } else {
        enter(DoseState::Settling, now_s);
      }
      break;

    default:
      break;
  }
  return cmd;
}

}  // namespace surdeig

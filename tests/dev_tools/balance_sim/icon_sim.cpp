// icon_sim.cpp - the iconostasis and the Raskol, month by month.
//
// The static checks prove the script is well formed. They cannot answer the
// two questions that decide whether the mechanic is any good:
//
//   1. can a church actually hold four icons for a century, or does the
//      upkeep quietly make the fourth slot decorative?
//   2. once the Raskol starts, is there a way OUT of it, and how long does it
//      take? The disaster carries monthly_fervor_increase = -1, which cancels
//      the base gain exactly - so the iconostasis starves, the lamps go out,
//      and going below two icons is one of the two can_end conditions. That is
//      meant to be the escape hatch. Whether it actually closes is arithmetic.
//
// Build: cl /std:c++17 /EHsc /O2 icon_sim.cpp
#include <cstdio>
#include <algorithm>

static const int  UPKEEP[5]   = { 0, 3, 8, 14, 20 };  // per bi-yearly pulse
static const int  LIGHT_COST  = 15;
static const int  MAX_FERVOR  = 100;
static const double PA_TIER[5]= { 0.0, 0.0, 0.30, 0.55, 0.80 }; // slots 1..4

static int slots_for(double pa) {
    if (pa >= 0.80) return 4;
    if (pa >= 0.55) return 3;
    if (pa >= 0.30) return 2;
    return 1;
}

struct Church {
    double fervor = 0;
    double pa     = 0.5;
    int    icons  = 0;
    bool   raskol = false;
    int    raskol_started_month = -1;
};

// One month of fervour. The disaster's -1 cancels the base +1 exactly.
static void month(Church& c) {
    double gain = 1.0 + (c.raskol ? -1.0 : 0.0);
    c.fervor = std::min((double)MAX_FERVOR, std::max(0.0, c.fervor + gain));
    if (c.raskol) c.pa -= 0.02 / 12.0;       // yearly_patriarch_authority = -0.02
}

// The bi-yearly pulse: rip_ro_icon_upkeep_effect, then the player's move.
static void pulse(Church& c, bool player_wants_max) {
    // authority lost takes a lamp with it
    while (c.icons > slots_for(c.pa)) --c.icons;

    // the oil
    if (c.icons > 0) {
        int owed = UPKEEP[c.icons];
        if (c.fervor >= owed) c.fervor -= owed;
        else --c.icons;                       // a lamp goes out
    }

    // the player lights what they can afford and have room for
    if (player_wants_max) {
        while (c.icons < slots_for(c.pa) && c.fervor >= LIGHT_COST + UPKEEP[c.icons + 1]) {
            c.fervor -= LIGHT_COST;
            ++c.icons;
        }
    }
}

static void steady_state(double pa, const char* label) {
    Church c; c.pa = pa;
    int lit_events = 0, went_dark = 0, prev = 0;
    for (int m = 0; m < 200 * 12; ++m) {
        month(c);
        if (m % 24 == 23) {
            int before = c.icons;
            pulse(c, true);
            if (c.icons > before) lit_events += c.icons - before;
            if (c.icons < before) went_dark  += before - c.icons;
            prev = c.icons;
        }
    }
    std::printf("  %-30s pa %.2f -> %d slot(s), settles at %d icon(s), "
                "fervour %5.1f, lit %d, went dark %d\n",
                label, pa, slots_for(pa), prev, c.fervor, lit_events, went_dark);
}

static void raskol_escape(double start_pa) {
    Church c; c.pa = start_pa; c.fervor = MAX_FERVOR; c.icons = 4; c.raskol = true;
    int m = 0, month_two_icons = -1, month_pa_60 = -1;
    for (; m < 100 * 12; ++m) {
        month(c);
        if (m % 24 == 23) pulse(c, false);      // the church cannot afford to relight
        if (month_two_icons < 0 && c.icons < 2) month_two_icons = m;
        if (month_pa_60 < 0 && c.pa < 0.60)     month_pa_60 = m;
        if (month_two_icons >= 0 && month_pa_60 >= 0) break;
    }
    int first = std::min(month_two_icons < 0 ? 99999 : month_two_icons,
                         month_pa_60 < 0 ? 99999 : month_pa_60);
    std::printf("  starting at pa %.2f, 4 icons, full fervour:\n", start_pa);
    std::printf("      authority falls under 60%%  after %5.1f years\n", month_pa_60 / 12.0);
    std::printf("      iconostasis falls under 2   after %5.1f years\n", month_two_icons / 12.0);
    std::printf("      -> can_end is satisfiable after %5.1f years\n\n", first / 12.0);
}

int main() {
    std::printf("\n=== CAN THE ICONOSTASIS BE HELD? (200 years, player lights greedily) ===\n\n");
    steady_state(0.20, "a metropolitan barely obeyed");
    steady_state(0.35, "an ordinary see");
    steady_state(0.60, "a strong patriarch");
    steady_state(0.85, "the patriarch of all Rus");

    std::printf("\n=== FERVOUR LEFT OVER FOR THE SOBOR (a focus costs 8) ===\n\n");
    for (int i = 0; i <= 4; ++i)
        std::printf("  %d icon(s): %2d gained per pulse - %2d upkeep = %2d spare\n",
                    i, 24, UPKEEP[i], 24 - UPKEEP[i]);

    std::printf("\n=== IS THE RASKOL ESCAPABLE? ===\n");
    std::printf("  the disaster's monthly_fervor_increase = -1 cancels the base gain,\n");
    std::printf("  so nothing comes in and the lamps burn what is left\n\n");
    raskol_escape(0.85);
    raskol_escape(0.70);
    return 0;
}

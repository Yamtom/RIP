// faith_sim.cpp - a bit-for-bit model of the RIP faith budget, so the numbers
// can be argued about before they reach the game.
//
// EU4's engine is closed: Clausewitz takes no C++ plugin, so the mechanics
// themselves must be script. What C++ is good for here is the arithmetic. The
// script does integer-ish work inside a `while` loop with no way to print, so
// the only way to know how a three-step budget behaves over a century - or
// whether the loop can spin - is to run the same arithmetic somewhere it can
// be watched.
//
// Build: cl /std:c++17 /EHsc /O2 faith_sim.cpp
#include <cstdio>
#include <vector>
#include <algorithm>
#include <numeric>
#include <random>
#include <string>

// ---------------------------------------------------------------- the script
// Mirrors rip_faith_unity_budget_effect: the unity ladder, in twentieths,
// exactly as the else_if chain walks it.
static double unity_ladder(double unity) {
    if (unity >= 1.00) return 1.00;   // the rung added for the 0.95 ceiling bug
    if (unity >= 0.95) return 0.95;
    if (unity >= 0.90) return 0.90;
    if (unity >= 0.85) return 0.85;
    if (unity >= 0.80) return 0.80;
    if (unity >= 0.75) return 0.75;
    if (unity >= 0.70) return 0.70;
    if (unity >= 0.60) return 0.60;
    if (unity >= 0.50) return 0.50;
    if (unity >= 0.40) return 0.40;
    if (unity >= 0.30) return 0.30;
    return 0.0;                       // below a third the church converts nobody
}

// The tithe. The budget is a TENTH of the realm's development, not all of it:
// a church can only put so many priests on the road in two years, however big
// the country is. Without this the mechanic converts a whole realm in one
// pulse - which is what this program was written to find out.
static const double TITHE = 10.0;

// The three steps the mod now runs the budget through.
static double stage_factor(int stage) {
    switch (stage) {
        case 1: return 0.75;
        case 2: return 0.50;
        default: return 0.25;         // step three is the permanent floor
    }
}

// The tier table the spend loop walks, top down.
struct Tier { int min_dev; int cost; };
static const Tier TIERS[] = { {24,24}, {16,16}, {11,11}, {7,7}, {0,4} };

// One pulse of the spend loop, written the way the script writes it: at each
// turn take the most expensive tier that is BOTH affordable and populated,
// charge its literal, convert one province from it. Returns provinces taken.
static int spend(std::vector<int>& unconverted, double budget_d, long long& wasted) {
    long long budget = (long long)budget_d;   // the script's floor()
    int taken = 0;
    for (;;) {
        if (budget < 4) break;                 // cheapest tier is 4
        bool any = false;
        for (const Tier& t : TIERS) {
            if (budget < t.cost) continue;
            auto it = std::find_if(unconverted.begin(), unconverted.end(),
                                   [&](int d){ return d >= t.min_dev; });
            if (it == unconverted.end()) continue;
            budget -= t.cost;
            unconverted.erase(it);
            ++taken;
            any = true;
            break;
        }
        // This is the `else = { set_variable ... value = 0 }` branch. Without
        // it the while loop would re-test its own condition unchanged and spin
        // the game to a halt - budget >= 4 and a province exists, but no tier
        // is both affordable and populated.
        if (!any) { wasted += budget; budget = 0; break; }
    }
    wasted += budget;
    return taken;
}

// ------------------------------------------------------------------ a realm
static std::vector<int> make_realm(int provinces, unsigned seed) {
    std::mt19937 rng(seed);
    // EU4's eastern-European spread: a few big sees, a long tail of hamlets.
    std::discrete_distribution<int> pick({0,0,0,12,18,20,16,12,8,5,4,3,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1});
    std::vector<int> v;
    v.reserve(provinces);
    for (int i = 0; i < provinces; ++i) v.push_back(std::max(3, pick(rng)));
    return v;
}

static void run(const char* label, int provinces, double unity, double already_ours) {
    std::vector<int> all = make_realm(provinces, 1234u);
    long long total_dev = std::accumulate(all.begin(), all.end(), 0LL);

    // the part of the realm still in the old rite
    std::vector<int> left(all.begin() + (size_t)(provinces * already_ours), all.end());
    int to_take = (int)left.size();

    long long wasted = 0;
    int stage = 1, pulse = 0, done = 0;
    std::string first_three;

    while (!left.empty() && pulse < 400) {
        ++pulse;
        double budget = (double)total_dev * unity_ladder(unity) / TITHE * stage_factor(stage);
        // THE ONE PRIEST FLOOR. Without it a poor see can never afford even the
        // cheapest tier and converts nothing at all for ever - which is what
        // this program showed for a 84-development Ruthenian minor.
        if (budget < 4.0 && unity_ladder(unity) > 0.0) budget = 4.0;
        int took = spend(left, budget, wasted);
        done += took;
        if (pulse <= 3) {
            char buf[64];
            std::snprintf(buf, sizeof buf, "%s%d", pulse > 1 ? "/" : "", took);
            first_three += buf;
        }
        if (stage < 3) ++stage;
        if (took == 0) break;             // nothing affordable and nothing changing
    }

    std::printf("  %-26s dev %4lld  unity %.2f  to take %3d  ->  %3d pulses (%s...), "
                "%d converted, %lld dev wasted\n",
                label, total_dev, unity, to_take, pulse, first_three.c_str(), done, wasted);
}

// ---------------------------------------------------------------- fervour
// Base monthly_fervor_increase is 1 (common/static_modifiers), so a bi-yearly
// pulse is worth about 24 fervour. MAX_FERVOR is 100.
static void fervour(int icons_held, int sobor_drain_per_pulse) {
    const int upkeep[5] = { 0, 3, 8, 14, 20 };   // the escalating table
    int gain = 24;
    int spend_ = upkeep[icons_held] + sobor_drain_per_pulse;
    std::printf("  %d icon(s) standing: gain %2d/pulse, upkeep %2d, Sobor %2d  ->  net %+3d\n",
                icons_held, gain, upkeep[icons_held], sobor_drain_per_pulse, gain - spend_);
}

int main() {
    std::printf("\n=== THE THREE-STEP BUDGET (0.75 / 0.50 / 0.25) ===\n");
    std::printf("  a pulse is two years; conversion starts from the schism\n\n");
    run("Muscovy, whole church",   60, 1.00, 0.20);
    run("Muscovy, unity 0.85",     60, 0.85, 0.20);
    run("Muscovy, unity 0.60",     60, 0.60, 0.20);
    run("Muscovy, unity 0.35",     60, 0.35, 0.20);
    run("a torn realm, unity 0.25",60, 0.25, 0.20);
    run("Ruthenian minor",         12, 0.90, 0.20);
    run("a great empire",         180, 0.90, 0.35);

    std::printf("\n=== WHAT THE FIRST STEP ALONE DOES ===\n");
    std::printf("  (step one is 0.75 of the ladder; the schism itself)\n\n");
    for (double u : {1.00, 0.85, 0.60, 0.35}) {
        std::vector<int> all = make_realm(60, 1234u);
        long long total = std::accumulate(all.begin(), all.end(), 0LL);
        double b = (double)total * unity_ladder(u) / TITHE * 0.75;
        std::printf("  unity %.2f -> budget %6.0f of %lld development (%.0f%% of the realm)\n",
                    u, b, total, 100.0 * b / (double)total);
    }

    std::printf("\n=== THE FERVOUR ECONOMY ===\n");
    std::printf("  base gain +1/month = 24 per bi-yearly pulse, cap 100\n\n");
    for (int i = 0; i <= 4; ++i) fervour(i, 0);
    std::printf("\n  with a Sobor focus also running (8 a pulse):\n\n");
    for (int i = 0; i <= 4; ++i) fervour(i, 8);

    std::printf("\n=== TERMINATION ===\n");
    {
        // The pathological case: a fat budget and nothing but hamlets left.
        std::vector<int> hamlets(3, 3);
        long long wasted = 0;
        int took = spend(hamlets, 400.0, wasted);
        std::printf("  budget 400, three 3-dev hamlets: took %d, wasted %lld, loop ended\n",
                    took, wasted);
    }
    {
        // The other one: budget just under the cheapest tier.
        std::vector<int> v(5, 30);
        long long wasted = 0;
        int took = spend(v, 3.0, wasted);
        std::printf("  budget 3 (below the 4 floor):     took %d, wasted %lld, loop ended\n",
                    took, wasted);
    }
    std::printf("\n");
    return 0;
}

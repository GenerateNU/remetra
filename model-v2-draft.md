# Trigger Finder model v2 (draft)

Draft, 2026-11-03. Once approved, this replaces the component exploration model (the M4–M5 build) as the
source of truth. Open items are at the end.

**In short.** The model learns 120 **family confidences**: for each component and symptom family, how
sure it is that the component causes symptoms in that family for this person. Every night it looks at
the symptoms logged in the past 24 hours. For each one, it looks back 36 hours (48 for skin) for the meals eaten before
it, weighted by exact delay, and shares out the blame, counting each other food in proportion to how
suspected it already is. Meals also lower their components' confidences a little over time, for every
reaction that would have been expected if they were real triggers. A component's **component confidence**
combines its three family confidences. Meals are chosen to explore, re-check or rest, and the person sees
an ingredient list plus a recipe. What is logged is all there is: time with no symptom logged counts as
symptom-free.

## Names

| Name | Symbol | Meaning | How many | Where it comes from |
|---|---|---|---|---|
| Family confidence | $q_{c,f}$ | How sure we are that component $c$ causes symptoms in family $f$ | 120 | learned |
| Component confidence | $Q_c$ | How sure we are that $c$ causes any symptom | 40 | computed from $c$'s three family confidences |
| Group confidence | $Q_G$ | The same for an always-together group (gluten and wheat fructans) | a few | computed from the members' component confidences |
| Background rate | $\lambda_f$ | How many family $f$ symptoms per hour happen with no food cause | 3 | learned |
| Reaction chance | $s_f$ | How often a real trigger causes a symptom after a full serving | 3 | fixed |
| Timing curve | $k_f$ | When after a meal a reaction tends to start (0–36 h, SKIN 0–48 h) | 3 | fixed |
| Exposure | $e_{m,c}$ | How much of $c$ a meal contains, 0 to 1 | per meal | ingredient map |
| Pull | $P_{j,c}$ | If $c$ is a real trigger, how strongly its recent meals were pushing towards symptom $j$ at the moment it started | per symptom | computed |
| Expected reactions | $R_{c,f}$ | How many family $f$ reactions we would have expected so far if $c$ were a real trigger | 120 | running total |
| Exposure count | $n_c$ | Meals with $c$ at a meaningful amount whose 48 h have passed | 40 | running count |

Confidences are never shown as numbers. The person sees labels.

## Inputs

| Input | From | Becomes |
|---|---|---|
| Conditions (IBS, IBD, celiac, other autoimmune) | onboarding | higher starting confidences for some components |
| Suspected foods | onboarding | higher starting confidences for their components |
| Exclusions and allergies | onboarding | never suggested |
| Meals eaten (ingredients, amounts, time) | food log | a meal event: time plus exposure per component (ingredient map, levels 1–3) |
| Symptoms (sensation, location, intensity, onset time) | symptom log | a symptom event: time plus family (symptom map); counts at intensity ≥ 3 |

## Outputs

**Visible to the person**
- Tonight's suggestion: an ingredient list and a recipe built from it. They can use the ingredients in
  their own dinner or cook the recipe.
- Weekly labels per food: Looks fine, Likely trigger, Still learning, or overall No clear food pattern.
- Safety messages for allergy and red-flag symptoms (unchanged).

**Hidden (debug view only)**
- Component confidences (40), family confidences (120), background rates (3).
- The meal type behind each suggestion and its target components.

## Lookback windows (decided)

- **Each night looks at the past 24 hours for symptoms**: every symptom logged since the previous nightly
  update. Older symptoms are not revisited; their effect is already in the stored confidences.
- **From each symptom, it looks back for meals** (binary search over the meal log): 36 hours for GI and
  HEAD symptoms, 48 hours for SKIN symptoms, because food-related eczema flares usually appear 6–48 hours
  after eating.
- **Expected reactions** are added for the part of each meal's window that fell in the past 24 hours, so
  the night touches every meal eaten in the past 60 hours (72 hours for SKIN).

Updates are incremental: yesterday's confidences, background rates and running totals carry over, and
only the new evidence is added. Nothing is recounted, because each symptom and each hour of each meal's
window is processed in exactly one night.

## What is tracked

**The log** (permanent, appended as the person logs)
- Meal events: time, and exposure per component (only the nonzero ones), sorted by time.
- Symptom events: time and family. Same-family entries within 3 hours of each other count as one
  symptom (bloating and cramps at 9 pm are one GI symptom).
- Profile: onboarding multipliers per component.

**Learned state** (stored, updated each night)
- 120 family confidences, kept as log-odds $\ell_{c,f}$.
- 3 background rates $\lambda_f$, with their running totals $B_f$ (symptoms put down to background) and
  $H$ (hours since onboarding).
- 120 expected-reaction totals $R_{c,f}$ (kept for the debug view; already folded into the log-odds).

**Bookkeeping for meals and labels**
- Per component: exposure count, completed re-checks, current label and when it was shown, last date
  served (no repeats within 7 days).
- Recent intense or multi-family symptoms (switches to rest meals).

## Learning mechanism

1. Every family confidence starts at the same 4%, raised for what the person said at onboarding.
2. Each night, two kinds of evidence move it:
   - **Expected reactions.** For every hour after eating a component, a real trigger would have had some
     chance to cause a reaction. That expected amount is subtracted from the log-odds, whether or not a
     symptom happened. A full serving whose whole window passes lowers the odds by the factor
     $1 - s_f \times e$.
   - **A symptom.** For each symptom in the past 24 hours, the model looks back 36 hours (48 for SKIN). Each component
     eaten in that window gains according to how much better it explains the symptom than the background
     and the other foods do, with each other food counted in proportion to how suspected it already is.
     A well-timed symptom gains more than its meal's expected reactions take away; a badly timed one
     gains less.
3. Within the night, tonight's evidence is applied, the confidences are recomputed, and tonight's
   evidence is re-scored with the new values until they settle. That lets blame move between foods
   eaten on the same day.
4. Blame from earlier nights stays where it was given (open item 7).

Example (simplified to whole days, onion the real trigger, rice eaten every day, 12 days): onion ends at
95% and rice at 14%. Rice keeps the blame it got early, before onion was suspected.

## Formulas

### Notation

| Symbol | Meaning |
|---|---|
| $c$, $d$ | a component (40 of them); $d$ is used for "another component" |
| $f$ | a symptom family: GI, SKIN or HEAD |
| $m$ | a meal, eaten at time $t_m$ |
| $j$ | a symptom, starting at time $t_j$, in family $f_j$ |
| $\mathcal{J}_f$ | the family $f$ symptoms logged since the last nightly update |
| $t_{\text{now}}$, $t_{\text{last}}$ | the time of tonight's update and of the previous one (24 h apart) |
| $\delta$ | hours after a meal |
| $T_f$ | the meal lookback for family $f$: 36 h for GI and HEAD, 48 h for SKIN |
| $i$ | an ingredient in a meal |
| $\text{level}_{i,c}$ | how much of component $c$ ingredient $i$ contains, from the ingredient map (1–3) |
| $g_i$, $g^{\text{serv}}_i$ | grams of ingredient $i$ eaten, and grams in its standard serving |
| $e_{m,c}$ | exposure: how much of $c$ meal $m$ contains, 0 to 1 (1 = a full serving) |
| $s_f$ | reaction chance: how often a real trigger causes a family $f$ symptom after a full serving |
| $k_f(\delta)$ | timing curve: how densely family $f$ reactions start $\delta$ hours after a meal (per hour; area 1) |
| $K_f(a, b)$ | the share of family $f$ reactions that start between $a$ and $b$ hours after a meal |
| $M$, $\sigma$ | a log-normal curve's median delay (hours; half of reactions start before it) and spread (how much delays vary) |
| $g(\delta; M, \sigma)$ | the log-normal curve with median $M$ and spread $\sigma$ |
| $G(\delta; M, \sigma)$ | the share of that curve before $\delta$ hours |
| $\Phi$ | the standard normal cumulative function |
| $\pi_f$ | for SKIN, the share of reactions that are early (0.5) |
| $a_{m,c,f}$ | meal strength: expected family $f$ reactions from meal $m$ if $c$ is a real trigger |
| $\Delta_{m,f}$ | the share of meal $m$'s timing curve that fell between the last update and tonight |
| $R_{c,f}$ | expected reactions: running total of $a \times \Delta$ over all meals containing $c$ |
| $P_{j,c}$ | pull: if $c$ is a real trigger, its rate of pushing towards symptom $j$ at time $t_j$ |
| $S_j$ | total pull at symptom $j$: background plus every component, each weighted by its confidence |
| $O_{j,c}$ | the pull at symptom $j$ from everything except $c$ |
| $p_0$ | starting family confidence, 0.04 |
| $w_c$ | onboarding multiplier for $c$: 1, ×3 if suspected, × any condition boost |
| $\ell_{c,f}$ | family confidence written as log-odds (so evidence adds instead of multiplying) |
| $q_{c,f}$ | family confidence, 0 to 1 |
| $Q_c$, $Q_G$ | component confidence, and group confidence for an always-together group $G$ |
| $\lambda_f$ | background rate: family $f$ symptoms per hour with no food cause |
| $\text{daily}^0_f$ | starting background chance per day: GI 0.20, SKIN 0.11, HEAD 0.15 |
| $\lambda^0_f$ | the starting background rate per hour |
| $B_f$ | running total of family $f$ symptoms put down to background |
| $H$ | hours since onboarding |
| $n_c$ | exposure count: meals with $e_{m,c} \ge 0.34$ whose 48 h have passed |

### Constants

| Symbol | Value |
|---|---|
| $p_0$ | 0.04 |
| $s_f$ | GI 0.40, SKIN 0.30, HEAD 0.25 |
| $\text{daily}^0_f$ | GI 0.20, SKIN 0.11, HEAD 0.15 |
| Prior weight of the starting background | 168 h (one week) |
| Symptom lookback (per night) | 24 h |
| Meal lookback (per symptom), $T_f$ | GI 36 h, HEAD 36 h, SKIN 48 h |
| Timing curves | GI: $M = 4$, $\sigma = 0.8$. HEAD: $M = 8$, $\sigma = 0.8$. SKIN: half early ($M = 1$, $\sigma = 0.7$), half late ($M = 24$, $\sigma = 0.5$) |
| Meaningful amount | $e \ge 0.34$ |

### Exposure

Meal-level fat load and insoluble fiber load come from gram thresholds instead.

$$
e_{m,c} = \min\!\left(1,\; \sum_{i \in m} \frac{\text{level}_{i,c}}{3} \cdot \frac{g_i}{g^{\text{serv}}_i}\right)
$$

### Timing curve

Log-normal curves: the standard shape for delays that vary a lot, rising quickly to a peak and then
tailing off. Each is cut off at the family's lookback $T_f$ and rescaled so its area is 1.

$$
g(\delta; M, \sigma) = \frac{1}{\delta\, \sigma \sqrt{2\pi}} \exp\!\left(-\frac{(\ln \delta - \ln M)^2}{2\sigma^2}\right),
\qquad
G(\delta; M, \sigma) = \Phi\!\left(\frac{\ln \delta - \ln M}{\sigma}\right)
$$

GI and HEAD use one curve; SKIN mixes an early and a late one:

$$
k_{\text{GI}}(\delta) = \frac{g(\delta; 4, 0.8)}{G(36; 4, 0.8)}, \qquad
k_{\text{HEAD}}(\delta) = \frac{g(\delta; 8, 0.8)}{G(36; 8, 0.8)}
$$

$$
k_{\text{SKIN}}(\delta) = \frac{\pi\, g(\delta; 1, 0.7) + (1 - \pi)\, g(\delta; 24, 0.5)}{\pi\, G(48; 1, 0.7) + (1 - \pi)\, G(48; 24, 0.5)}, \qquad \pi = 0.5
$$

for $0 < \delta \le T_f$, and 0 otherwise. The share of reactions between $a$ and $b$ hours, used for
expected reactions, needs no integration: replace each $g$ in the numerator with $G(b) - G(a)$.

$$
K_f(a, b) = \int_a^b k_f(\delta)\, \mathrm{d}\delta
$$

| Family | Most common delay | 90% of reactions start between | Why |
|---|---|---|---|
| GI | 2 h | 1 and 15 h | Lactose breath tests peak 2–4 h after the drink; fructan and fructose challenges are read over about 3 h with a 24 h follow-up |
| HEAD | 4 h | 2 and 30 h | Food-linked migraine usually starts within a day, most often 1–12 h; one small chocolate study had a median of 22 h. Weakest evidence of the three |
| SKIN | about 1 h (early) and about 20 h (late) | 0.3–3 h early, 10–55 h late | Flushing and hives come within an hour or two; food-related eczema flares appear 6–48 h after eating, most often about 24 h (the European guideline checks at 24 and 48 h) |

The 48 h SKIN lookback keeps 96% of the SKIN curve; 36 h would lose about 10% of late flares. GI loses
0.3% beyond 36 h, HEAD 3%.

Timing sources: BMC Gastroenterology 2024 breath-test table; ClinicalTrials.gov NCT01776853 (fructose and
fructan challenge); HKU challenge study 10722/249354; Gibb et al. 1991 (chocolate); EuroGuiDerm dietary
interventions guideline 2022; Late eczematous reactions to food in children with atopic dermatitis
(Breuer et al. 2004).

### Meal strength

The expected number of reactions from one meal if $c$ is a real trigger. It is chosen so that the chance
of no reaction from that meal is exactly $1 - s_f\, e_{m,c}$.

$$
a_{m,c,f} = -\ln\!\left(1 - s_f\, e_{m,c}\right)
$$

### Starting values (at onboarding)

$$
\ell_{c,f} = \ln\frac{p_0}{1 - p_0} + \ln w_c, \qquad
\lambda_f = \lambda^0_f = \frac{-\ln\!\left(1 - \text{daily}^0_f\right)}{24}, \qquad
R_{c,f} = B_f = H = n_c = 0
$$

### Each night

**1. Expected reactions since the last update.** Every meal eaten in the past 24 h + $T_f$ adds the part of
its timing curve that fell in the past 24 hours.

$$
\Delta_{m,f} = K_f\!\left(\max(0,\; t_{\text{last}} - t_m),\; \min(T_f,\; t_{\text{now}} - t_m)\right)
\qquad (0 \text{ if the first is above the second})
$$

$$
\ell_{c,f} \leftarrow \ell_{c,f} - \sum_m a_{m,c,f}\, \Delta_{m,f}, \qquad
R_{c,f} \leftarrow R_{c,f} + \sum_m a_{m,c,f}\, \Delta_{m,f}
$$

Call the result $\ell^{\text{base}}_{c,f}$: last night's log-odds minus tonight's expected reactions.

**2. Pulls for tonight's symptoms.** For each symptom $j$ since the last update, binary-search the meals
eaten in the $T_{f_j}$ hours before it:

$$
P_{j,c} = \sum_{m:\; t_j - T_{f_j} \,\le\, t_m \,<\, t_j} a_{m,c,f_j}\; k_{f_j}\!\left(t_j - t_m\right)
$$

**3. Rounds.** Repeat until no $q_{c,f}$ changes by more than 0.001 (at most 200 rounds), starting from
$q_{c,f} = 1 / (1 + e^{-\ell^{\text{base}}_{c,f}})$ and last night's $\lambda_f$:

$$
S_j = \lambda_{f_j} + \sum_{c} q_{c,f_j}\, P_{j,c}, \qquad
O_{j,c} = S_j - q_{c,f_j}\, P_{j,c}
$$

$$
\ell^{\text{new}}_{c,f} = \ell^{\text{base}}_{c,f} + \sum_{j \in \mathcal{J}_f} \ln\!\left(1 + \frac{P_{j,c}}{O_{j,c}}\right),
\qquad
q_{c,f} \leftarrow \tfrac{1}{2}\, q_{c,f} + \tfrac{1}{2} \cdot \frac{1}{1 + e^{-\ell^{\text{new}}_{c,f}}}
$$

$$
\lambda_f \leftarrow \tfrac{1}{2}\, \lambda_f + \tfrac{1}{2} \cdot
\frac{168\, \lambda^0_f + B_f + \sum_{j \in \mathcal{J}_f} \lambda_f / S_j}{168 + H + (t_{\text{now}} - t_{\text{last}})}
$$

- $\ln(1 + P_{j,c} / O_{j,c})$ is the Bayesian evidence from symptom $j$: how much more likely the symptom
  is with $c$ as a real trigger than without it, given everything else that could explain it.
- $O_{j,c}$ is where blame moves between foods: a food that is already suspected makes $O$ large for its
  mealmates, so they gain little.
- $\lambda_f / S_j$ is background's share of symptom $j$.
- Moving halfway each round stops the values bouncing. Updating every $q$ at once, not one at a time,
  keeps always-together pairs equal.

**4. Store.** Keep the settled values and roll the running totals forward:

$$
\ell_{c,f} \leftarrow \ln\frac{q_{c,f}}{1 - q_{c,f}}, \qquad
B_f \leftarrow B_f + \sum_{j \in \mathcal{J}_f} \frac{\lambda_f}{S_j}, \qquad
H \leftarrow H + (t_{\text{now}} - t_{\text{last}})
$$

and add 1 to $n_c$ for every meal with $e_{m,c} \ge 0.34$ that reached 48 hours old in the past 24 hours.

**Sanity checks.** A full serving whose window passes quietly takes $-\ln(0.6) = 0.51$ off the GI
log-odds, multiplying the odds by 0.6. A GI symptom 4 h after a full serving with nothing else eaten
multiplies them by about 7.9 (pull 0.064/h against a background of 0.0093/h), so with that meal's
expected reactions the net is about 4.7×. The same symptom 30 h after the meal multiplies them by about
1.04, a net of 0.62×: badly timed symptoms count against a food.

### Component and group confidence

The chance that at least one of $c$'s three family relationships is real. It is always at least the
highest of the three, and small ones add up: three families at 4% give 11.5%.

$$
Q_c = 1 - \prod_{f} \left(1 - q_{c,f}\right), \qquad
Q_G = 1 - \prod_{c \in G} \left(1 - Q_c\right)
$$

### Meal choice

Candidate meals first pass hard filters: exclusions, allergies, confirmed triggers, and no repeats within
7 days. Then, judging only components at a meaningful amount ($e_{m,c} \ge 0.34$):

| Type | When | Rule | Pick |
|---|---|---|---|
| Rest (washout) | a symptom of intensity ≥ 7, or 2 families within 24 h | every component has $Q_c \le 0.15$ | fewest components at a meaningful amount |
| Re-check (rechallenge) | some $Q_c \ge 0.60$, with fewer than 2 completed re-checks | that component at $e \ge 0.67$; all others $Q \le 0.15$ | test-recipe builder, as today |
| Explore | otherwise | at most one component with $Q_c \ge 0.30$ | highest explore score |

$$
\text{score}(m) = \sum_{c:\; e_{m,c} \ge 0.34} \frac{1}{1 + n_c}
$$

Ties go to the meal with fewer components at a meaningful amount, which keeps blame easier to assign.

### Labels

Shown every 7 days at local midnight:
- Looks fine: $Q_c \le 0.05$ and $n_c \ge 3$. Goes back to Still learning if $Q_c$ rises above 0.30.
- Likely trigger: $Q_c \ge 0.90$ and a completed re-check.
- Always-together groups (the taxonomy's list of pairs that can't be separated) are labelled as the group,
  using $Q_G$, never member by member.
- No clear food pattern: at least 60% of components look fine and none has $Q_c \ge 0.30$.

## Steps

At onboarding:
1. Record conditions, suspected foods and exclusions; set the starting values.

Every night:

2. Take the symptoms logged since the last update; merge same-family symptoms within 3 hours.
3. Subtract the expected reactions for the past 24 hours from every meal eaten in the past 60 hours
   (72 for SKIN).
4. For each new symptom, binary-search the meals in the 36 hours before it (48 for SKIN) and compute the
   pulls.
5. Run the rounds until the confidences and background rates settle; store them and roll the running
   totals forward.
6. Combine into component confidences.
7. Pick the meal type, filter the candidates, pick the best meal, and show its ingredient list and recipe.

Every 7 days:

8. Update the labels and show them.

## Diagram

```
 ONBOARDING                    FOOD AND SYMPTOM LOGS
 conditions, suspicions        meals                        symptoms
      |                          |                             |
      |                   ingredient map                 symptom map
      |                   (levels 1-3)                   (location + sensation)
      |                          |                             |
      v                          v                             v
 starting values          meal events                   symptom events
 (4%, raised by           (time, exposures)             (time, family)
 onboarding)                     |                             |
      |                          |                   symptoms from the past 24 h
      |                          |                             |
      |                          v                             v
      |              expected reactions for        meals in the 36 h (SKIN 48 h)  
      |              meals in the past 60 h        before each symptom -> pulls   
      |                          |                             |
      |                          +-------------+---------------+
      v                                        v
 stored state  --------------------->   NIGHTLY UPDATE   <-------------+
 (log-odds, background,                120 family confidences +        | repeat until
  running totals)  <-----------------  background, using each other    | settled
                         store                 |                       |
                                               +-----------------------+
                                               |
                      +------------------------+------------------------+
                      v                                                 v
         family confidences (120)  ------------------------>  component confidences (40)
                [hidden]                                              [hidden]
                                                                         |
                                           +-----------------------------+
                                           v                             v
                                      MEAL CHOICE                  WEEKLY LABELS
                              rest / re-check / explore      looks fine / likely trigger /
                                           |                 still learning / no pattern
                                           v                          [visible]
                               ingredient list + recipe
                                       [visible]
                                           |
                                           +----> eaten and logged (loop)
```

## Assumptions

1. **Starting confidence.** Every family confidence starts at 4%, the same for every food and family. That
   gives a component confidence of about 11.5%, an expected 4 to 5 trigger foods per person, and almost
   nobody with none (open item 1).
2. **Onboarding raises starting odds.** Suspected ×3 (component confidence about 30%); IBS ×2 for FODMAP
   components (about 21%); IBD ×1.5 for fat load, insoluble fiber and lactose (about 17%); celiac ×1.5
   for oats.
3. **Families.** Each of a component's three family confidences is learned separately. No food is assumed
   to favour any family.
4. **Reaction chance.** Fixed per family and the same for every food: GI 40%, SKIN 30%, HEAD 25% after a
   full serving, scaled by amount below that. It only sets how far one symptom or one quiet meal moves a
   confidence. Reasoning below; open item 5.
5. **Timing.** Log-normal curves from the evidence above: GI most often about 2 h after eating, 90% within
   1–15 h; HEAD most often about 4 h, 90% within 2–30 h; SKIN half early (within about 3 h) and half late
   (10–55 h, most often about a day).
6. **Background rate.** Each family has a non-food symptom rate, estimated from the logs.
7. **Triggers act independently.** Two triggers in one meal each have their own chance to cause a
   reaction. Combination effects are out of scope.
8. **No log means nothing happened.** If a symptom wasn't logged, the person didn't have one; a meal that
   wasn't logged doesn't exist for the model.
9. **Always-together pairs** (gluten and wheat fructans; lactose and milk protein) can't be told apart
   and are reported as a group.
10. **Check meals aren't announced.** Onboarding says some dinners re-check foods, without saying which.

### Reaction chance: reasoning

No study measures this number directly ("after a full serving of a real trigger, how often does a reaction
follow?"), so these values are a judgment from blinded challenge studies. The current build's 70/60/50 was
a placeholder.

- **Intolerance reactions are far less reliable than people's own reports.** In blinded gluten challenges
  of people who report gluten sensitivity, only 16–30% react specifically to gluten, and 36–40% react to
  placebo (Lionetti et al. 2017; Skodje et al. 2018).
- **They depend on dose.** Most people who can't digest lactose tolerate about 12 g (a cup of milk) with
  little or no difference from placebo; a 50 g load causes symptoms in most (Suarez & Savaiano 1995;
  Shaukat et al. 2010). A typical serving sits at the low end of that range.
- **FODMAP reactions are partial.** In a blinded reintroduction trial, IBS patients reacted to about 2
  FODMAP groups each, and effects showed up as group averages rather than a reaction every time.
- **Skin.** In children with eczema, late flares make up roughly 25–45% of positive food challenges in
  selected groups, and some hospital cohorts see almost none.
- **Head.** Migraine triggers are the least reliable: self-reported natural triggers provoked attacks in
  11% of migraine-with-aura patients, and controlled chocolate studies mostly find no difference from
  placebo. Headaches also depend on sleep, stress and hormones, not food alone.

So GI (dose-dependent and the best-studied) gets the highest value, 40%; SKIN 30%; HEAD the lowest, 25%.

What the change does:
- One quiet full serving now takes a food from 11.5% to about 8% (it was 4.8%). Three quiet servings take
  it to about 4%, so "Looks fine" arrives around the 3-serving minimum instead of after one meal.
- A real trigger that reacts 30% of the time is no longer typically cleared after 10 servings.
- Each single symptom counts for less, so strong triggers need a few more exposures to reach Likely
  trigger.

Sources: Lionetti et al., Frontiers in Physiology 2017 (gluten re-challenge meta-analysis); Skodje et al.,
Gastroenterology 2018 (fructan vs gluten); Suarez & Savaiano, NEJM 1995; Shaukat et al., Annals of Internal
Medicine 2010; Clinical Gastroenterology and Hepatology 2024 (FODMAP reintroduction trial); Hougaard et al.
2013 (migraine provocation); Nutrients 2020 (chocolate and migraine review); atopic dermatitis challenge
series (PMC3354259).

## Checks

- **Exact comparison.** For small test cases (up to about 16 family relationships), list every on/off
  combination and compute the exact confidences by brute force with the same timing and pull formulas.
  Report the gap on a fixed set of scenarios: a staple eaten daily with a real trigger, two triggers in
  different families, mixed meals, and an always-together pair (which must stay equal). The nightly
  update is expected to trail the exact answer where early blame went to the wrong food (open item 7).
- **Simulation.** Run the old and new models on the same simulated people, generated two ways (from the
  old family profiles, and with triggers spread evenly), against the same success criteria. Include
  simulated people whose real triggers react less often than the assumed reaction chance, and people who
  skip logging some days.

## What changed from the current build

| | Current build | v2 |
|---|---|---|
| What is learned | 38,501 explanations; at most 2 triggers | 120 family confidences; any number of triggers |
| Headline number | P_trigger | component confidence (same meaning, now computed from family confidences) |
| Time | 3-hour bins | exact times; meals found by binary search in the 36 h (SKIN 48 h) before each symptom |
| Update | whole history each day | incremental: symptoms from the past 24 h, added to stored values |
| Missing logs | time without a confirmed log is skipped | no log means nothing happened |
| Starting weight per component | tier (high/medium/low) × onboarding boosts | the same 4% × onboarding boosts |
| Which families a component affects | per-component profile | learned separately, no profile |
| Background rate | averaged over a fixed grid | estimated from the logs |
| Reaction chance | GI 70%, SKIN 60%, HEAD 50% | GI 40%, SKIN 30%, HEAD 25% |
| What the phone shows | a recipe | an ingredient list and a recipe |
| Explore meals | highest information gain | least-explored components first, fewer components breaks ties |
| No clear food pattern | P(no trigger) ≥ 0.80 and 60% look fine | 60% look fine and none ≥ 0.30 |
| Timing curves | 3-hourly steps; SKIN over by 24 h | log-normal curves; SKIN adds late flares, 48 h lookback |
| Exposure, meal-type thresholds, label thresholds, weekly reveal | | unchanged |

## Open items

1. **Starting confidence.** 4% assumes 4 to 5 trigger foods per person and almost nobody with none; the
   current build assumes about one, with 25% having none. A lower value (about 1%) matches that, but then
   every food starts under the 5% "Looks fine" line and gets cleared too easily. Tune in simulation.
2. **Too sure of itself.** In tests the update runs a little overconfident (rice falls to 0% where the
   exact answer is 3%), so "Looks fine" may come early. Watch the dangerous-miss rate in simulation and
   tighten clearing if needed.
3. **Explore score.** It doesn't aim to split foods that are usually, but not always, eaten together.
4. **Clinician review** of the reaction chances, timing curves and background starting rates. The HEAD
   curve rests on the weakest evidence, and the SKIN early/late split (50/50) is a judgment.
5. **Reaction chance.** Now 40/30/25 from the evidence above (was 70/60/50, under which a trigger that
   reacts 30% of the time was typically cleared after 10 servings). Still a judgment: test it in simulation
   across real triggers that react 20–90% of the time, and consider learning one value per family per person
   later.
6. **Days without logs.** A skipped day counts as symptom-free, so it lowers the confidence of everything
   eaten the day before, including real triggers; meals that weren't logged leave symptoms to the
   background. Watch in simulation how much skipped days cost (in the current build's evaluation, missed
   logs were among the biggest costs, about 63 days of median time).
7. **Old blame stays.** Because each symptom is scored once, on the night it is logged, blame given to a
   food before another food was suspected is never taken back. In a simplified test (onion the real
   trigger, rice eaten daily) rice ended at 14% instead of 2%, so it never reaches Looks fine. A possible
   fix, not adopted: re-score the whole history once a week, before the labels are shown.
8. **Late entries.** A meal or symptom logged after the night that covers its time is never processed.
   Decide whether late entries are picked up the next night or ignored.

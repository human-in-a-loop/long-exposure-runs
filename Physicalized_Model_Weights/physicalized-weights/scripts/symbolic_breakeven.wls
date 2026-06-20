(* created: 2026-05-13T02:07:00Z
   cycle: 1
   run_id: run-2026-05-13T015136Z
   agent: worker
   milestone: M-MODEL-1 *)

ClearAll[Nreq, fixedCost, cProg, cPhys, updateInterval, softwareSavings,
  analogPenalty, yieldPenalty, fallbackPenalty, delta];

delta = cProg - cPhys;
solution = fixedCost/(cProg - cPhys);

Print["N_break_even = ", TraditionalForm[solution]];
Print["N = 0 with fixedCost > 0 satisfies win inequality? ",
  FullSimplify[0 * delta > fixedCost, fixedCost > 0 && delta > 0]];
Print["fixedCost = 0 threshold: ",
  FullSimplify[solution /. fixedCost -> 0, delta > 0]];
Print["cProg <= cPhys finite positive break-even? ",
  FullSimplify[Resolve[Exists[Nreq, Nreq > 0 && Nreq * delta > fixedCost], Reals],
    fixedCost > 0 && delta <= 0]];
Print["updateInterval -> 0 qualitative penalty: fixed update cost proportional to 1/updateInterval diverges: ",
  Limit[fixedCost/updateInterval, updateInterval -> 0, Direction -> "FromAbove"]];
Print["softwareSavings = 0.5 raises threshold when programmable memory cost falls: ",
  FullSimplify[fixedCost/((cProg - 0.5) - cPhys) > fixedCost/(cProg - cPhys),
    fixedCost > 0 && cProg - cPhys > 0.5]];
Print["high analog penalties can remove positive denominator: ",
  FullSimplify[cProg - (cPhys + analogPenalty + yieldPenalty + fallbackPenalty) <= 0,
    analogPenalty + yieldPenalty + fallbackPenalty >= cProg - cPhys]];

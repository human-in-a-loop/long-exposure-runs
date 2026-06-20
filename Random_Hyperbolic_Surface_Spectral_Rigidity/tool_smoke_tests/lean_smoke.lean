import Init

theorem add_zero_smoke (n : Nat) : n + 0 = n := by
  exact Nat.add_zero n

#eval 2 + 3

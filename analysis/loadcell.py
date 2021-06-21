#!/usr/bin/python3

"""
Analysis for a 4 load cells (2 strain gauges each) wired to give a single differential output.
https://www.eevblog.com/forum/reviews/large-cheap-weight-digital-scale-options/
"""

def deltav(V, R, r0, r1, r2, r3):
  """return the differential output voltage for the 4x load cell"""
  i0 = V / (4.0 * R + r0 - r3)
  i1 = V / (4.0 * R - r0 + r3)
  va = i0 * (2.0 * R - r1 - r3)
  vb = i1 * (2.0 * R + r2 + r3)
  return va - vb

def main():

  Ve = 5.0
  Rn = 1000.0

  x = deltav(Ve, Rn, 1, 1, 1, 1)
  print(x)
  x = deltav(Ve, Rn, 0, 0, 2, 2)
  print(x)
  x = deltav(Ve, Rn, 0, 2, 2, 0)
  print(x)
  x = deltav(Ve, Rn, 0, 1, 3, 0)
  print(x)
  x = deltav(Ve, Rn, 0, 0, 3, 1)
  print(x)
  x = deltav(Ve, Rn, 1, 0, 0, 3)
  print(x)

main()

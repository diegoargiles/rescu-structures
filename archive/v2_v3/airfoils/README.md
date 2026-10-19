# Airfoil reference

`sd7037.dat` is the SD7037-092-88 coordinate file downloaded unchanged on 2026-10-07 from the [UIUC Airfoil Data Site](https://m-selig.ae.illinois.edu/ads/coord/sd7037.dat). The [database documentation](https://m-selig.ae.illinois.edu/ads/coord_database.html) describes the upper-trailing-edge, leading-edge, lower-trailing-edge ordering.

V3 normalizes the discrete minimum and maximum x coordinates to 0 and 1 before interpolation. The file's sampled minimum x is 0.00021. This prevents extrapolated negative thickness at the nose. The source file itself is not changed.

The tail uses the NACA four-digit thickness equation with thickness ratio 0.10. V3 explicitly substitutes the closed-trailing-edge coefficient -0.1036 for the standard finite-edge coefficient -0.1015. This is a geometric assumption to be checked against CAD, not a claim that it is the team's exact tail.

Do not replace the file with arbitrary CAD instructions. Export actual section points with units, axes and station identifiers; review their geometry before using them as model inputs.

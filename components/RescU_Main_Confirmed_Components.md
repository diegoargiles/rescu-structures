# RescU main component reference | updated 5 November 2026

The latest user correction confirms Molicel INR-21700-M65A cells and supersedes the intervening P26A link. Retain 6S2P. R11 already uses M65A references; no P26A CAD was generated.

| System | Team selection | Quantity and status |
|---|---|---|
| Lift motors | T-Motor AT2814 V2.0 long shaft, 1200 KV | 4 confirmed by Diego. Supersedes UM2807. 108 g each including cable, 432 g total. |
| Lift ESCs | T-Motor AIR 40A, 2-6S, no BEC | 4, one per lift motor. |
| Lift propellers | APC 9x4.5 and APC 10x3 | Board lists four of each. Treat as two sets for comparison. Installed set pending. |
| Pusher motor | T-Motor MT4008-18, 380 KV | 1. Board handwriting and earlier team presentation agree. |
| Pusher ESC | AT55A, 2-6S | 1, as written on board. |
| Pusher propeller | 13x8 | 1, APC per earlier team presentation. |
| Main battery | Molicel INR-21700-M65A lithium-ion, 6S2P | 12 cells total. Latest user correction restores M65A. Two physical modules remain a packaging proposal. |
| Flight controller | Cube Orange | PX4 is listed for flight software. Pixhawk is also written under avionics. Count one controller pending final carrier-board details. On 5 November Diego confirmed dimensions/models are not yet available; use adjustable provisions. |
| Backup RC receiver | RadioMaster, appears to read R86C V2 | Exact suffix needs verification before selecting a CAD footprint. |
| V-tail servos | Hitec, appears to read HS-5085MG, metal gear | 2. Whiteboard mass reads 21.9 g each, 43.8 g total. Verify model suffix and installed linkage mass. |
| Camera payload | IR camera | Model, mounting interface and mass pending. |

## Battery quantities: restored M65A baseline

Molicel lists 6.5 Ah typical and 3.6 V nominal per cell. The confirmed 6S2P pack is therefore 21.6 V nominal, 25.2 V fully charged, 13 Ah typical and 280.8 Wh nominal. Twelve bare cells give up to 894 g before interconnects, insulation, holders, connectors and protection hardware. Weigh the finished pack for CG.

The product page lists maximum diameter 21.7 mm, height 70.2 mm and mass 74.5 g. The public datasheet v0.1 dated 2025-08-05 instead lists maximum height 71.00 mm. Retain 71.00 mm in CAD until the discrepancy is resolved for the supplied cells. The datasheet's 26 A continuous rating includes a 90 C surface cut-off; installed pack current capability remains unqualified.

The earlier P26A comparison and smaller-tray proposal are superseded. No P26A geometry was applied to R11.

## R12 installation status: modeled and checked

RescU_R12_Service_Access_Review.zip supersedes the earlier R12 implementation proposal. M65A 6S2P remains the baseline. The R11 nose is retained and the first 6 mm of the front hatch opening, covered during nose restoration, is reopened with a matching smooth cover.

Narrow trays and under-floor saddles replace the obstructing side flanges. Fore/aft end fences use nominal M2 countersunk hardware and separate retained nut envelopes. Four nominal M2.5 retainers per bay are accessible from above after removing the battery. Fixed nominal end-stop positions are modeled; battery trim travel is not released.

Service order: open hatch, disconnect and park harness, release straps, lift module, undo the four exposed tray screws, lift empty tray. Wing joiner, receiver rails and anti-rotation pins remain installed.

Two fitted bonded lower nose frames now support the avionics deck, with slotted mounting strips as adjustable provisions. Actual carrier-board and receiver footprints, mounting hardware, isolation and connector access remain pending.

Completed checks: all feature shapes valid; 231 static intersection tests with no overlaps over 0.01 mm3; continuous 100 mm vertical removal envelopes for both complete loaded installations clear; eight straight 3.5 mm driver-shaft paths clear with the battery/pad removed from the access calculation. No hand/handle or actual strap-closure manipulation is certified.

The module packaging allowance remains provisional at 75 x 68 x 47 mm. Nominal centers are X=237.5 and 362.5 mm, Y=0, Z=1.25 mm. Each generic connector clearance is 10 x 12 x 10 mm above the forward end. These are layout assumptions, not measured finished pack or connector dimensions.

R12 adds 13.26 g relative to R11. The modeled nose/installation addition relative to R10 is 89.48 g, or 97.48 g with an 8 g allowance. Battery cells, electronics and wiring are excluded. These are incremental estimates, not total aircraft mass. Final aircraft CG, load qualification, hardware locking/thread engagement, strap closures and actual electronics fit remain unfinished.

The R12 generation, validation and export completed in separate short stages with project-local temporary storage. No automatic approval rejection occurred in this run. The origin of earlier reported telemetry remains unestablished. R10's unfinished pusher checks are not closed by this revision.

## Integration decision retained

T-Motor rates the selected 1200 KV motor for 3-4S. Direct operation from the confirmed 6S pack exceeds that rating even with the selected 2-6S ESC. Propulsion must resolve lift supply voltage before powered testing. Keep 17.3 N per motor as a provisional structural load case until thrust and current are established for the actual supply and propeller. Check aggregate current across the four lift motors and other active loads against pack capability. The motor maker lists 55 A peak for 180 s, so operating current with the chosen propeller also needs checking against the 40 A ESC.

Four lift motors alone account for 432 g. Replace the older 400 g all-motors-and-props placeholder when adding the pusher and propeller masses. Track the four ESCs against their existing accounting category to avoid double counting.

## References

- Current user-selected M65A cell: https://www.molicel.com/product/inr-21700-m65a/
- M65A datasheet v0.1: https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-M65A-80153-0.1_250805.pdf
- T-Motor AT2814: https://store.tmotor.com/product/at2814-long-shaft-fixed-wing-motor.html
- T-Motor AIR 40A ESC: https://store.tmotor.com/product/air-40a-6s-esc.html

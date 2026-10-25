# P07 CAD downloads and validation scope

Download RescU_P07_Native_CAD.zip for the constrained FreeCAD assembly and display macro. Download RescU_P07_SolidWorks_Review.zip for the whole wing/arm model without separate adhesive bodies. Download RescU_P07_Carrier_Review.zip for both arm/carrier views with opaque wing context removed. Extract each archive into this study folder. STEP has separate placed solids; FreeCAD joints do not become SolidWorks mates.

The full local STEP package additionally contains124 individual reinforcement-region exports; the local full review package contains all CAD and reports. Those larger convenience archives are delivered locally rather than duplicated in the repository. All exported component files are hashed in cad/ARTIFACT_MANIFEST.json; published archive identities are in publication_packages.json. Native CAD and compact STEP archives are versioned here.

**Review candidate only:** conservative spar-to-rib radial edge transfer demands12.255 MPa versus an assumed2 MPa screen. That screen fails; a larger developed face joint or another substantiated load path is required. See reports/REVIEW.md. Carrier/individual STEP quantity checks pass. Full-wing skin centroids have a documented small STEP/native discrepancy and remain reference geometry. Structural budget1,171.807 g, +14.135 g from P06; the separate200 g reserve is unchanged.

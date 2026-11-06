# CAD baseline and provenance

R12 source: `RescU_R12_Serviceable_Fuselage.FCStd`, from [RescU_R12_Service_Access_Review.zip](https://chatgpt.com/library?file_id=libfile_421c4a385ee0819187b0367b22cbe5e5&account_id=personal).

SHA256: `1998ebcfadd7398ea2b0075816696841f28581b3e9c6e186d92ef756a051b11e`.

R12 was inspected without overwriting it. `scripts/build_r13.py` consumes that exact baseline and creates a separate R13 candidate. `scripts/build_r14_socket_study.py` consumes R13 and saves a separate overlap study. Geometry and demand checks have explicit scopes; filenames do not imply structural acceptance.

See [FILE_MANIFEST.md](FILE_MANIFEST.md) for source hashes, download packages and directly committed exports. Full native assemblies and the large full-assembly STEP are in owner-access packages; they are not stored in Git or Git LFS at this checkpoint. Git contains build/check scripts, smaller added-parts STEP exports, review images and reviewed numerical records. Never count assembly containers or reference equipment/propeller reservations as structural material.

# CAD file manifest

R15 and R16 full-assembly STEPs are committed zipped (under GitHub's 100 MB file limit); the landing station STEP and STLs are committed directly. R13/R14 native assemblies and the large R13 STEP are distributed as package downloads. They are not in Git LFS or the ordinary clone. Package links require Diego's ChatGPT access; team sharing must be arranged separately.

| File / expected path | Bytes | In this commit | Access |
|---|---:|---|---|
| `cad/r13/RescU_R13_Layout_Candidate.FCStd` | 19364528 | No | [Versioned package](https://chatgpt.com/library?file_id=libfile_573f8c70636c8191aa2602bc7ac1c0de&account_id=personal) |
| `cad/r13/RescU_R13_Assembly.step` | 61581862 | No | [Versioned package](https://chatgpt.com/library?file_id=libfile_573f8c70636c8191aa2602bc7ac1c0de&account_id=personal) |
| `cad/r14_socket_study/RescU_R14_Socket_Overlap_Study.FCStd` | 19365401 | No | [Versioned package](https://chatgpt.com/library?file_id=libfile_4e62f1a569b08191858788317d0e35ea&account_id=personal) |
| `cad/r13/RescU_R13_New_Parts.step` | 675184 | Yes | [Repository file](../cad/r13/RescU_R13_New_Parts.step) |
| `cad/r14_socket_study/RescU_R14_Four_Wing_Sockets.step` | 73157 | Yes | [Repository file](../cad/r14_socket_study/RescU_R14_Four_Wing_Sockets.step) |
| `cad/r13/R13_Layout_Review.png` | 151111 | Yes | [Repository file](../cad/r13/R13_Layout_Review.png) |
| `reports/connection_study/Attachment_Annotated.png` | 153092 | Yes | [Repository file](../reports/connection_study/Attachment_Annotated.png) |
| `cad/r15/RescU_R15_Full_Aircraft.step.zip` | 19116359 | Yes | [Repository file](../cad/r15/RescU_R15_Full_Aircraft.step.zip) |
| `cad/r16/RescU_R16_Full_Aircraft.step.zip` (R16.2) | 32852237 | Yes | [Repository file](../cad/r16/RescU_R16_Full_Aircraft.step.zip) |
| `cad/landing_station/RescU_Landing_Station.step` | 2313028 | Yes | [Repository file](../cad/landing_station/RescU_Landing_Station.step) |
| `cad/landing_station/STL/Cradle_Boom_PETG_print_x2.stl` | 1418984 | Yes | [Repository file](../cad/landing_station/STL/Cradle_Boom_PETG_print_x2.stl) |
| `cad/landing_station/STL/Cradle_Tail_PETG_print_x1.stl` | 103784 | Yes | [Repository file](../cad/landing_station/STL/Cradle_Tail_PETG_print_x1.stl) |
| `cad/r16/R15_vs_R16_root_joints.png` | 377620 | Yes | [Repository file](../cad/r16/R15_vs_R16_root_joints.png) |
| `cad/landing_station/renders/S1_hero_seated.png` | 802580 | Yes | [Repository file](../cad/landing_station/renders/S1_hero_seated.png) |

## SHA-256 checksums

- `cad/r15/RescU_R15_Full_Aircraft.step.zip`: `98d974f6254f7c5d9b714094fc7aa949059c21c2ac6cae40c50d53d7a3f45bae`
- `cad/r16/RescU_R16_Full_Aircraft.step.zip` (R16.2; the R16 base zip `f1af144e…bdf2` is in commit `9d0ae2d`): `a3c8d2f809c7e1f86e92de328ec6b347932f6037b8255d97140efc99ad18387b`
- `cad/landing_station/RescU_Landing_Station.step`: `bbf5808aa012ff2a6ad94f5a1ece9c77643495361d099c53f3f5d26dd20b1649`
- `cad/landing_station/STL/Cradle_Boom_PETG_print_x2.stl`: `508fd57860cc0ecd649e7874d8d571889c526465de729b74e689eec98e0567e1`
- `cad/landing_station/STL/Cradle_Tail_PETG_print_x1.stl`: `03f9c45bbfb57776de8df07d5aff4c09e0a04634e9e97105c3472dd18ca45772`
- `cad/r16/R15_vs_R16_root_joints.png`: `34ce297b34bf42862162890a823206d42dee12c671e54e3e6b0a13a195508daf`
- `cad/landing_station/renders/S1_hero_seated.png`: `10430c13236f0ab72f25d07aa5b083af498bb750f085ffacc211576606516fee`

- `cad/r13/RescU_R13_Layout_Candidate.FCStd`: `a3dce4b9c3e0d9ba07f226cec989d9e6cf5a1c445e86b45c52cb9a1a2ab83ef7`
- `cad/r13/RescU_R13_Assembly.step`: `d013a68473c429608e30b0dbd89ad2dc310c788a834fad72f443eabcbf2b8baf`
- `cad/r14_socket_study/RescU_R14_Socket_Overlap_Study.FCStd`: `a11538af7ea76200404d203677b1203c0c749c8f3cf3d85e289b14d1f043638e`
- `cad/r13/RescU_R13_New_Parts.step`: `ad15fe7e43d73d51fdedf680b95f06e7c22fa9ae90e987ffcb566d7fb572996c`
- `cad/r14_socket_study/RescU_R14_Four_Wing_Sockets.step`: `e2bc4b97fb2e13d7d2906b56840d72cd07fc309eabc8d3fa2d852bebe3b61f14`
- `cad/r13/R13_Layout_Review.png`: `4cc7f481fed68155e776ac0e6ce62d4c0e801668e218e627274d8fe1d4918168`
- `reports/connection_study/Attachment_Annotated.png`: `b46b8f167f80b04f55bcbffac0668ac0131cafa20b0818965f2a97dbabe6009f`

Extract the R13/R14 native files from the packages into these expected paths before running CAD build/check scripts. Package directory prefixes may differ; preserve the filenames. All build scripts save a separate candidate rather than overwrite the baseline.

[Machine-readable manifest](file_manifest.json) · [Baseline](BASELINE.md) · [Current status](../docs/CURRENT_STATUS.md)

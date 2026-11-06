# CAD file manifest

Full native assemblies and the large full-assembly STEP are distributed as package downloads. They are not in Git LFS or the ordinary clone. Package links require Diego's ChatGPT access; team sharing must be arranged separately.

| File / expected path | Bytes | In this commit | Access |
|---|---:|---|---|
| `cad/r13/RescU_R13_Layout_Candidate.FCStd` | 19364528 | No | [Versioned package](https://chatgpt.com/library?file_id=libfile_573f8c70636c8191aa2602bc7ac1c0de&account_id=personal) |
| `cad/r13/RescU_R13_Assembly.step` | 61581862 | No | [Versioned package](https://chatgpt.com/library?file_id=libfile_573f8c70636c8191aa2602bc7ac1c0de&account_id=personal) |
| `cad/r14_socket_study/RescU_R14_Socket_Overlap_Study.FCStd` | 19365401 | No | [Versioned package](https://chatgpt.com/library?file_id=libfile_4e62f1a569b08191858788317d0e35ea&account_id=personal) |
| `cad/r13/RescU_R13_New_Parts.step` | 675184 | Yes | [Repository file](../cad/r13/RescU_R13_New_Parts.step) |
| `cad/r14_socket_study/RescU_R14_Four_Wing_Sockets.step` | 73157 | Yes | [Repository file](../cad/r14_socket_study/RescU_R14_Four_Wing_Sockets.step) |
| `cad/r13/R13_Layout_Review.png` | 151111 | Yes | [Repository file](../cad/r13/R13_Layout_Review.png) |
| `reports/connection_study/Attachment_Annotated.png` | 153092 | Yes | [Repository file](../reports/connection_study/Attachment_Annotated.png) |

## SHA-256 checksums

- `cad/r13/RescU_R13_Layout_Candidate.FCStd`: `a3dce4b9c3e0d9ba07f226cec989d9e6cf5a1c445e86b45c52cb9a1a2ab83ef7`
- `cad/r13/RescU_R13_Assembly.step`: `d013a68473c429608e30b0dbd89ad2dc310c788a834fad72f443eabcbf2b8baf`
- `cad/r14_socket_study/RescU_R14_Socket_Overlap_Study.FCStd`: `a11538af7ea76200404d203677b1203c0c749c8f3cf3d85e289b14d1f043638e`
- `cad/r13/RescU_R13_New_Parts.step`: `ad15fe7e43d73d51fdedf680b95f06e7c22fa9ae90e987ffcb566d7fb572996c`
- `cad/r14_socket_study/RescU_R14_Four_Wing_Sockets.step`: `e2bc4b97fb2e13d7d2906b56840d72cd07fc309eabc8d3fa2d852bebe3b61f14`
- `cad/r13/R13_Layout_Review.png`: `4cc7f481fed68155e776ac0e6ce62d4c0e801668e218e627274d8fe1d4918168`
- `reports/connection_study/Attachment_Annotated.png`: `b46b8f167f80b04f55bcbffac0668ac0131cafa20b0818965f2a97dbabe6009f`

Extract the R13/R14 native files from the packages into these expected paths before running CAD build/check scripts. Package directory prefixes may differ; preserve the filenames. All build scripts save a separate candidate rather than overwrite the baseline.

[Machine-readable manifest](file_manifest.json) · [Baseline](BASELINE.md) · [Current status](../docs/CURRENT_STATUS.md)

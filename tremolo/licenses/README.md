# Component notices

The built ZDL uses the reference project's `own_runtime=True` path at commit
`32f3d6877d892409c6defeeeec57040ad004d31f`. Its `build/runtime/dll.asm`
and UI handlers are covered by [runtime-MIT.txt](runtime-MIT.txt), subject
to the component exclusions stated there. TI call-stub and push/pop portions
carry [TI-RTS-NOTICE.txt](TI-RTS-NOTICE.txt); retain these notices with binaries.

[upstream-NOTICE.txt](upstream-NOTICE.txt) preserves the reference project's
license scope and exclusions. Its older statements about embedded stock code
refer to the old linker path; DmTrem explicitly uses `own_runtime=True`
and does not read or distribute the stock Zoom handler/RTS blobs. This is
source-path evidence; a binary-window comparison against proprietary stock
blobs was not run because those files are not present.

The TI compiler, installer and Ziddle source remain external/local and are
not included in this repository. Their own terms apply. No license grant
for proprietary Zoom firmware or effects is implied.

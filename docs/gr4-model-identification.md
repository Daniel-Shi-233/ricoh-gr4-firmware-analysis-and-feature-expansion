# GR IV family model identification

Resource existence cannot identify the body: all three shutdown files were present on the tested Monochrome. Writing GoodBye.jpg on HDF changed a file but not the visible screen; targeting GB_HDF.jpg corrected it.

| Product ID | Output | Target under A:\Resource\Jpeg |
| --- | --- | --- |
| 0x132E0 | STANDARD | GoodBye.jpg |
| 0x132E1 | HDF | GB_HDF.jpg |
| 0x13330 | MONO | GB_Mono.jpg |

## Read-only identification

With Script enabled, save any existing script/startup.ttl and copy examples/identify-gr4-model.ttl.example there. Archive/remove old AUTOMOD.TXT first to avoid mistaking a stale result for a new run. Start normally once, wait for storage activity to finish, shut down and inspect AUTOMOD.TXT. Restore the previous entry afterward as needed.

The example reads exactly eight bytes, one byte at a time, from E:\BlkCtl15.bin. It checks little-endian magic A55A5AA5 and an exact product allowlist. It writes only STANDARD, HDF, MONO or UNKNOWN to C:\AUTOMOD.TXT. No internal writes, installation, serial-number export, memory access or engineering commands occur. Unknown input must not select an installer. Logging failure may leave no fresh output. The backend's short-read/error reporting is imperfect; header checks are not an authenticity guarantee.

`tools/gr4_model.py` exposes `identify_header(eight_bytes)` returning `(label, target_path)` or `None` for host tooling. It never contacts a camera. A dispatcher can use these exact labels to choose a separately reviewed workflow; never default UNKNOWN to Standard or overwrite all targets.

## Evidence

On 2026-10-01, physical detection passed on ordinary GR IV, HDF and Monochrome research bodies. Standard and HDF were confirmed as 1.11; the precise Monochrome version was not recorded. Separate private automatic-dispatch rotation trials passed Standard 6->7, HDF 1->2 and Mono 1->2. That installer and its private assets are outside this PR. These observations do not qualify all versions or factory-new installation.

Static analysis used decoded GR IV 1.11 SHA-256 c4e597c7c9ca1bc181b30e35139ed90a4fd876ddcca14f12be0e00b6702233ae. Selector 0x538e7d94 reads product data at +4; object setup at 0x5373026c and constructor 0x53740048 resolve E:\BlkCtl15.bin. Validation at 0x5372de64 checks the magic. Tables 0x53fe50d0, 0x53fe5220 and 0x53fe5180 contain Standard, HDF and Monochrome names. Addresses apply only to that payload. GetModelNumber is a diagnostic label, not a demonstrated TTL command. Synthetic Python tests are not firmware execution or hardware emulation.

## Image workflow boundary

Existing goodbye templates remain Standard-specific. Do not run their unchanged target on HDF/Monochrome. For a reviewed adaptation, use the selected path consistently for backup, replacement, readback and restore. Preserve the original for each body and model. A backup from an already modified target is not a factory original. Copying may leave stale trailing bytes; prefix equality is not whole-file equality. Detection alone does not verify JPEG compatibility.

No firmware, resource artwork, device readbacks, manufacturing dumps, serials or private media are contributed. See LICENSE and CONTRIBUTING.md.

## Related model-specific work

[PR #2](https://github.com/radium-wang/ricoh-gr4-firmware-analysis-and-feature-expansion/pull/2) documents GR IIIx Urban 1.60 and is already merged. It uses a different resource drive, factory entry and transfer workflow. This GR IV-family header detector does not establish support for GR IIIx; keep those workflows separate.

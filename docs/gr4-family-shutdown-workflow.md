# Automatic GR IV / HDF / Monochrome single shutdown image

This workflow detects the camera model automatically, backs up its shutdown image, generates a replacement package, verifies complete readbacks and prepares restoration. It installs one persistent image, **not rotation**. No firmware update is involved.

## Requirements and evidence

Use a FAT32 card, Python 3.10+ and Pillow (`python3 -m pip install Pillow`). Script must be enabled through the existing factory-menu procedure; see the main README. Keep adequate battery charge. Full installation from exFAT is not supported by this workflow.

Identification and each target path were physically tested on three research bodies. Standard and HDF were 1.11; the exact Mono version was not recorded. **This new generated workflow, one-shot guard and automatic JPEG fitting are offline-tested, not an end-to-end camera-qualified release.** A successful desktop decode does not prove camera JPEG acceptance. Check the actual display after the full readback check.

Use a dedicated backup/package per physical body. Model detection does not identify an individual camera or its firmware. Before starting on another body, archive all previous outputs and remove old GBMODEL.TXT, GBSTD.JPG, GBHDF.JPG, GBMONO.JPG, GBREAD.JPG, GBREST.JPG and GBARM.TXT from the working card only after saving them elsewhere. Never reuse one body's original on another body of the same model. The tools do not format, locate or write a card automatically.

## 1. Automatically identify and back up

From the repository root:

```sh
python3 tools/gr4_shutdown.py backup ./stage-backup
```

Save any existing card startup script, then copy `stage-backup/script/startup.ttl` to the card as `script/startup.ttl`. Safely eject and start the camera normally once. Wait for storage activity to finish, shut down and reconnect the card.

The card now contains `GBMODEL.TXT` and one original: `GBSTD.JPG`, `GBHDF.JPG` or `GBMONO.JPG`. Open the JPEG and confirm it is the expected original. Copy both files to a new per-camera folder on the computer before continuing. Existing backup filenames are never overwritten. An UNKNOWN result, missing output or unexpected original is a stop condition. A backup of an already customized image is not the factory original.

## 2. Prepare and replace one image

Use a 720x480 image, e.g. your own PNG or JPEG. Substitute your mounted card path for `/path/to/card`:

```sh
python3 tools/gr4_shutdown.py prepare /path/to/card ./my-image.png ./my-camera-package
```

No model argument is needed. The tool reads the model report and decodes the original, then encodes a baseline 4:2:0 JPEG, trying quality 95 down to 5 until it can fit the original byte length. It uses the existing COM-padding helper to reach **exactly** that length; it never pads or modifies the saved original. Check `jpeg_quality` in manifest.json and open NEWGB.JPG before using it. Very detailed artwork may not fit a small original; the tool stops rather than enlarging the target. Use simpler artwork if needed. Metadata is not retained in the generated replacement.

The output directory must be new or empty. Keep the whole package on the computer. Copy only `NEWGB.JPG`, `GBARM.TXT` and `script/startup.ttl` from it onto the same camera's card. Keep the original backup already on the card. Archive/remove any old GBREAD.JPG first. Do not copy restore.ttl as the active entry yet.

Safely eject, start normally once, wait for activity to finish and shut down. The script detects the model again, rejects a mismatch, checks source/backup/current-target lengths, consumes and rereads the one-shot permit, writes the matching resource and exports `GBREAD.JPG`. It does not rotate images. It will not retry automatically, even if a readback copy fails. These are guards, not atomic power-loss protection or on-camera cryptographic checks.

## 3. Verify and finish

```sh
python3 tools/gr4_shutdown.py verify ./my-camera-package /path/to/card/GBREAD.JPG
```

This checks the entire file length and SHA-256 against the saved replacement, and checks that the saved original is unchanged. A prefix match with trailing bytes is not accepted. If verification fails, stop; archive the output and investigate or use the preserved original. Do not repeatedly re-arm an uncertain write.

Once verification passes, also confirm the visible shutdown picture. Remove the active startup script (or restore the previous one only if it does not overwrite this image), set Script back to Disable if no other feature needs it, and confirm a normal power cycle. Retain the complete package and original separately. The image remains until another operation replaces it.

## Restore this body's original

```sh
python3 tools/gr4_shutdown.py restore ./my-camera-package ./stage-restore
```

Use only the same physical camera. Keep a second original copy; archive/remove old GBREST.JPG. Copy the generated original backup, GBARM.TXT and script/startup.ttl to the card. Enable Script, safely eject, start once, wait and shut down. Then:

```sh
python3 tools/gr4_shutdown.py verify ./my-camera-package /path/to/card/GBREST.JPG --restore
```

Confirm the original display and remove the restore entry afterward. The restore gate requires the current target to have the original length; it stops if unrelated operations changed that length. No automatic deletion, truncation or forced recovery is attempted. Interrupted writes may require individual diagnosis.

## Technical boundaries

See [model identification](gr4-model-identification.md) for product IDs and target mapping. The camera checks lengths only; host verification checks complete hashes. The tool cannot detect a same-model camera swap, authenticate manufacturing data or recover an original that was never backed up. No copyrighted/private artwork, firmware or actual camera dumps are distributed. GR IIIx Urban uses a different workflow documented separately.

<!-- License: see LICENSE (earlier Apache-2.0 grants remain in force) -->

# Ricoh GR IV Firmware Analysis and Feature Expansion

[English](#english) · [简体中文](#中文)

## English

This project documents GR IV firmware format research, USB/MTP capabilities, factory-menu findings, and a shutdown-image replacement workflow tested on one camera.

It includes example files to reproduce the factory-menu entry and shutdown-image replacement. It does **not** distribute camera firmware, extracted system files, camera readbacks, or brand artwork. The workflow was tested on one GR IV only. Camera modification carries a risk of data loss or device malfunction; back up the original file and verify each step.

### Tools and examples

**GR IIIx Urban Edition 1.60:** a separate [verified shutdown-image report and procedure](docs/gr3x-urban-160-shutdown-image.md) documents one successful camera test. It uses `B:` paths, `00078490.609`, an exact-size JPEG encoder and a two-step TTL generator with computer readback verification. Follow that model-specific report rather than the GR IV steps below. `tools/create_factory_entry.py --model gr3x-urban-160` selects its entry files; the default remains GR IV.

- `tools/inspect_firmware.py`: inspect a local firmware container and optionally decode its payload for offline analysis.
- `tools/mtp_probe_readonly.py`: query MTP device, storage, and object information. It has no upload or delete operation. Requires Python 3 and PyUSB (`python3 -m pip install pyusb`).
- `tools/ic_probe_readonly.swift`: enumerate camera devices with macOS ImageCaptureCore.
- `tools/create_factory_entry.py`: create the SD-card factory-menu entry files observed in this test.
- `tools/pad_jpeg.py`: add a JPEG COM segment to reach a target file size without changing the decoded image.
- `examples/`: TTL templates for backing up, writing, and reading back the shutdown image.

### Reproduce the shutdown-image replacement

Read [the research report](docs/firmware-and-shutdown-image-research.md) and [the research log](docs/research-log.md) first. These steps describe one tested GR IV setup and may not apply to other firmware or regional variants.

1. On your computer, create an empty folder representing the SD-card root and generate the factory-menu entry files:

   ```sh
   python3 tools/create_factory_entry.py /path/to/sdcard-root
   ```

   Copy `00078560.636` and `DEVELOP.MOD` to the SD-card root. With the camera off, hold MENU while powering it on to enter the factory menu. Change only the verified `Script` setting to Enable. Other items may affect calibration, hardware tests, or user data. Turn the camera off before removing the card to add the script.

2. Back up the original image first. Remove the card and connect it to your computer. Create a `script` directory on the card and copy `examples/backup-goodbye.ttl.example` into it as `script/startup.ttl`. Safely eject the card, reinstall it, start the camera normally once, then turn it off. The script copies the camera image to `GBBACK.JPG` in the card root. Remove the card and reconnect it to your computer; confirm the file exists and opens, and save another copy on your computer.

3. Put your own 720×480 JPEG in the card root as `NEWGB.JPG`. To avoid stale trailing bytes when a shorter file overwrites a longer one, make the replacement the same size as `GBBACK.JPG`:

   ```sh
   python3 tools/pad_jpeg.py NEWGB.JPG TARGET_BYTES NEWGB_READY.JPG
   ```

   Replace `TARGET_BYTES` with the byte length of `GBBACK.JPG` (`stat -f %z GBBACK.JPG` on macOS). Rename the result to `NEWGB.JPG`. The utility adds only a JPEG comment segment; it does not resample or change decoded pixels. It does not verify that the camera accepts the JPEG encoding. If the new image is larger, first test expansion and readback using a separate temporary path; do not assume another camera behaves the same way.

4. While the card is connected to your computer, replace `script/startup.ttl` with `examples/write-goodbye.ttl.example` and make sure `NEWGB.JPG` is in the card root. Safely eject the card and reinstall it. The script copies `NEWGB.JPG` to `A:\Resource\Jpeg\GoodBye.jpg`, then reads the target back to `GBREAD.JPG` on the card. Keep the battery charged, start the camera normally once, allow the script to run, then turn it off.

5. Reconnect the card to your computer. Compare the SHA-256 hashes of `NEWGB.JPG` and `GBREAD.JPG`, and inspect the image:

   ```sh
   shasum -a 256 NEWGB.JPG GBREAD.JPG
   ```

   If the hashes differ or the image does not display, stop and restore the backup. After a successful check, delete `script/startup.ttl`, set Script back to Disable through the factory menu, and confirm the image remains after a normal power cycle. You may then remove the entry files.

The backup script preserves an existing `GBBACK.JPG`; repeated startup cannot replace it with the modified image. The write script refuses to run without `GBBACK.JPG` or `NEWGB.JPG`, or when `GBREAD.JPG` already exists. Before another write attempt, archive the previous readback on your computer and remove only `GBREAD.JPG` from the card. Keep `GBBACK.JPG` throughout the process. These guards check existence only, not integrity or provenance; verify the backup opens and retain a second copy on your computer before writing. Copy failures still require manual inspection and SHA-256 verification. The new guards and restore script have been tested in an offline model, **not on a camera**; the earlier copy workflow was tested on one camera. Do not experiment with unknown factory-menu items.

### Restore the original shutdown image

With the card connected to your computer, confirm that `GBBACK.JPG` is the original backup from this camera and opens correctly. Archive any old `GBREST.JPG` and remove it from the card. Copy `examples/restore-goodbye.ttl.example` to `script/startup.ttl`. With Script enabled, safely eject the card, reinstall it, start the camera normally once, then turn it off. The script restores `GBBACK.JPG` to `A:\Resource\Jpeg\GoodBye.jpg` and reads it back to `GBREST.JPG`; it exits without writing if the backup is missing or that readback already exists.

Reconnect the card and run `shasum -a 256 GBBACK.JPG GBREST.JPG`. Both files must exist and their hashes must match. Check the shutdown image, remove `script/startup.ttl`, and set Script back to Disable. Retain the backup on your computer. If the replacement was longer than the backup, restoration may leave trailing bytes: do not treat a mismatched readback as success or pad/modify the original backup to hide the mismatch.

If the camera image was already overwritten without a backup, this feature cannot recover the lost original. A backup taken now contains the current image, not the factory image. Look for a prior SD-card/computer backup; do not assume a firmware update restores it. This repository does not distribute original camera artwork.

### Inspect a firmware package

```sh
python3 tools/inspect_firmware.py /path/to/fwdc248b.bin
```

Obtain firmware from an official source yourself; this repository does not distribute it.

### Disclaimer and license

Results are from a single-camera experiment and are not guaranteed for other bodies or firmware versions. Some factory-menu items can affect camera operation.

From the commit that introduces the [GR IV Project Noncommercial Source License 1.0](LICENSE), original project material released under that license may be used for personal learning, research, modification, and noncommercial redistribution. Commercial use requires prior written permission from the relevant copyright holders. This includes paid resale, paid installation or support, paid access to project features, and other use intended to generate revenue or commercial advantage. Calling a fee a donation does not change the restriction. **This is a source-available, noncommercial license, not an OSI-approved open-source license.** See the full [LICENSE](LICENSE), [NOTICE](NOTICE), and [contribution guide](CONTRIBUTING.md).

Earlier revisions, through commit [`a55a2c7`](https://github.com/radium-wang/ricoh-gr4-firmware-analysis-and-feature-expansion/tree/a55a2c7), were published under [Apache License 2.0](https://github.com/radium-wang/ricoh-gr4-firmware-analysis-and-feature-expansion/blob/a55a2c7/LICENSE). Those grants cannot be revoked retroactively; previously released material remains available under Apache-2.0, including unchanged portions carried into later revisions. The new restriction applies to newly licensed material from the license-change commit onward. It cannot stop commercial reuse of the earlier Apache-2.0 version.

Neither license grants rights to Ricoh, GR, or Hasselblad marks or to third-party firmware or artwork. The licenses do not remove responsibilities under local law, product warranties, or third-party rights. Warranty and liability terms may not have the same effect in every jurisdiction; seek legal advice for your circumstances.

---

## 中文

本项目记录 GR IV 固件格式、USB/MTP 能力、工厂菜单线索，以及在一台相机上验证的关机画面替换流程。

项目提供复现工厂菜单入口和关机图替换的示例文件，但不分发相机固件、解包后的系统文件、相机读回数据或品牌图稿。流程只在一台 GR IV 上验证，不能保证适用于其他机身或固件。改机存在数据丢失或设备故障风险；请备份原文件并逐步核对。

### 工具和示例

**GR IIIx Urban Edition 1.60：**新增[关机图替换实测报告与完整流程](docs/gr3x-urban-160-shutdown-image.md)，记录一台机身的成功结果，提供等长 JPEG 编码、两阶段 TTL 生成和电脑完整读回校验工具。它使用 `B:` 路径和 `00078490.609`，请按该机型报告操作。`tools/create_factory_entry.py --model gr3x-urban-160` 生成对应入口，默认仍为 GR IV；下方 GR IV 步骤不能直接用于 GR IIIx。

- `tools/inspect_firmware.py`：检查本地固件包，也可选解码载荷供离线分析。
- `tools/mtp_probe_readonly.py`：查询 MTP 设备、存储和对象信息，不提供上传或删除操作。依赖 Python 3 与 PyUSB（`python3 -m pip install pyusb`）。
- `tools/ic_probe_readonly.swift`：使用 macOS ImageCaptureCore 枚举相机设备。
- `tools/create_factory_entry.py`：生成本次实测使用的 SD 卡工厂菜单入口文件。
- `tools/pad_jpeg.py`：为 JPEG 添加 COM 段以补到目标文件长度，不改变解码图像。
- `examples/`：备份、写入和读回关机图的 TTL 模板。

### 复现关机图替换

请先阅读[研究报告](docs/firmware-and-shutdown-image-research.md)和[研究日志](docs/research-log.md)。以下步骤只对应一台 GR IV 的实测环境，其他固件或地区版本可能不同。

1. 在电脑上创建一个空目录作为 SD 卡根目录的临时副本，并生成工厂菜单入口文件：

   ```sh
   python3 tools/create_factory_entry.py /path/to/sdcard-root
   ```

   将 `00078560.636` 和 `DEVELOP.MOD` 复制到 SD 卡根目录。相机关机时按住 MENU 并开机进入工厂菜单。只将已经验证的 `Script` 选项改为 Enable；其他选项可能影响校准、硬件测试或用户数据。关机后再取出 SD 卡添加脚本。

2. 先备份原图。取出 SD 卡并接入电脑，在卡上创建 `script` 目录，将 `examples/backup-goodbye.ttl.example` 复制进去并命名为 `script/startup.ttl`。安全弹出卡，装回相机后正常开机一次，再关机。脚本会把机内图片复制为卡根目录的 `GBBACK.JPG`。取出 SD 卡并接回电脑，确认文件存在且可打开，并另存一份到电脑。

3. 将自己的 720×480 JPEG 放到卡根目录并命名为 `NEWGB.JPG`。为避免较短文件覆盖较长文件后残留旧尾部，建议让新图与 `GBBACK.JPG` 字节数相同：

   ```sh
   python3 tools/pad_jpeg.py NEWGB.JPG TARGET_BYTES NEWGB_READY.JPG
   ```

   将 `TARGET_BYTES` 替换为 `GBBACK.JPG` 的字节数（macOS 可用 `stat -f %z GBBACK.JPG` 查看），再把输出文件改名为 `NEWGB.JPG`。工具只添加 JPEG 注释段，不重采样、不改变解码像素；它不会验证相机是否接受该 JPEG 编码。如果新图更大，先在独立临时路径测试扩容和读回，不要假设其他机身的行为相同。

4. 卡接在电脑上时，将 `script/startup.ttl` 替换为 `examples/write-goodbye.ttl.example`，并确认 `NEWGB.JPG` 位于卡根目录。安全弹出卡并装回相机。脚本会把 `NEWGB.JPG` 写到 `A:\Resource\Jpeg\GoodBye.jpg`，再将目标读回到卡上的 `GBREAD.JPG`。保持电量充足，正常开机一次，等待脚本运行后关机。

5. 把卡接回电脑，比较 `NEWGB.JPG` 和 `GBREAD.JPG` 的 SHA-256，并检查图像：

   ```sh
   shasum -a 256 NEWGB.JPG GBREAD.JPG
   ```

   如果哈希不同或图像无法显示，停止后续操作并用备份恢复。确认成功后删除 `script/startup.ttl`，再通过工厂菜单把 Script 设回 Disable。正常开关机确认图像仍显示后，可移除入口文件。

备份脚本发现已有 `GBBACK.JPG` 就退出，避免重复开机把原图备份覆盖成修改后的图片。写入脚本在缺少 `GBBACK.JPG`、缺少 `NEWGB.JPG` 或已有 `GBREAD.JPG` 时退出。再次写入前，先在电脑上归档旧读回文件，再仅删除卡上的 `GBREAD.JPG`，始终保留 `GBBACK.JPG`。这些保护只检查文件是否存在，不能证明备份完整或确实是原图；写入前必须确认备份可打开，并在电脑上另存一份。复制失败仍需人工检查，SHA-256 校验仍在电脑上完成。新增保护和恢复脚本仅通过离线模型测试，**尚未在相机上验证**；此前复制流程在一台相机上实测过。不要试验用途不明的工厂菜单项目。

### 恢复原始关机图片

将 SD 卡接入电脑，确认 `GBBACK.JPG` 是这台相机修改前的原图备份且可正常打开。若卡上已有 `GBREST.JPG`，先归档到电脑并从卡上删除。将 `examples/restore-goodbye.ttl.example` 复制为 `script/startup.ttl`。保持 Script 为 Enable，安全弹出卡并装回相机，正常开机一次再关机。脚本把 `GBBACK.JPG` 写回 `A:\Resource\Jpeg\GoodBye.jpg`，再读回为 `GBREST.JPG`；没有备份或已有该读回文件时，不执行写入。

把卡接回电脑，执行 `shasum -a 256 GBBACK.JPG GBREST.JPG`，确认两个文件都存在且哈希一致。检查关机图显示后，删除 `script/startup.ttl` 并把 Script 设回 Disable，电脑上的原图备份继续保留。如果替换图比原图更长，恢复时可能残留尾部字节；读回哈希不同就不能视为成功，也不要修改或填充原始备份来掩盖差异。

如果此前已经覆盖机内图片且没有备份，新功能无法找回丢失的原图。此时再备份得到的是当前图片，并非出厂原图。请先查找旧 SD 卡或电脑上的备份；不能假设升级固件会恢复原图。本仓库不分发相机原始图稿。

### 检查固件包

```sh
python3 tools/inspect_firmware.py /path/to/fwdc248b.bin
```

固件需自行从官方来源获取；本仓库不分发固件。

### 免责声明和许可证

结果来自单台相机的实验，不保证适用于其他机身或固件。部分工厂菜单项目可能影响相机运行。

自引入 [GR IV Project Noncommercial Source License 1.0](LICENSE) 的提交起，按该许可证发布的项目原创内容允许个人学习、研究、修改和非商业再分发。商业使用须事先取得相关著作权人的书面许可，包括收费转售、收费安装或支持、收费提供项目功能，以及其他以获得收入或商业利益为目的的使用。把收费称作“捐赠”不改变限制。**这是可查看源码的非商业许可证，不再是 OSI 定义下的开源许可证。** 具体条款见 [LICENSE](LICENSE)、[NOTICE](NOTICE) 和[贡献指南](CONTRIBUTING.md)。

截至 [`a55a2c7`](https://github.com/radium-wang/ricoh-gr4-firmware-analysis-and-feature-expansion/tree/a55a2c7) 提交的旧版本已按 [Apache License 2.0](https://github.com/radium-wang/ricoh-gr4-firmware-analysis-and-feature-expansion/blob/a55a2c7/LICENSE) 发布；这些授权不能追溯撤销。旧版内容即使原样出现在后续版本中，原有 Apache-2.0 授权仍然有效。新限制适用于许可证切换提交起新授权的内容，无法禁止他人商业使用此前已按 Apache-2.0 发布的版本。

上述许可证均不授予 Ricoh、GR 或 Hasselblad 商标及第三方固件、图稿的权利，也不会免除当地法律、产品保修或第三方权利产生的责任。无担保及责任限制条款在不同司法辖区的效力可能不同；具体情况请咨询律师。

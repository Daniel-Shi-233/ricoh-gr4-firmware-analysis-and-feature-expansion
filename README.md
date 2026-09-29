<!-- SPDX-License-Identifier: Apache-2.0 -->

# Ricoh GR IV Firmware Analysis and Feature Expansion

[English](#english) · [简体中文](#中文)

## English

This project documents GR IV firmware format research, USB/MTP capabilities, factory-menu findings, and a shutdown-image replacement workflow tested on one camera.

It includes example files to reproduce the factory-menu entry and shutdown-image replacement. It does **not** distribute camera firmware, extracted system files, camera readbacks, or brand artwork. The workflow was tested on one GR IV only. Camera modification carries a risk of data loss or device malfunction; back up the original file and verify each step.

### Tools and examples

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

The TTL templates do not perform automatic error handling or hash verification. The operator must check the backup and readback. Do not experiment with unknown factory-menu items.

### Inspect a firmware package

```sh
python3 tools/inspect_firmware.py /path/to/fwdc248b.bin
```

Obtain firmware from an official source yourself; this repository does not distribute it.

### Disclaimer and license

Results are from a single-camera experiment and are not guaranteed for other bodies or firmware versions. Some factory-menu items can affect camera operation.

Original code and documentation in this repository are licensed under [Apache License 2.0](LICENSE), which permits use, modification, and redistribution and includes standard warranty disclaimers and liability limitations. The license does not grant rights to Ricoh, GR, or Hasselblad marks, and does not remove responsibilities under local law, product warranties, or third-party rights. See [NOTICE](NOTICE) and [Contributing](CONTRIBUTING.md). The license may not limit liability in every jurisdiction; consult a lawyer in your jurisdiction for advice about your circumstances.

---

## 中文

本项目记录 GR IV 固件格式、USB/MTP 能力、工厂菜单线索，以及在一台相机上验证的关机画面替换流程。

项目提供复现工厂菜单入口和关机图替换的示例文件，但不分发相机固件、解包后的系统文件、相机读回数据或品牌图稿。流程只在一台 GR IV 上验证，不能保证适用于其他机身或固件。改机存在数据丢失或设备故障风险；请备份原文件并逐步核对。

### 工具和示例

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

TTL 模板没有自动错误处理或哈希校验，操作者必须检查备份和读回文件。不要试验用途不明的工厂菜单项目。

### 检查固件包

```sh
python3 tools/inspect_firmware.py /path/to/fwdc248b.bin
```

固件需自行从官方来源获取；本仓库不分发固件。

### 免责声明和许可证

结果来自单台相机的实验，不保证适用于其他机身或固件。部分工厂菜单项目可能影响相机运行。

本仓库原创代码和文档采用 [Apache License 2.0](LICENSE)，允许使用、修改和再分发，并包含标准的无担保和责任限制条款。许可证不授予 Ricoh、GR 或 Hasselblad 商标权，也不会免除当地法律、产品保修或第三方权利产生的责任。请见 [NOTICE](NOTICE) 和[贡献指南](CONTRIBUTING.md)。该许可证不保证在所有司法辖区都能限制责任；如需针对个人情况的法律建议，请咨询当地律师。

<!-- SPDX-License-Identifier: Apache-2.0 -->

# Ricoh GR IV Firmware Analysis and Feature Expansion

记录 GR IV 固件包结构、USB/MTP 可见能力、工厂菜单线索，以及在一台自有 GR IV 上验证的关机图替换结果。研究说明和工具以中文编写。

本项目提供复现工厂菜单入口和关机图替换的示例文件，但不提供相机固件、解包后的系统文件、设备读回数据或品牌图稿。示例只在一台 GR IV 上验证；修改相机有设备风险，请先备份原文件并逐步核对。

## 工具

- `tools/inspect_firmware.py`：离线检查固件容器头部、版本字段、整文件校验，可选解码载荷供静态分析。
- `tools/mtp_probe_readonly.py`：查询 GR IV 的 MTP 设备、存储和对象信息；不提供上传或删除操作。依赖 Python 3 与 PyUSB（`python3 -m pip install pyusb`）。
- `tools/ic_probe_readonly.swift`：macOS ImageCaptureCore 设备枚举示例。
- `tools/create_factory_entry.py`：生成本次实测的 SD 卡工厂菜单入口文件。
- `tools/pad_jpeg.py`：将 JPEG 加入合法 COM 段，补到指定字节数而不改动解码图像。
- `examples/`：先备份、再写入并回读关机图的 TTL 示例。

## 复现关机图替换

请先阅读[固件与关机画面研究](docs/firmware-and-shutdown-image-research.md)和[研究日志](docs/research-log.md)。以下流程对应单台 GR IV 的实测版本，不保证适用于其他固件或地区：

1. 在电脑上为 SD 卡创建空目录，例如 `sdcard-root`，生成工厂菜单入口文件：

   ```sh
   python3 tools/create_factory_entry.py /path/to/sdcard-root
   ```

   把生成的 `00078560.636` 和 `DEVELOP.MOD` 放到 SD 卡根目录。将卡装回相机，关机状态下按住 MENU 并开机进入工厂菜单。只修改已确认的 `Script` 项为 Enable；其他选项可能影响校准、硬件测试或用户数据。

2. 先只做备份。把 `examples/backup-goodbye.ttl.example` 复制到卡上的 `script/startup.ttl`，正常开机一次后关机。脚本会把机内原图复制成卡根目录的 `GBBACK.JPG`。将卡接回电脑，确认备份文件存在、能正常打开，并另存一份到电脑。

3. 将你自己的 720×480 JPEG 放到卡根目录并命名为 `NEWGB.JPG`。为避免较短文件覆盖后残留旧数据，优先把输出长度补到 `GBBACK.JPG` 的实际字节数：

   ```sh
   python3 tools/pad_jpeg.py NEWGB.JPG TARGET_BYTES NEWGB_READY.JPG
   ```

   把 `TARGET_BYTES` 替换为 `GBBACK.JPG` 的文件长度（macOS 可用 `stat -f %z GBBACK.JPG` 查看），再将 `NEWGB_READY.JPG` 改名为 `NEWGB.JPG`。此工具只添加 JPEG 注释段，不重采样、不改解码像素；它不会替你检查相机是否接受该 JPEG 编码。如果新图比原文件长，应先在独立临时路径验证扩容和读回，切勿直接假定其他机型行为相同。

4. 将 `examples/write-goodbye.ttl.example` 复制到 `script/startup.ttl`。脚本会先将 `NEWGB.JPG` 复制到 `A:\Resource\Jpeg\GoodBye.jpg`，再把目标文件读回为卡根目录的 `GBREAD.JPG`。保持电量充足，正常开机一次，等待脚本运行后关机。

5. 将 SD 卡接回电脑，运行 `shasum -a 256 NEWGB.JPG GBREAD.JPG` 比较两者 SHA-256 并检查图像。哈希不一致或无法显示时停止后续操作，使用备份恢复。确认成功后删除 `script/startup.ttl`，再通过工厂菜单将 Script 设回 Disable。正常开关机确认图片仍显示后，可移除入口文件。

脚本不包含自动错误处理或哈希验证，读回和核对步骤必须由操作者完成。不要在未知工厂菜单项目上试错。

固件检查示例：

```sh
python3 tools/inspect_firmware.py /path/to/fwdc248b.bin
```

固件样本需自行从官方来源获取，本仓库不分发。详细方法、已知限制和实机结果见[固件与关机画面研究](docs/firmware-and-shutdown-image-research.md)及[研究日志](docs/research-log.md)。

## 免责声明与许可

结果来自一台相机的个案实验，不能保证适用于其他机身或固件版本。工厂菜单含有可能影响相机工作的选项，请勿在不了解用途时更改。

本仓库原创代码和文档采用 [Apache License 2.0](LICENSE)，允许使用、修改和再分发，并附有标准的无担保和责任限制条款。它不授予 Ricoh、GR 或 Hasselblad 商标权，也不会免除当地法律、产品保修或第三方权利产生的责任。请见 [NOTICE](NOTICE) 和[贡献指南](CONTRIBUTING.md)。许可证条款不保证在所有司法辖区都能限制责任；如需针对个人法律风险的建议，请咨询当地律师。

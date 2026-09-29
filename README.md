# Ricoh GR IV 固件与关机画面研究

记录 GR IV 固件包结构、USB/MTP 可见能力、工厂菜单线索，以及在一台自有 GR IV 上验证的关机图替换结果。研究说明和工具以中文编写。

**本项目不提供相机固件、解包后的系统文件、设备读回数据或写入脚本。** 所有相机修改均有设备风险；请只在自有设备上操作，并先做好原文件备份。

## 工具

- `tools/inspect_firmware.py`：离线检查固件容器头部、版本字段、整文件校验，可选解码载荷供静态分析。
- `tools/mtp_probe_readonly.py`：查询 GR IV 的 MTP 设备、存储和对象信息；不提供上传或删除操作。依赖 Python 3 与 PyUSB（`python3 -m pip install pyusb`）。
- `tools/ic_probe_readonly.swift`：macOS ImageCaptureCore 设备枚举示例。

固件检查示例：

```sh
python3 tools/inspect_firmware.py /path/to/fwdc248b.bin
```

固件样本需自行从官方来源获取，本仓库不分发。详细方法、已知限制和实机结果见[研究记录](docs/GR4_固件与关机画面研究.md)。

## 免责声明与许可

结果来自一台相机的个案实验，不能保证适用于其他机身或固件版本。工厂菜单含有可能影响相机工作的选项，请勿在不了解用途时更改。

本仓库未附开源许可证；除非作者另行书面许可，不授予代码再分发或改编权。商标与品牌图像归其各自权利人所有。

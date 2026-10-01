<!-- License: see LICENSE (earlier Apache-2.0 grants remain in force) -->

# GR IIIx Urban Edition 1.60: verified shutdown-image replacement

## English summary

A custom shutdown image was successfully displayed on **one GR IIIx Urban Edition running firmware 1.60**. The final target was read back in full and matched the replacement SHA-256; normal power cycles worked after removing `script/startup.ttl` and returning `Script` to `Disable`. No firmware was flashed. This report does not establish compatibility with standard GR IIIx, HDF, GR III, GR IV, or other firmware versions.

The GR IV examples cannot be used unchanged: this body uses **`B:\Resource\Jpeg\GB_Urban.jpg`**, factory entry **`00078490.609`**, and a different transfer method. Copies with an SD-card `C:` source repeatedly produced zero-byte destinations in this experiment. Internal `B:` sources worked. The successful approach embedded nonzero JPEG bytes as TTL literals into a fresh, zero-extended internal temporary file, verified three complete readbacks on the computer, then installed with a separate short `B:` → `B:` copy script. There are no interpreted checksum loops.

The successful JPEG was 720×480 RGB, baseline 4:2:0, exactly **107,902 bytes**, with the original JFIF/frame/scan parameters and no COM padding or additional metadata. This is a tested encoding profile, not proof that every other profile is rejected. The encoder below uses a bounded quantizer search; it can fail for other artwork and never guarantees camera decoding. Computer tools create local files only and do not locate or write an SD card.

The detailed Chinese procedure below includes original-backup prerequisites, separate staging steps, full readback verification, restoration, macOS cleanup, evidence, and limitations. The generated two installation scripts reproduce the successful scripts byte for byte for the tested private input. Consolidated backup/restore example guards and the new CLI wrappers have offline tests; the complete new backup/restore wrappers have not been run on the camera. This repository contains no firmware, extracted image, personal artwork, or camera readback.

## 实测范围与 GR IV 的区别

记录日期：2026-10-01。机身为 GR IIIx Urban Edition，菜单固件版本 1.60。离线检查的官方固件包头版本为 `1.60.11.17`。官方固件信息见 [Ricoh GR IIIx 支持页](https://www.ricoh-imaging.co.jp/english/support/digital/gr3x_s.html)。下载和分析固件只用于核对版本与行为；整个替换流程没有刷写固件。

| 项目 | 本次 GR IIIx Urban 1.60 | 项目原有 GR IV 示例 |
|---|---|---|
| 工厂菜单入口文件 | `00078490.609` + `DEVELOP.MOD` | `00078560.636` + `DEVELOP.MOD` |
| 关机图目标 | `B:\Resource\Jpeg\GB_Urban.jpg` | `A:\Resource\Jpeg\GoodBye.jpg` |
| 已验证的安装来源 | 机内 `B:` 临时文件 | 原示例的 SD 卡 `C:` 文件 |
| 本次 JPEG 策略 | 编码到原图等长，不添加 COM | 原工具提供 COM 填充 |

共享的 TTL 语法、工厂菜单研究、备份和读回思路有参考价值。盘符、资源路径、入口文件、复制行为和 JPEG 接受情况必须分别验证。不要把下述方法用于未验证机型，也不要把 GR IV 的 `A:` 路径直接改个名字后运行。

## 已成功的方法

1. 保存相机原始 Urban 图到 SD 卡和电脑，再建立并验证机内原图备份。
2. 将已准备好的 720×480 RGB 图稿编码成 107,902 字节的 JPEG，保留成功的结构。
3. 第一段 TTL 只创建机内新临时文件，不覆盖关机图；将新临时文件、原图备份、当前原图完整读到 SD 卡。
4. 在电脑上核对三份文件的完整 SHA-256，再换成第二段短脚本。
5. 第二段从机内临时文件复制到机内关机图，再完整读回；电脑核对内容，相机核对显示。
6. 删除启动脚本，把 `Script` 改回 `Disable`，确认正常开关机后清理入口和任务文件，保留备份。

TTL 的 `filewrite` 字符串接口无法直接写入嵌入的 NUL 字节。本次先在**不存在的新路径**创建空文件，再 `filetruncate` 到目标长度；该新文件扩展区域在实测中为零。生成器跳过 JPEG 中的零字节，对其他字节使用 `fileseek` 和最多 42 字节的 `#数值` 字面量写入。不要在已有文件上套用“跳过零字节”的写法，也不要复用已有临时文件：旧内容可能保留下来。

本次某些复制操作不会截断目标旧尾部，因此原图、新图、临时文件均保持 107,902 字节。长度一致只是前置条件，不能代替完整内容校验。

## 复现前的备份和菜单设置

请先备份 SD 卡上的照片，记录照片的相对路径、大小和修改时间；后续只处理这次任务的明确文件。保持电量充足。所有相机循环都要先安全弹出卡，关机后再取卡。

电脑上创建新的本地工作目录，例如 `gr3x-urban-local/`。该目录已加入 `.gitignore`；里面的原图、新图、读回数据和生成脚本不应提交到仓库。

```sh
python3 tools/create_factory_entry.py gr3x-urban-local/entry --model gr3x-urban-160
```

将生成的两个入口文件复制到 SD 卡根目录。相机关机时按住 MENU 并开机，进入 Factory Menu，只把 `FW Setting1 → Script` 改为 `Enable`。本次 `Camera Mode` 保持 `Normal`，其他项目不变。关机后再把卡接回电脑。不要用改校准、属性或硬件测试选项来处理复制问题。

将 [备份示例](../examples/gr3x-urban-backup.ttl.example) 以 ASCII、CRLF 字节写成卡上的 `script/startup.ttl`。该示例保留已存在的备份，拒绝重复覆盖已有 SD 输出，只接受 107,902 字节的目标。它用已实测的复制指令组合成带保护的新模板；完整模板仅在离线模型中测试过。安全弹出，正常开机，等进入拍摄界面且活动灯停止后关机，再接回电脑。

仓库模板使用 LF，复制前先在本地转成 CRLF；恢复模板同样处理。两阶段生成器的输出已是 CRLF，不要再次转换。

```sh
python3 - <<'PY'
from pathlib import Path
source = Path('examples/gr3x-urban-backup.ttl.example')
data = ('\r\n'.join(source.read_text(encoding='ascii').splitlines()) + '\r\n').encode('ascii')
with Path('gr3x-urban-local/backup-startup.ttl').open('xb') as output:
    output.write(data)
PY
```

再将本地 `backup-startup.ttl` 的字节复制为卡上的 `script/startup.ttl`。

备份阶段应得到：

- `URBANBK.JPG`：当前 `GB_Urban.jpg` 的完整读回。
- `URBOLD.JPG`：机内 `RB41OL.JPG` 的完整读回；该机内备份只在原先不存在时创建。

两份都必须是 **107,902 字节**，能打开，而且 SHA-256 都为：

```text
7a2154a6d24ed5e460d2a918783d593171e399562923da582801186098ffc89f
```

```sh
shasum -a 256 /path/to/card/URBANBK.JPG /path/to/card/URBOLD.JPG
```

把两份文件另外保存到电脑。若文件缺失、零字节、哈希不同，或相机之前已经修改过且没有原图备份，**停止**。刚从已修改目标取得的备份不是出厂原图。这里不提供原图下载，也不能保证升级固件会恢复它。生成器会拒绝不匹配的原图，而不会修改它来绕过校验。

## JPEG 编码：保持成功结构，严格等长

先自行准备 720×480、RGB 模式的 PNG 图稿。编码器不自动裁剪、缩放或重新设计图稿。编码需要 Python 3 和 Pillow；检查、生成脚本、读回校验不需要 Pillow。

```sh
python3 -m pip install Pillow
python3 tools/gr3x_urban_jpeg.py encode \
  gr3x-urban-local/URBANBK.JPG gr3x-urban-local/artwork.png \
  gr3x-urban-local/candidate.jpg
python3 tools/gr3x_urban_jpeg.py check \
  gr3x-urban-local/URBANBK.JPG gr3x-urban-local/candidate.jpg
```

成功编码的结构：

```text
SOI APP0(JFIF) DQT DQT SOF0 DHT DHT DHT DHT SOS entropy EOI
D8  E0         DB  DB  C0   C4  C4  C4  C4  DA          D9
```

JFIF、SOF0 和 SOS 载荷与原图完全相同，720×480、8 位、3 分量、4:2:0；没有 Exif、Photoshop、ICC、COM、DRI、重启标记或 EOI 后尾部。本次保持原 JFIF 分辨率声明，载荷为 `4a46494600010101004800480000`。

编码器从原图量化表与 Pillow quality 91 量化表之间选择参数，用固定随机种子搜索精确长度，最多 6,000 次尝试或 45 秒，失败不写输出。原图表在本次对应 quality 90。其他图稿可能无法在这个范围达到目标长度；应调整图稿后重新编码，不要把这次成功等同于任意图稿都会成功。Pillow/libjpeg 版本也可能影响结果。该方法有 JPEG 有损编码；并非像素无损。

`check` 只核对字节长度、标记结构和与原图相同的声明。编码器还做 Pillow 完整解码。它们不能证明硬件解码器会显示新图。此前“能在电脑打开、完整读回正确”仍出现关机停在当前预览帧的情况，显示必须独立实测。

## 第一段：只写临时文件，先读回验证

```sh
python3 tools/gr3x_urban_shutdown.py build \
  gr3x-urban-local/URBANBK.JPG gr3x-urban-local/candidate.jpg \
  gr3x-urban-local/package
```

输出目录必须是新的本地目录，不能直接位于 `/Volumes`。输出为：

```text
package/manifest.json
package/01-temporary-only/script/startup.ttl
package/01-temporary-only/URBLOG8.TXT             (空文件)
package/02-install-after-readback/script/startup.ttl
package/02-install-after-readback/URBLOG9.TXT     (空文件)
```

生成的 TTL 包含自己的图片全部字节，不要发布。第一段在开始前检查目标和原图备份长度、目标属性以及新临时文件不存在，复制原图和备份到卡，再写入 `B:\Resource\Jpeg\RB81NW.JPG`。没有覆盖关机资源的指令。空日志是一次运行的凭据：没有日志或日志非空时退出，防止重复执行。若同名临时文件已存在，不要强行覆盖；先归档并查明此前运行状态。

此时仅复制 `01-temporary-only` 里面的脚本和**空的** `URBLOG8.TXT` 到卡的对应路径，替换之前的备份脚本。不要一次把两个目录都复制到卡。正常开机运行、关机后接回电脑，将日志和三份完整读回复制到新的本地目录 `step1-readback/`：

| 文件 | 必须匹配 |
|---|---|
| `URBIMG8.JPG` | `candidate.jpg` 的完整 SHA-256 |
| `URBORG8.JPG` | 原图 SHA-256 |
| `URBPRE8.JPG` | 原图 SHA-256 |

```sh
python3 tools/gr3x_urban_shutdown.py verify \
  gr3x-urban-local/package/manifest.json gr3x-urban-local/step1-readback --step 1
```

验证器要求所有文件精确等长、完整哈希匹配，日志 `started=1,error=0,attempted=0,restored=0,completed=1`。缺文件、不匹配、日志中断或重复字段都会失败。**只有这一步通过后才进入第二段。** 保留未修改的 manifest 和 candidate；哈希来源本身也要可信，验证器不会认证被手工篡改的输入。

这次成功输入生成的第一段为 512,603 字节、6,271 行、3,055 次字面量写入，最长行 178 字符，低于本次分析的 256 字节行缓冲区。它没有逐字节读回或解释执行的哈希循环。

## 第二段：短脚本安装并验证显示

确认第一段读回通过，卡仍接在电脑时，仅用 `02-install-after-readback` 的脚本替换 `script/startup.ttl`，并复制空的 `URBLOG9.TXT` 到根目录。不要清空或复用旧日志掩盖失败；旧尝试应先完整归档。

第二段检查三份机内文件的长度和目标属性，先把新临时图、原图备份、安装前目标读回 SD 卡，再执行：

```text
filecopy 'B:\Resource\Jpeg\RB81NW.JPG' 'B:\Resource\Jpeg\GB_Urban.jpg'
filecopy 'B:\Resource\Jpeg\GB_Urban.jpg' 'C:\URBRD9.JPG'
```

这段脚本只有 3,004 字节、146 行。长度/属性检查失败时会尝试机内备份恢复，并写 `URBRS9.JPG` 读回。TTL 无法确认完整内容或硬件显示，因此不能把 `completed=1` 单独当成成功。

安全弹出，正常开机，等进入拍摄界面且活动灯停止，再关机检查画面。接回电脑，将日志和以下四份文件保存到新的 `step2-readback/`：

| 文件 | 必须匹配 |
|---|---|
| `URBNW9.JPG` | 新图 SHA-256 |
| `URBOR9.JPG` | 原图 SHA-256 |
| `URBPRE9.JPG` | 原图 SHA-256 |
| `URBRD9.JPG` | 新图 SHA-256（最终目标） |

```sh
python3 tools/gr3x_urban_shutdown.py verify \
  gr3x-urban-local/package/manifest.json gr3x-urban-local/step2-readback --step 2
```

日志还必须为 `error=0,attempted=1,restored=0,completed=1`。验证失败，或出现预览帧残留、空白画面时停止安装流程，保留所有证据，按下述原图恢复流程处理。相机处于黑屏、镜头未伸出且活动灯持续闪烁时，不要反复触发脚本或在活动过程中拔卡；本次旧脚本曾导致长时间忙碌，恢复后才继续操作。此处没有为异常情况建立安全的断电时限。

## 完成后清理，以及 macOS 文件注意事项

成功需同时满足最终目标完整 SHA-256 匹配、相机显示新图、正常开关机。之后按顺序：

1. 卡接电脑时移除 `script/startup.ttl`，保留入口文件，安全弹出。
2. MENU + 开机进入工厂菜单，把 `Script` 改回 `Disable`；正常开关机确认新图仍显示。
3. 关机取卡，接电脑；归档这次脚本、日志和读回后，再移除入口文件、空 `script` 目录及明确的任务临时文件。保留原图和个人新图的电脑备份。
4. 核对照片的相对路径、大小和修改时间没有变化，完成写入后同步并安全弹出卡。

Mac 上采用程序的二进制 `write_bytes` 写文件，或使用 `COPYFILE_DISABLE=1 cp` 复制任务文件，以减少额外元数据。TTL 必须是 ASCII、CRLF，不能是富文本、UTF-16 或带 BOM 的文本。随复制方式产生的 `._startup.ttl`、`._URBLOG8.TXT` 等 AppleDouble 文件不应作为相机输入；归档后只清理已确认属于本次任务的 `._*`、`.DS_Store` 和任务文件扩展属性。

不要对整卡运行递归删除或递归清扩展属性命令，也不要把 `.Spotlight-V100`、`.Trashes`、`.fseventsd` 当作本次脚本文件清除。上述复制设置不能保证全卡永远没有 macOS 元数据；每次准备后都要检查卡根目录及 `script` 目录的实际文件名和字节数。不要删除 `DCIM` 或照片。若安全弹出提示设备忙，先关闭占用程序后重试，避免强制弹出。

本次最后清理后，卡上没有启动脚本和工厂入口，Script 为 Disable。4,000 个照片目录文件的路径、大小和修改时间清单保持一致；这不是逐张照片内容哈希校验。卡已正常安全弹出。

## 原图恢复

恢复使用**此前已通过完整读回核验的机内** `B:\Resource\Jpeg\RB41OL.JPG`，不是从 SD 卡把 JPEG 复制回去。本次 B: → B: 恢复和随后完整读回已实测成功。

将 [恢复示例](../examples/gr3x-urban-restore.ttl.example) 写为 `script/startup.ttl`。该新保护模板仅有离线模型测试；其底层复制操作已实测。它要求备份、目标均为 107,902 字节，目标属性为 32，且卡上不存在旧 `URBREST.JPG`。保留旧读回后才可准备另一次运行。Script Enable、安全弹出、正常开机运行、关机后读回 `URBREST.JPG`。它必须精确等长，完整 SHA-256 匹配原图，并且相机再次显示原图。之后移除脚本、Script Disable、移除入口。

若机内备份未验证、目标长度已改变、恢复读回缺失或不匹配，模板不能保证恢复，应停止进一步写入并保留证据。不要给原图加尾部来掩盖长度或哈希差异。

## 实测证据与失败尝试的边界

| 内容 | SHA-256 / 结果 |
|---|---|
| 原 Urban 图，107,902 字节 | `7a2154a6d24ed5e460d2a918783d593171e399562923da582801186098ffc89f` |
| 成功新图，107,902 字节 | `098e95207b205237a855bc5e987e0052784be3c62298eb2c12191988a9933ace` |
| 成功第一段 TTL | `95470f5ffbb3b61ed6137620696c2a2f0fbaaaf37e8be9d563e4325781cbc277` |
| 成功第二段 TTL | `9af75290f8c44b1a95437901ddc93d3e90386a8d61a1e9a87920ed7c37f55c80` |
| 第一段 | 三份完整读回匹配；日志 error 0、attempted 0、restored 0、completed 1 |
| 第二段 | 四份完整读回匹配；日志 error 0、attempted 1、restored 0、completed 1 |
| 显示与收尾 | 使用者确认新图显示；正常开关机；Script Disable；启动文件清理 |

成功新图在编码前已由使用者确认。Pillow 与独立的 jpeg-js 严格模式均完整解码通过。这里只发布结构、哈希和过程，不发布图稿或读回。

此前尝试的限制：

- **SD 来源复制失败**：Mac 写入和相机生成的 C: 来源均出现过目标零字节；B: → B:、B: → C: 完整哈希匹配。精确原因未确定，不能归因于 macOS 垃圾文件本身。
- **读回正确但显示失败**：早期新图的完整写入已核验，关机却停留在预览最后一帧。该图与最终成功图在多处元数据和 JPEG 结构上不同，不能单独认定 COM、Exif 或某个标记就是原因。
- **解释执行校验过慢**：废弃的一版脚本拟对三份 107,902 字节文件逐字节读入，共 323,722 次读取，其循环体对应约 680 万次源行访问。实测出现黑屏、镜头不伸出、绿色灯持续闪烁约两分钟，后来恢复正常。没有证明无限循环，也没有定位确切卡住指令；该版不能作为推荐流程。最终方案改为电脑校验，机内不跑这些循环。
- **固定 JPEG 偏移不是已证实要求**：离线检查的 13 个资源 JPEG 都是 720×480 baseline，但有一个带 ICC，其 SOF 偏移不同。因此“SOF 必须位于固定偏移”不成立；成功图只是尽量沿用原图声明，未证明硬件所有接受规则。
- **离线测试不等于硬件测试**：成功脚本曾在原生 TTL 解释器的离线环境中运行，文件系统适配为内存模型，覆盖正常执行及重复日志/已有临时图/错误长度等拒绝分支。该模型不能证明相机存储行为、硬件 JPEG 驱动或真实运行时间。新增单元测试进一步核对生成字节和完整读回校验，不扩展实测机型范围。

代码审查与本地验证：

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

本报告提供的是单台 Urban 1.60 的实测记录与可审查工具。新输入仍需逐阶段验证，不能用文件存在、大小正确或日志结束代替完整哈希和相机显示。

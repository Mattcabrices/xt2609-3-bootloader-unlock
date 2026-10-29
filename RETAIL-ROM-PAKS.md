# Motorola retail Android and PAKS removal

## Ready-made Community build v2

[Community build v2 downloads](https://github.com/Mattcabrices/xt2609-3-bootloader-unlock/releases/tag/retail-cleanup-v2) include system_a.img, system_ext.cleaned.v2.img, product.cleaned.v2.img (split into five raw .part files) and vbmeta.retail.verification-disabled.img. Download the release's README-DOWNLOAD.md and manifest, then use reassemble_and_verify.py to assemble and validate the files before considering installation. Use the v2 filenames in place of the older cleaned filenames below; all device/slot/partition preflight checks and bootloader-preservation boundaries still apply.

The v2 images additionally exclude all five APK packages previously removed only for user 0, plus dedicated configuration files. Offline decompression, exact-removal, Android metadata and 400-APK identity audits passed. The earlier build was booted on one XT2609-3; **v2 itself has not had a separate boot or reset/setup test**. The historical preparation notes below describe the older images where they mention extra per-user removal.


## Scope

This records the successful **Android-only** conversion on one XT2609-3. It is not a universal flash recipe. The retail package targets **XT2609-1 RETUS/CID50**, while the tested phone is XT2609-3 Cricket/CID51. Both use masera, but that alone does not prove interchangeability.

**Retail firmware still contained PAKS, Cricket apps and carrier overlays.** Changing the channel label or simply flashing stock retail does not guarantee their removal. The software-channel property remained Cricket after our conversion.

## 1. Obtain and preserve the stock packages

Keep the phone's own Cricket stock package as a restoration source. Motorola Software Fix can look up the phone's matching firmware. Download only; do not run Rescue or its complete stock XML flashing script on the patched phone.

The retail package used was:

[XT2609-1 MASERA RETUS Android 16 W3WF36.52-40-3, CID50](https://mirrors.lolinet.com/firmware/lenomola/2026/masera/official/RETUS/XT2609-1_MASERA_RETUS_16_W3WF36.52-40-3_subsidy-DEFAULT_regulatory-DEFAULT_cid50_CFC.xml.zip)

This is an OEM firmware package hosted by the **third-party Lolinet mirror**, not a Motorola-hosted download. Download size was 9,556,568,842 bytes. Preserve the original ZIP, check extraction CRCs and each supplied manifest MD5. We additionally verified the original OEM AVB signatures. Do not assume a checksum from the same archive alone establishes authenticity.

Do not commit these large archives to this repository.

## 2. Unpack the Android logical images

Extract the ZIP into `retail-os/extracted`. The Android partitions are inside `super.img_sparsechunk.*`, not separate system/product files.

```text
python unpack_sparse_super.py retail-os/extracted retail-os/logical --partitions system_a system_ext_a product_a
```

The included read-only parser checks sparse structure and LP metadata checksums. It does not flash or modify the phone.

Use [EROFS tools](https://github.com/sekaiacg/erofs-tools/releases) for your host platform. The original run used the project's Cygwin x86-64 build, version 1.8.10-251217. Extract both app partitions while retaining the generated fs_config and file_contexts:

```text
extract.erofs.exe -i retail-os/logical/system_ext_a.img -x -s -o retail-os/modified-tree
extract.erofs.exe -i retail-os/logical/product_a.img -x -s -o retail-os/modified-tree
```

Work on extracted copies. Preserve the original images. These are EROFS filesystems; deleting a filename directly from the image with a ZIP utility is not a valid modification.

## 3. Remove PAKS and the identified carrier packages

PAKS was at:
- system_ext: /priv-app/PAKSFinance/PAKSFinance.apk
- system_ext: /priv-app/PaksFinanceNotification/PaksFinanceNotification.apk

Also remove their separate permission, nondisable, sysconfig and product feature/background-intent files. A product framework overlay lists PAKS as a protected provisioning package, so ordinary `pm uninstall --user 0 com.motorola.paks` and disable commands failed on stock. The working method omitted the APKs from rebuilt images. The general framework overlay itself was retained to preserve its unrelated device settings.

The helper first prints a plan. Add --execute only after reviewing it:

```text
python clean_retail_tree.py --tree retail-os/modified-tree --metadata-dir retail-os/modified-tree/config --out-config retail-os/build-config
python clean_retail_tree.py --tree retail-os/modified-tree --metadata-dir retail-os/modified-tree/config --out-config retail-os/build-config --execute
```

It targets PAKS/Cricket-named paths plus the additionally identified AttIqi, IqiMotMetrics, TheScoop and CKT-named overlays. **That expanded list has not yet been flashed as one complete rebuilt image.** In the successful run, the first image cleanup missed these five packages; they were subsequently removed for user 0:

```text
adb shell pm uninstall --user 0 com.att.iqi
adb shell pm uninstall --user 0 com.motorola.iqimotmetrics
adb shell pm uninstall --user 0 com.cricketwireless.thescoop
adb shell pm uninstall --user 0 com.motorola.android.overlay.cricket
adb shell pm uninstall --user 0 com.motorola.android.overlay.cricket.default
```

Per-user removal can be undone by a factory reset; physical image removal avoids that specific limitation. Identify packages by their manifest/package ID, not filenames alone. Do not remove similarly named core telephony components indiscriminately.

## 4. Rebuild and validate

Use each image's original filesystem UUID from the extractor's fs_options if preserving it. The helper maps metadata prefixes from system_ext_a/product_a to the real Android mount names.

```text
mkfs.erofs.exe -zlz4hc -T 0 --mount-point=/system_ext --fs-config-file=retail-os/build-config/system_ext_fs_config --file-contexts=retail-os/build-config/system_ext_file_contexts system_ext.cleaned.img retail-os/modified-tree/system_ext_a
mkfs.erofs.exe -zlz4hc -T 0 --mount-point=/product --fs-config-file=retail-os/build-config/product_fs_config --file-contexts=retail-os/build-config/product_file_contexts product.cleaned.img retail-os/modified-tree/product_a
fsck.erofs.exe --extract system_ext.cleaned.img
fsck.erofs.exe --extract product.cleaned.img
```

Here --extract without an output path validates decompression; it does not extract another tree. Compare source/rebuilt file lists, ownership, permissions, capabilities and SELinux labels. Confirm only planned files disappeared and every image fits the actual phone's logical partition capacity. Repacked image hashes will differ if build settings/tools or removal lists differ.

## 5. Installation boundaries and the successful approach

Prepare a restoration plan before writing. Check fastbootd, unlocked state, slot a and no active snapshots. Preserve LK/preloader/GPT, modem, kernel, vendor drivers and device calibration/security data. Never run the stock XML flashing script; it includes bootloader writes and nvdata erasure. Do not switch to slot B.

The successful installation wrote only:
1. Retail system_a.
2. Cleaned system_ext_a.
3. Cleaned product_a.
4. Retail vbmeta_a with AVB flags changed from 0 to 3 to disable verification/verity for rebuilt filesystems.

The Android-only installer used explicit partition names and 256 MB transfer chunks. system_a required a small logical resize inside super. **No physical GPT, bootloader, kernel or vendor partition was replaced.** Do not assume the same size/compatibility on another device.

For the exact reviewed source and slot-a configuration, these are the corresponding manual commands. First run the read-only getvar checks and confirm sizes, slot and snapshot state. Do not proceed on a different configuration without review:

```text
adb reboot fastboot
fastboot getvar is-userspace
fastboot getvar unlocked
fastboot getvar current-slot
fastboot getvar snapshot-update-status
fastboot getvar partition-size:system_a
fastboot getvar partition-size:system_ext_a
fastboot getvar partition-size:product_a
```

Required responses include is-userspace=yes, unlocked=yes, current-slot=a, snapshot-update-status=none. Check capacity/free space; host fastboot may resize logical partitions. Prepare matching verification metadata offline, then write ONLY these four named partitions:

```text
python disable_avb_flags.py retail-os/extracted/vbmeta.img vbmeta.retail.disabled.img
fastboot -S 256M flash system_a retail-os/logical/system_a.img
fastboot -S 256M flash system_ext_a system_ext.cleaned.img
fastboot -S 256M flash product_a product.cleaned.img
fastboot flash vbmeta_a vbmeta.retail.disabled.img
fastboot reboot bootloader
fastboot getvar securestate
fastboot getvar current-slot
fastboot oem partition md5 lk_a 0 4081712
```

Each command must succeed before sending the next. Stop on any failure; do not reboot an incomplete installation casually. Compare LK MD5 with the recorded unchanged value, confirm unlocked slot a, then `fastboot reboot`. This helper only accepts the exact documented stock VBMeta hash and does not edit the original file. It is not a general unlock or AVB tool.

AVB flag editing intentionally invalidates the original signature and requires the bootloader to stay unlocked. See Android's [AVB documentation](https://android.googlesource.com/platform/external/avb/+/master/README.md). The tested phone entered recovery and required a factory reset before Android setup appeared. The original installed LK was not dumped; the saved stock LK is the downloaded 7-1 source.

## 6. Verify the result and manage updates

```text
adb shell getprop ro.system.build.fingerprint
adb shell pm path com.motorola.paks
adb shell pm path com.motorola.paks.notification
adb shell pm list packages --user 0
```

Check actual package absence, normal boot and the hardware functions you use, especially calling/VoLTE, mobile data, Wi-Fi, camera and fingerprint. Only boot/setup, package checks and alternate-carrier eSIM internet were explicitly confirmed in this record; do not report untested functions as tested.

To turn off Android's automatic-update preference:

```text
adb shell settings put global ota_disable_automatic_update 1
adb shell settings get global ota_disable_automatic_update
```

Motorola's OTA updater refused both disabling and per-user uninstall. This preference is **not a demonstrated complete OTA block**. Do not accept OTA/Rescue updates blindly: they may refuse modified images, restore apps or replace the patched bootloader. Future updates need inspection and selective handling.

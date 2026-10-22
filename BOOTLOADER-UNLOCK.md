# Bootloader unlock — tested configuration only

## Evidence and prerequisites

Tested device: Motorola Edge (2026), XT2609-3, masera, Cricket, CID `0x0033`, active slot **a**. Source LK: W3WFS36.52-27-7-1. Original Android: W3WF36.52-27-7.

This modifies a critical boot component and can permanently brick an incompatible device. Successful recovery from a hard brick has not been demonstrated. The tested phone's `lk_b` was blank; **slot B was not a fallback**. Do not switch slots or write both bootloaders.

Use only on a device you own or are authorized to service. Unlocking factory-resets the phone. Keep backups and exact compatible stock firmware.

## 1. Verify files and phone

Install current Android platform-tools and the signed Motorola USB driver from the vendor. Enable USB debugging and authorize your computer. Reboot to bootloader, then inspect:

```text
adb reboot bootloader
fastboot devices
fastboot getvar product
fastboot getvar sku
fastboot getvar cid
fastboot getvar current-slot
fastboot getvar securestate
```

Check the exact model, source build, CID, slot and image SHA-256 against this README and VERIFIED-RESULT.md. These commands do not establish compatibility with a different build. Stop if the target differs or is not on slot a; do not “fix” that by switching slots.

Patched LK SHA-256:
`6a8ed0c93b8a5a791d015cb13004ffe84fdfe59d18f1b4350d653aaf707685e6`

## 2. Generate a key for the actual phone

The image uses **runtime serial-derived keys**. Each phone needs its own generated key. The original device serial and keys are excluded from this public project.

Use [Val Protocol](https://github.com/Maikyxd/val-protocol), matching the locally used commit `dc7f41f9b1a32da1a78ef327bb62d2bef17d7bd0`. Follow its requirements for Python/dependencies. The intentionally public seed in PUBLIC-PATCH-SEED.txt matches the included tested image. Use it with the target phone's own serial (available from the phone/fastboot; do not post it):

```text
python lk_keygen.py --secret YOUR_PATCH_SECRET --serialno YOUR_PHONE_SERIAL --count 1
```

Do not post serials or generated keys publicly. Using a different patch secret requires building a matching patched image; do not mix arbitrary keys and images.

## 3. Flash only the reviewed LK and verify it starts

For the tested slot-a configuration, the commands actually used were:

```text
fastboot flash lk_a lk.patched.img
fastboot oem partition md5 lk_a 0 4081712
fastboot reboot bootloader
fastboot getvar securestate
```

The exact written-range MD5 must be `49f44ac37828de168736f722f3cd0b94`. A successful flash does not itself mean unlocked; the tested phone still reported oem_locked at this point.

## 4. Perform the separate unlock

```text
fastboot oem unlock YOUR_GENERATED_KEY
fastboot getvar securestate
```

Confirm the destructive unlock on the phone if prompted. In the successful run the command reported “Bootloader is unlocked!” and a later query independently returned `flashing_unlocked`.

```text
fastboot reboot
```

Complete setup and reenable USB debugging after the reset. Do not relock, restore stock LK, overwrite lk_b or run a full stock flashing script as a cleanup step. Those transitions were not validated for this method.

## Reproducing the patch

The image was built from the verified stock LK with Val Protocol's `unlock-serial` preset and the seed shared in PUBLIC-PATCH-SEED.txt. Five embedded subimages passed the tool's integrity checks. Offline certificate/hash checks alone did not prove hardware acceptance; the observed flash/reboot/unlock supplied that additional evidence for this one phone. Credit the upstream authors rather than presenting this as a new universal exploit.

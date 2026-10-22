# Motorola Edge (2026) XT2609-3 bootloader unlock

Community unlock guide, tested image, and reproducibility notes for **Motorola Edge (2026), XT2609-3, codename masera**.

**Project maintained and documented by [Matt Cabrices](https://github.com/Mattcabrices).** This project records a tested repair and interoperability workflow using upstream Val Protocol research; upstream exploit and patcher credit belongs to its authors.

## Device identification

This project is for the **Motorola Edge (2026)**, also called **Moto Edge (2026)**. The tested carrier variant is **XT2609-3 (Cricket)**, codename **masera**. Match the model number and documented firmware before using any image. Other Edge generations and XT2609 variants have not been verified by this project.

## Compatibility — read this first

**Confirmed on one XT2609-3 Cricket/CID51 phone. Not verified on every unit, variant, or firmware version.** This is not a universal Motorola unlock. The method may apply to other compatible units, but a matching model name alone is insufficient.

The patched LK was made from Cricket **W3WFS36.52-27-7-1**, with the phone originally running **W3WF36.52-27-7**. It booted, accepted a generated unlock key, and independently reported `securestate: flashing_unlocked`. The image itself enables the separate unlock command; flashing it alone does not unlock a phone.

- [Bootloader instructions](BOOTLOADER-UNLOCK.md)
- [Download retail Android and remove PAKS](RETAIL-ROM-PAKS.md)
- [Verified results and limits](VERIFIED-RESULT.md)
- [Credits and firmware ownership](NOTICE.md)

## Download contents

| File | Purpose |
|---|---|
| lk.patched.img | Exact patched LK used successfully |
| lk.stock.img | Downloaded Cricket 7-1 source LK; **not a dump of the original installed bootloader** |
| PUBLIC-PATCH-SEED.txt | Intentionally shared patch seed: generate a different key for your own serial |
| SHA256SUMS.txt | File integrity checks |

This public edition excludes the original phone serial and device-specific unlock keys and starts with a clean commit history. The patch seed is intentionally public so compatible owners can generate their own keys. It is not a GitHub credential or a universal unlock key. Do not post your serial, IMEI, generated key, personal logs or private backup here.

## What happened to Android

Retail XT2609-1 RETUS Android was unpacked and cleaned. Only `system_a`, `system_ext_a`, `product_a` and verification-disabled `vbmeta_a` were flashed. Kernel, vendor drivers, modem, GPT, preloader and both LK partitions were preserved. A factory reset was required; Android then booted successfully. PAKS was absent. Five differently named carrier packages required additional per-user removal; the guide includes them.

An alternate-carrier eSIM successfully used mobile data. **No SIM/network-unlock procedure was performed, and bootloader unlock is separate from carrier unlock.**

Large stock ROM archives and rebuilt Android images are kept locally, not committed here. Firmware modifications can require manual updates; do not relock or run stock flashing/Rescue scripts blindly.

## Finding and downloading this project

Search terms: Moto Edge 2026 XT2609-3 bootloader unlock, masera, Cricket Motorola, com.motorola.paks removal, retail RETUS Android. Download with **Code > Download ZIP**, extract, then check SHA256SUMS.txt before using files. Public search indexing can take time and ranking is not guaranteed.

## Report compatibility

Use an issue to report model, firmware build, CID, slot, and result. Redact serial numbers, IMEI, generated keys, account data, and private file paths. A report of success on another configuration is useful evidence; it does not prove every model is supported.

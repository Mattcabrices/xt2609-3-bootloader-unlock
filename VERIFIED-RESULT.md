# Verified result and hashes

Tested on one Motorola Edge (2026) XT2609-3 / masera / Cricket CID51, slot a.

- Original Android: W3WF36.52-27-7.
- Patched LK source: Cricket W3WFS36.52-27-7-1.
- Bootloader version after successful reboot: MBM-3.1-masera-82d9b9-W3WFS36.52-27-7-1-c6948e.
- Separate generated-key unlock succeeded; independent fastboot query returned flashing_unlocked.
- Patched LK length: 4,081,712 bytes.
- Patched SHA-256: 6a8ed0c93b8a5a791d015cb13004ffe84fdfe59d18f1b4350d653aaf707685e6.
- Exact written-range MD5: 49f44ac37828de168736f722f3cd0b94.
- Stock LK SHA-256: c3ffa81b2dee3850fddc1eccc49dae811e526f5f2b7bff3b96781c4208c820fd.
- Stock LK source manifest MD5: 06557019e238c78f53fa82605cfa90af.
- Four non-LK embedded payloads/certificates were unchanged in the independent parsed-image audit; reviewed LK code changes were limited to the validator and three gate-call ranges.
- Hardware-root/efuse trust was not established by the offline checker. Actual flash, reboot and unlock succeeded on this unit.
- No original installed LK readback was obtained. lk.stock.img is not that backup.
- lk_b was zero-filled and remains unchanged; no slot switch occurred.

Later Android-only conversion used retail W3WF36.52-40-3. A factory reset was needed; Android setup then appeared. ADB confirmed:
motorola/masera_g_sys/masera:16/W3WF36M.52-40-3/0cd13:user/release-keys

PAKS was absent. Five remaining differently named carrier packages were removed for user 0. Existing prepared Android images still contain those five packages, so reset could restore them. Both LK checksums and unlocked state were reverified after the Android flash.

User confirmed alternate-carrier eSIM internet works and generally reported the phone working well. No SIM-lock bypass operation was performed. Root was not installed. No evidence supports a claim that this works on all Motorola phones or all XT2609 firmware versions.

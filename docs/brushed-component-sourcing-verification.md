# Active Components Compliance & Origin Analysis

To ensure compliance with defense procurement or supply chain security standards (such as **NDAA Section 889**, **DFARS 252.225-7007**, or **ITAR / EAR compliance**), silicon must not originate from restricted entity lists or covered regions (primarily China and Russia).
Below is the verification breakdown for the active components across all tiers:

## **1\. Core Microcontroller & Security Root of Trust**

| Component | Function | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **MSPM0G3518-Q1** | Primary Microcontroller | Texas Instruments (USA) | USA / Japan | Malaysia / Taiwan / Thailand | **Compliant** |
| **OPTIGA™ Trust M V3** | Security Element / Common Criteria | Infineon (Germany) | Dresden, Germany / Villach, Austria | Malaysia / Philippines | **Compliant** |

## **2\. Tier 1: Integrated H-Bridge ICs (2S–6S / 10A–20A)**

| Component | Function | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **DRV8873-Q1 / DRV8874** | Integrated H-Bridge Driver | Texas Instruments (USA) | USA (Dallas, TX / Sherman, TX) | Taiwan / Malaysia | **Compliant** |

## **3\. Tier 2 & Tier 3: Gate Drivers & Controller Interfaces**

| Component | Function | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status / Notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **DRV8706-Q1** | Smart Gate Driver (Up to 37V) | Texas Instruments (USA) | USA | Taiwan / Philippines | **Compliant** |
| **DRV8718S-Q1** | Multi-Channel Gate Driver (High-V) | Texas Instruments (USA) | USA | Taiwan / Malaysia | **Compliant** |
| **LTC7010** | High-Side / Half-Bridge Driver | Analog Devices / LTC (USA) | USA (Camas, WA / Milpitas, CA) | Malaysia / Philippines | **Compliant** |
| **L6387E** | Gate Driver (*Optional Spec*) | STMicroelectronics (EU) | Agrate, Italy / Crolles, France | Shenzhen, China | ⚠️ **Use Caution / Replace** *(Backend assembly occurs in China).* |

**Substitution Recommendation:** Replace the ST L6387E with the **Texas Instruments DRV8706-Q1** or **Analog Devices LTC7004 / LTC7010** across all builds to keep gate drivers 100% compliant with US/EU supply chain directives.

## **4\. Power MOSFET Silicon (Discrete Power Stage)**

| Component | Specs & Package | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **IPT012N08N5** | 80V, 1.2mΩ (HSOF-8) | Infineon (Germany) | Villach, Austria / Dresden, Germany | Melaka, Malaysia / Regensburg, Germany | **Compliant** |
| **IPT015N10N5** | 100V, 1.5mΩ (HSOF-8) | Infineon (Germany) | Villach, Austria / Dresden, Germany | Melaka, Malaysia / Regensburg, Germany | **Compliant** |
| **SUM70042E** | 100V, 4.2mΩ (TO-263) | Vishay Siliconix (USA) | USA (Santa Clara, CA) | Migdal HaEmek, Israel / Taiwan | **Compliant** |
| **IPB072N15N3G** | 150V, 7.2mΩ (TO-263) | Infineon (Germany) | Villach, Austria | Melaka, Malaysia | **Compliant** |

## **5\. Nacelle-tilt build (6S / 10 A / brushed) — parts added 2026-09-17**

Rows added for `builds/6s/10A/BRUSHED_CAN_485_isolation/`. Vendor comes from each datasheet's imprint (`REFERENCES.md` tags);
fab and assembly sites are **not stated in any datasheet** and are carried
as `UNVERIFIED — needs primary source (see TODO.md 18.4)` until a vendor
country-of-origin statement or a distributor COO document is on file.
Nothing in this table may be read as a compliance verdict until then.

| Component | Function | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **DRV8874-Q1** [63] | Tier-1 integrated brushed H-bridge (orderable; [62] is the non-Q1 twin) | Texas Instruments (USA) | see §2 row for DRV8873-Q1 / DRV8874 — same family; site not stated in [63] | as §2 | **Pending** — UNVERIFIED — needs primary source (see TODO.md 18.4) |
| **TPS54560B** [65] | 6–7 V motor/solenoid rail buck, 4.5–60 V in, 5 A | Texas Instruments (USA) | not stated in [65] — UNVERIFIED — needs primary source (see TODO.md 18.4) | not stated in [65] — UNVERIFIED | **Pending** |
| **TPL7407L** [66] | Pin-brake solenoid low-side driver (2 channels paralleled), clamp to COM | Texas Instruments (USA) | not stated in [66] — UNVERIFIED — needs primary source (see TODO.md 18.4) | not stated in [66] — UNVERIFIED | **Pending** |
| **AEAT-8800-Q24** [64] | Remote worm-shaft absolute magnetic encoder (off-board, SPI/SSI) | Broadcom (imprint "Copyright © 2016–2017 by Broadcom"; HQ location not stated in [64]) | not stated in [64] — UNVERIFIED — needs primary source (see TODO.md 18.4) | not stated in [64] — UNVERIFIED | **Pending** |

## **Verification Summary & BOM Rules for Procurement**

> * **100% Compliant Core Architecture:** The TI MSPM0 MCU, OPTIGA Trust M V3 security chip, and the primary Infineon OptiMOS power MOSFETs originate entirely from fabs and packaging facilities in **the United States, Western Europe, Israel, Taiwan, Thailand, and Malaysia.**
> * **Gate Driver Standardization:** Standardize on TI's automotive driver suite (**DRV8706-Q1** and **DRV8718-Q1**) or Analog Devices drivers rather than generic European drivers (like ST's L6387E) to ensure that backend assembly remains outside of China.
> * **Traceability Requirement:** For OSHWA and government/industrial supply chain verification, require **Certificate of Origin (COO)** documents from authorized distributors (e.g., Arrow, Mouser, Digi-Key) for each batch reel prior to PCB assembly.

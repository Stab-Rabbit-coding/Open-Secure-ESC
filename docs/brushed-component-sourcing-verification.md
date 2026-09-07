### **Active Components Compliance & Origin Analysis**

To ensure compliance with defense procurement or supply chain security standards (such as **NDAA Section 889**, **DFARS 252.225-7007**, or **ITAR / EAR compliance**), silicon must not originate from restricted entity lists or covered regions (primarily China and Russia).  
Below is the verification breakdown for the active components across all tiers:

### **1\. Core Microcontroller & Security Root of Trust**

| Component | Function | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **MSPM0G3518-Q1** | Primary Microcontroller | Texas Instruments (USA) | USA / Japan | Malaysia / Taiwan / Thailand | **Compliant** |
| **OPTIGA™ Trust M V3** | Security Element / Common Criteria | Infineon (Germany) | Dresden, Germany / Villach, Austria | Malaysia / Philippines | **Compliant** |

### **2\. Tier 1: Integrated H-Bridge ICs (2S–6S / 10A–20A)**

| Component | Function | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **DRV8873-Q1 / DRV8874** | Integrated H-Bridge Driver | Texas Instruments (USA) | USA (Dallas, TX / Sherman, TX) | Taiwan / Malaysia | **Compliant** |

### **3\. Tier 2 & Tier 3: Gate Drivers & Controller Interfaces**

| Component | Function | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status / Notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **DRV8706-Q1** | Smart Gate Driver (Up to 37V) | Texas Instruments (USA) | USA | Taiwan / Philippines | **Compliant** |
| **DRV8718S-Q1** | Multi-Channel Gate Driver (High-V) | Texas Instruments (USA) | USA | Taiwan / Malaysia | **Compliant** |
| **LTC7010** | High-Side / Half-Bridge Driver | Analog Devices / LTC (USA) | USA (Camas, WA / Milpitas, CA) | Malaysia / Philippines | **Compliant** |
| **L6387E** | Gate Driver (*Optional Spec*) | STMicroelectronics (EU) | Agrate, Italy / Crolles, France | Shenzhen, China | ⚠️ **Use Caution / Replace** *(Backend assembly occurs in China).* |

**Substitution Recommendation:** Replace the ST L6387E with the **Texas Instruments DRV8706-Q1** or **Analog Devices LTC7004 / LTC7010** across all builds to keep gate drivers 100% compliant with US/EU supply chain directives.

### **4\. Power MOSFET Silicon (Discrete Power Stage)**

| Component | Specs & Package | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test | Compliance Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **IPT012N08N5** | 80V, 1.2mΩ (HSOF-8) | Infineon (Germany) | Villach, Austria / Dresden, Germany | Melaka, Malaysia / Regensburg, Germany | **Compliant** |
| **IPT015N10N5** | 100V, 1.5mΩ (HSOF-8) | Infineon (Germany) | Villach, Austria / Dresden, Germany | Melaka, Malaysia / Regensburg, Germany | **Compliant** |
| **SUM70042E** | 100V, 4.2mΩ (TO-263) | Vishay Siliconix (USA) | USA (Santa Clara, CA) | Migdal HaEmek, Israel / Taiwan | **Compliant** |
| **IPB072N15N3G** | 150V, 7.2mΩ (TO-263) | Infineon (Germany) | Villach, Austria | Melaka, Malaysia | **Compliant** |

### **Verification Summary & BOM Rules for Procurement**

> * **100% Compliant Core Architecture:** The TI MSPM0 MCU, OPTIGA Trust M V3 security chip, and the primary Infineon OptiMOS power MOSFETs originate entirely from fabs and packaging facilities in **the United States, Western Europe, Israel, Taiwan, Thailand, and Malaysia.**  
> * **Gate Driver Standardization:** Standardize on TI's automotive driver suite (**DRV8706-Q1** and **DRV8718-Q1**) or Analog Devices drivers rather than generic European drivers (like ST's L6387E) to ensure that backend assembly remains outside of China.  
> * **Traceability Requirement:** For OSHWA and government/industrial supply chain verification, require **Certificate of Origin (COO)** documents from authorized distributors (e.g., Arrow, Mouser, Digi-Key) for each batch reel prior to PCB assembly.
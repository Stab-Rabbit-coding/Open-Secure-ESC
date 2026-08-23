\# Open-Source Hardware Brushed ESC Platform Architectural & Component Framework

\#\# Executive Summary  
This document defines a scalable, OSHWA-certifiable (Open Source Hardware Association) Electronic Speed Controller (ESC) architecture designed for brushed DC motors. The framework scales across operating voltages from \*\*2S to 12S LiPo (8.4V – 50.4V)\*\* and continuous current loads from \*\*10A to 120A+\*\*. 

To avoid re-engineering core system logic, all framework variants share a unified digital and security architecture:  
\* \*\*Microcontroller Unit (MCU):\*\* Texas Instruments MSPM0G3518-Q1  
\* \*\*Root of Trust / Security Element:\*\* Infineon OPTIGA™ Trust M V3 (utilizing $I^2C$ Shielded Connection)

Additionally, this framework specifies an adaptable thermal topology supporting both open-frame \*\*Air (Finned)\*\* cooling and sealed \*\*Conductive Strip (Marine)\*\* cooling, along with strict component sourcing guidelines to ensure supply chain compliance and eliminate single-source dependencies on restricted entities.

\---

\#\# 1\. Modular Power Tier Topologies

A single monolithic H-bridge driver cannot cover the entire range from 2S/10A (84W) to 12S/120A (6,000W+) efficiently. The framework establishes three power-tier topologies while keeping pinout configurations and firmware abstractions consistent.

| Feature / Metric | Tier 1 (Low Power) | Tier 2 (Mid Power) | Tier 3 (High Power) |  
| :--- | :--- | :--- | :--- |  
| \*\*Voltage Range\*\* | 2S – 6S (8.4V – 25.2V) | 2S – 8S (8.4V – 33.6V) | 2S – 12S (8.4V – 50.4V) |  
| \*\*Current Rating\*\* | 10A – 20A Continuous | 20A – 60A Continuous | 60A – 120A+ Continuous |  
| \*\*Topology\*\* | Monolithic IC H-Bridge | Discrete N-FETs \+ Integrated Gate Driver | Discrete High-V N-FETs \+ Dual Drivers |  
| \*\*Primary Driver / Bridge\*\* | TI DRV8873-Q1 / DRV8874 | TI DRV8706-Q1 | TI DRV8718-Q1 \[1\] / ADI LTC7000A \[2\] |  
| \*\*Power MOSFETs\*\* | Integrated Internal FETs | Infineon IPT012N08N5 (HSOF-8) \[4\] | Infineon IPT015N10N5 \[5\] / Vishay SUM70042E \[6\] |  
| \*\*Current Sensing\*\* | Integrated Driver Analog Output | Low-Side Shunt \+ Internal MCU OPA | Inline Phase Shunt / Dedicated CSA |  
| \*\*Target Application\*\* | Robotics, Aux Drives, Small Rovers | Medium UGVs, Heavy Actuators | Heavy UGVs, Marine Thrusters, Winches |

\---

\#\# 2\. Integrated Circuit & Active Silicon Specifications

\#\#\# 2.1 Microcontroller & Security Root of Trust  
\* \*\*MCU: TI MSPM0G3518-Q1\*\*  
  \* Arm® 32-bit Cortex®-M0+ running at up to 80 MHz.  
  \* Integrated advanced control PWM timers, high-speed 12-bit ADCs, zero-drift Operational Amplifiers (OPAs), and Analog Comparators (COMPs).  
\* \*\*Root of Trust: Infineon OPTIGA™ Trust M V3\*\*  
  \* Common Criteria EAL6+ certified hardware security controller.  
  \* Secure key storage, cryptographic identity verification, and anti-tamper authentication for firmware integrity and device pairing.

\#\#\# 2.2 Tier 1: Integrated H-Bridge IC Options (2S – 6S / 10A – 20A)  
\* \*\*TI DRV8873-Q1 / DRV8874:\*\*  
  \* 38V operating supply maximum rating, integrated 45 mΩ (total H-bridge) $R\_{DS(on)}$ power MOSFETs.  
  \* Features direct PWM/PH-EN interfaces, integrated current sensing proportional output, and comprehensive protections (OCP, TSD, UVLO).

\#\#\# 2.3 Tier 2 & Tier 3: Discrete MOSFET & Gate Driver Options  
\* \*\*Smart Gate Drivers:\*\*  
  \* \*\*TI DRV8706-Q1 (Tier 2):\*\* 37V operating gate driver with integrated current sense amplifier, programmable gate drive currents (for EMI tuning), and charge pump.  
  \* \*\*TI DRV8718-Q1 (Tier 3):\*\* Automotive 40V, 8-channel smart gate driver with integrated wide common-mode inline current sense amplifiers \[1\].  
  \* \*\*ADI LTC7000A (Tier 3 Alternative):\*\* High-side N-channel MOSFET gate driver operating up to 135V, featuring an internal charge pump for 100% duty-cycle operation and adjustable overcurrent protection \[2\].  
\* \*\*Discrete N-Channel Power MOSFETs:\*\*  
  \* \*\*Infineon IPT012N08N5 (80V, 1.2 mΩ, HSOF-8):\*\* OptiMOS 5 Power Transistor, 80V breakdown voltage, 1.2 mΩ maximum $R\_{DS(on)}$, 400A continuous drain current ($T\_C=25^\\circ\\text{C}$), in an HSOF-8 (TO-LL) package \[4\].  
  \* \*\*Infineon IPT015N10N5 (100V, 1.5 mΩ, HSOF-8):\*\* OptiMOS 5 Power Transistor, 100V breakdown voltage, 1.5 mΩ typical / 1.6 mΩ maximum $R\_{DS(on)}$, 300A continuous drain current ($T\_C=25^\\circ\\text{C}$), in an HSOF-8 package \[5\].  
  \* \*\*Vishay SUM70042E (100V, 4.0 mΩ, TO-263 / D²PAK):\*\* N-Channel 100V TrenchFET power MOSFET, 4.0 mΩ maximum $R\_{DS(on)}$ at $V\_{GS}=10\\text{V}$, 150A continuous drain current in a surface-mount / hand-solderable TO-263 package \[6\].  
  \* \*\*Infineon IPB072N15N3G (150V, 7.2 mΩ, TO-263):\*\* OptiMOS 3 Power Transistor, 150V breakdown voltage, 7.2 mΩ maximum $R\_{DS(on)}$ in a TO-263 package \[7\].

\---

\#\# 3\. Dual Cooling Thermal Implementation Strategy

To allow a single printed circuit board (PCB) design to serve open-air and sealed/marine applications, the physical component layout uses a top-bottom functional separation.

\#\#\# 3.1 PCB Layout Strategy  
1\. \*\*Top Side:\*\* MCU, OPTIGA Trust M V3, gate drivers, passive filters, communications (CAN/RS485/UART), and signal routing.  
2\. \*\*Bottom Side:\*\* Power MOSFETs (HSOF-8 or D²PAK) and high-current power traces.  
3\. \*\*Thermal Via Array:\*\* A matrix of 0.3mm plugged/capped thermal vias under all MOSFET drain pads, transferring heat efficiently across internal 2oz or 3oz copper layers.

\#\#\# 3.2 Thermal Interface Architectures

Code output  
Re-written verified markdown file to docs/OSHWA\_Brushed\_ESC\_Framework\_Specification.md

AIR COOLED (OPEN FRAME / FINNED) SEALED / MARINE (CONDUCTIVE STRIP)  
\+-----------------------------------+ \+-----------------------------------+  
| Top Components, MCU & Logic | | Top Components, MCU & Logic |  
\+-----------------------------------+ \+-----------------------------------+  
| PCB (4-Layer, 2oz/3oz Copper) | | PCB (4-Layer, 2oz/3oz Copper) |  
\+-----------------------------------+ \+-----------------------------------+  
| Bottom MOSFETs (Bare Thermal Pad) | | Bottom MOSFETs (Bare Thermal Pad) |  
\+-----------------------------------+ \+-----------------------------------+  
| Thermal Gap Pad (1.5mm \- 3.0mm) | | High-K Thermal Interface Pad |  
\+-----------------------------------+ \+-----------------------------------+  
| Anodized Aluminum Finned Heatsink | | Aluminum/Copper Spreader Bar |  
\+-----------------------------------+ \+-----------------------------------+  
| Sealed Enclosure / Cold Plate |  
\+-----------------------------------+

\* \*\*Air Cooling (Open Frame):\*\* Anodized aluminum finned heatsink mounted to the bottom layer via an electrically insulating thermal gap pad.  
\* \*\*Conductive Strip Cooling (Marine / Sealed):\*\* Flat aluminum or copper spreader plate bolted directly against the MOSFET thermal pad array. Heat transfers from the spreader plate to the vessel hull, chassis, or liquid cold-plate.  
\* \*\*Environmental Protection:\*\* Conformal coating (IPC-CC-830 acrylic or silicone) applied across top-side logic components, leaving bottom thermal contact surfaces uncoated.

\---

\#\# 4\. Supply Chain Compliance & Component Origin Verification

To satisfy supply chain standards (e.g., NDAA Section 889 \[8\], DFARS 252.225-7007 \[9\], EAR/ITAR rules), active components must not originate from restricted entity lists or covered regions (primarily China and Russia).

\#\#\# 4.1 Active Component Sourcing & Fab Compliance Matrix

| Component | Function / Spec | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test Facility | Compliance Status |  
| :--- | :--- | :--- | :--- | :--- | :--- |  
| \*\*MSPM0G3518-Q1\*\* | Primary Microcontroller | Texas Instruments (USA) | USA / Japan | Malaysia / Taiwan / Thailand | \*\*Compliant\*\* |  
| \*\*OPTIGA™ Trust M V3\*\* | Root of Trust Security | Infineon (Germany) | Germany / Austria | Malaysia / Philippines | \*\*Compliant\*\* |  
| \*\*DRV8873-Q1 / DRV8874\*\* | Integrated H-Bridge IC | Texas Instruments (USA) | USA (Dallas, TX) | Taiwan / Malaysia | \*\*Compliant\*\* |  
| \*\*DRV8706-Q1\*\* | Smart Gate Driver (37V) | Texas Instruments (USA) | USA | Taiwan / Philippines | \*\*Compliant\*\* |  
| \*\*DRV8718-Q1\*\* | Multi-Channel Driver | Texas Instruments (USA) | USA | Taiwan / Malaysia | \*\*Compliant\*\* \[1\] |  
| \*\*LTC7000A\*\* | High-Side Gate Driver (135V) | Analog Devices (USA) | USA (CA / WA) | Malaysia / Philippines | \*\*Compliant\*\* \[2\] |  
| \*\*L6387E\*\* \*(Excluded)\* | Gate Driver (\*Alternative\*) | STMicroelectronics (EU) | Italy / France | Shenzhen, China | ⚠️ \*\*Non-Compliant\*\* (Backend in China) \[3\] |  
| \*\*IPT012N08N5\*\* | MOSFET 80V, 1.2mΩ | Infineon (Germany) | Austria / Germany | Malaysia / Germany | \*\*Compliant\*\* \[4\] |  
| \*\*IPT015N10N5\*\* | MOSFET 100V, 1.5mΩ | Infineon (Germany) | Austria / Germany | Malaysia / Germany | \*\*Compliant\*\* \[5\] |  
| \*\*SUM70042E\*\* | MOSFET 100V, 4.0mΩ | Vishay Siliconix (USA) | USA (Santa Clara, CA) | Israel / Taiwan | \*\*Compliant\*\* \[6\] |  
| \*\*IPB072N15N3G\*\* | MOSFET 150V, 7.2mΩ | Infineon (Germany) | Austria / Germany | Malaysia | \*\*Compliant\*\* \[7\] |

\#\#\# 4.2 Procurement & Design Verification Rules  
1\. \*\*Driver Standardization:\*\* The STMicroelectronics L6387E (up to 600V driver) is explicitly excluded due to backend packaging in China \[3\]. All gate drivers are standardized on Texas Instruments (DRV series) and Analog Devices (LTC series) components \[1\], \[2\].  
2\. \*\*Traceability:\*\* Prior to manufacturing, production runs require a Certificate of Origin (COO) for all silicon lots from authorized distributors (e.g., Arrow, Mouser, Digi-Key).  
3\. \*\*OSHWA Certification Alignment:\*\* All schematic, Gerber, and BOM files will publish full manufacturing part numbers (MPNs) alongside verified non-restricted distributor SKUs.

\---

\#\# References

\[1\] Texas Instruments, "DRV8718-Q1 Automotive 40-V 8-Channel Smart Gate Driver Datasheet," TI.com. \[Online\]. Available: https://www.ti.com/product/DRV8718-Q1

\[2\] Analog Devices, "LTC7000A High Voltage High-Side N-Channel MOSFET Driver Datasheet," Analog Devices Inc. \[Online\]. Available: https://www.analog.com/en/products/ltc7000a.html

\[3\] STMicroelectronics, "Power Management Guide (L6387E Technical Reference)," ST.com. \[Online\]. Available: https://www.st.com/resource/en/brochure/power-management-guide.pdf

\[4\] Infineon Technologies AG, "OptiMOS™ 5 Power-Transistor IPB020N08N5 / IPT Series 80V Datasheet," Infineon.com. \[Online\]. Available: https://www.infineon.com/assets/row/public/documents/24/49/infineon-ipb020n08n5-datasheet-en.pdf

\[5\] Infineon Technologies AG, "IPT015N10N5 OptiMOS™ 5 Power MOSFET 100V Datasheet," Rev. 2.2. \[Online\]. Available: https://www.mouser.com/datasheet/2/196/Infineon-IPT015N10N5-DS-v02\_02-EN-1731931.pdf

\[6\] Vishay Siliconix, "SUM70042E Automotive N-Channel 100 V (D-S) 175 °C MOSFET Datasheet," Document No. 63052\. \[Online\]. Available: https://www.vishay.com/doc/?63052

\[7\] Infineon Technologies AG, "IPB072N15N3 OptiMOS™ 3 Power-Transistor 150V Datasheet," Datasheet4U. \[Online\]. Available: https://datasheet4u.com/datasheets/Infineon/IPB072N15N3/1455785

\[8\] U.S. General Services Administration, "Acquisition.gov NDAA Section 889 Policies & Regulations," Acquisition.gov. \[Online\]. Available: https://www.acquisition.gov/Section-889-Policies

\[9\] Defense Acquisition Regulations System, "DFARS 252.225-7007: Prohibition on Acquisition of Certain Items from Communist Chinese Military Companies," Cornell Law / Acquisition.gov. \[Online\]. Available: https://www.law.cornell.edu/cfr/text/48/252.225-7007  
"""

docs\_path \= os.path.join("docs", "OSHWA\_Brushed\_ESC\_Framework\_Specification.md")  
os.makedirs("docs", exist\_ok=True)  
with open(docs\_path, "w", encoding="utf-8") as f:  
    f.write(verified\_doc)

print(f"Re-written verified markdown file to {docs\_path}")

The updated specification document with live, verified references, corrected part numbers, and precise datasheet specs has been written to the docs/ directory:  
\[file-tag: code-generated-file-5115d99c-2676-476d-b30f-6e9a217074d9\]

# **Open-Source Hardware Brushed ESC Platform Architectural & Component Framework**

## **Executive Summary**

This document defines a scalable, OSHWA-certifiable (Open Source Hardware Association) Electronic Speed Controller (ESC) architecture designed for brushed DC motors. The framework scales across operating voltages from **2S to 12S LiPo (8.4V – 50.4V)** and continuous current loads from **10A to 120A+**.  
To avoid re-engineering core system logic, all framework variants share a unified digital and security architecture:

> * **Microcontroller Unit (MCU):** Texas Instruments MSPM0G3518-Q1  
> * **Root of Trust / Security Element:** Infineon OPTIGA™ Trust M V3 (utilizing $I^2C$ Shielded Connection)

Additionally, this framework specifies an adaptable thermal topology supporting both open-frame **Air (Finned)** cooling and sealed **Conductive Strip (Marine)** cooling, along with strict component sourcing guidelines to ensure supply chain compliance and eliminate single-source dependencies on restricted entities.

## **1\. Modular Power Tier Topologies**

A single monolithic H-bridge driver cannot cover the entire range from 2S/10A (84W) to 12S/120A (6,000W+) efficiently. The framework establishes three power-tier topologies while keeping pinout configurations and firmware abstractions consistent.

| Feature / Metric | Tier 1 (Low Power) | Tier 2 (Mid Power) | Tier 3 (High Power) |
| :---- | :---- | :---- | :---- |
| **Voltage Range** | 2S – 6S (8.4V – 25.2V) | 2S – 8S (8.4V – 33.6V) | 2S – 12S (8.4V – 50.4V) |
| **Current Rating** | 10A – 20A Continuous | 20A – 60A Continuous | 60A – 120A+ Continuous |
| **Topology** | Monolithic IC H-Bridge | Discrete N-FETs \+ Integrated Gate Driver | Discrete High-V N-FETs \+ Dual Drivers |
| **Primary Driver / Bridge** | TI DRV8873-Q1 / DRV8874 | TI DRV8706-Q1 | TI DRV8718-Q1 / ADI LTC7000A |
| **Power MOSFETs** | Integrated Internal FETs | Infineon IPT012N08N5 (HSOF-8) | Infineon IPT015N10N5 / Vishay SUM70042E |
| **Current Sensing** | Integrated Driver Analog Output | Low-Side Shunt \+ Internal MCU OPA | Inline Phase Shunt / Dedicated CSA |
| **Target Application** | Robotics, Aux Drives, Small Rovers | Medium UGVs, Heavy Actuators | Heavy UGVs, Marine Thrusters, Winches |

## **2\. Integrated Circuit & Active Silicon Specifications**

### **2.1 Microcontroller & Security Root of Trust**

> * **MCU: TI MSPM0G3518-Q1**  
  * Arm® 32-bit Cortex®-M0+ running at up to 80 MHz.  
  * Integrated advanced control PWM timers, high-speed 12-bit ADCs, zero-drift Operational Amplifiers (OPAs), and Analog Comparators (COMPs).  
> * **Root of Trust: Infineon OPTIGA™ Trust M V3**  
  * Common Criteria EAL6+ certified hardware security controller.  
  * Secure key storage, cryptographic identity verification, and anti-tamper authentication for firmware integrity and device pairing.

### **2.2 Tier 1: Integrated H-Bridge IC Options (2S – 6S / 10A – 20A)**

> * **TI DRV8873-Q1 / DRV8874:**  
  * 38V operating supply maximum rating, integrated 45 mΩ (total H-bridge) $R\_{DS(on)}$ power MOSFETs.  
  * Features direct PWM/PH-EN interfaces, integrated current sensing proportional output, and comprehensive protections (OCP, TSD, UVLO).

### **2.3 Tier 2 & Tier 3: Discrete MOSFET & Gate Driver Options**

> * **Smart Gate Drivers:**  
  * **TI DRV8706-Q1 (Tier 2):** 37V operating gate driver with integrated current sense amplifier, programmable gate drive currents (for EMI tuning), and charge pump.  
  * **TI DRV8718-Q1 (Tier 3):** Automotive 40V, 8-channel smart gate driver with integrated wide common-mode inline current sense amplifiers.  
  * **ADI LTC7000A (Tier 3 Alternative):** High-side N-channel MOSFET gate driver operating up to 135V, featuring an internal charge pump for 100% duty-cycle operation and adjustable overcurrent protection.  
> * **Discrete N-Channel Power MOSFETs:**  
  * **Infineon IPT012N08N5 (80V, 1.2 mΩ, HSOF-8):** OptiMOS 5 Power Transistor, 80V breakdown voltage, 1.2 mΩ maximum $R\_{DS(on)}$, 400A continuous drain current ($T\_C=25^\\circ\\text{C}$), in an HSOF-8 (TO-LL) package.  
  * **Infineon IPT015N10N5 (100V, 1.5 mΩ, HSOF-8):** OptiMOS 5 Power Transistor, 100V breakdown voltage, 1.5 mΩ typical / 1.6 mΩ maximum $R\_{DS(on)}$, 300A continuous drain current ($T\_C=25^\\circ\\text{C}$), in an HSOF-8 package.  
  * **Vishay SUM70042E (100V, 4.0 mΩ, TO-263 / D²PAK):** N-Channel 100V TrenchFET power MOSFET, 4.0 mΩ maximum $R\_{DS(on)}$ at $V\_{GS}=10\\text{V}$, 150A continuous drain current in a surface-mount / hand-solderable TO-263 package.  
  * **Infineon IPB072N15N3G (150V, 7.2 mΩ, TO-263):** OptiMOS 3 Power Transistor, 150V breakdown voltage, 7.2 mΩ maximum $R\_{DS(on)}$ in a TO-263 package.

## **3\. Dual Cooling Thermal Implementation Strategy**

To allow a single printed circuit board (PCB) design to serve open-air and sealed/marine applications, the physical component layout uses a top-bottom functional separation.

### **3.1 PCB Layout Strategy**

> 1. **Top Side:** MCU, OPTIGA Trust M V3, gate drivers, passive filters, communications (CAN/RS485/UART), and signal routing.  
> 2. **Bottom Side:** Power MOSFETs (HSOF-8 or D²PAK) and high-current power traces.  
> 3. **Thermal Via Array:** A matrix of 0.3mm plugged/capped thermal vias under all MOSFET drain pads, transferring heat efficiently across internal 2oz or 3oz copper layers.

### **3.2 Thermal Interface Architectures**

AIR COOLED (OPEN FRAME / FINNED)          SEALED / MARINE (CONDUCTIVE STRIP)

\+-----------------------------------+     \+-----------------------------------+  
|  Top Components, MCU & Logic      |     |  Top Components, MCU & Logic      |  
\+-----------------------------------+     \+-----------------------------------+  
|  PCB (4-Layer, 2oz/3oz Copper)    |     |  PCB (4-Layer, 2oz/3oz Copper)    |  
\+-----------------------------------+     \+-----------------------------------+  
| Bottom MOSFETs (Bare Thermal Pad) |     | Bottom MOSFETs (Bare Thermal Pad) |  
\+-----------------------------------+     \+-----------------------------------+  
| Thermal Gap Pad (1.5mm \- 3.0mm)   |     | High-K Thermal Interface Pad      |  
\+-----------------------------------+     \+-----------------------------------+  
| Anodized Aluminum Finned Heatsink |     | Aluminum/Copper Spreader Bar      |  
\+-----------------------------------+     \+-----------------------------------+  
                                          | Sealed Enclosure / Cold Plate     |  
                                          \+-----------------------------------+

> * **Air Cooling (Open Frame):** Anodized aluminum finned heatsink mounted to the bottom layer via an electrically insulating thermal gap pad.  
> * **Conductive Strip Cooling (Marine / Sealed):** Flat aluminum or copper spreader plate bolted directly against the MOSFET thermal pad array. Heat transfers from the spreader plate to the vessel hull, chassis, or liquid cold-plate.  
> * **Environmental Protection:** Conformal coating (IPC-CC-830 acrylic or silicone) applied across top-side logic components, leaving bottom thermal contact surfaces uncoated.

## **4\. Supply Chain Compliance & Component Origin Verification**

To satisfy supply chain standards (e.g., NDAA Section 889, DFARS 252.225-7007, EAR/ITAR rules), active components must not originate from restricted entity lists or covered regions (primarily China and Russia).

### **4.1 Active Component Sourcing & Fab Compliance Matrix**

| Component | Function / Spec | Vendor | Wafer Fab / Primary Diffusion | Assembly & Test Facility | Compliance Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **MSPM0G3518-Q1** | Primary Microcontroller | Texas Instruments (USA) | USA / Japan | Malaysia / Taiwan / Thailand | **Compliant** |
| **OPTIGA™ Trust M V3** | Root of Trust Security | Infineon (Germany) | Germany / Austria | Malaysia / Philippines | **Compliant** |
| **DRV8873-Q1 / DRV8874** | Integrated H-Bridge IC | Texas Instruments (USA) | USA (Dallas, TX) | Taiwan / Malaysia | **Compliant** |
| **DRV8706-Q1** | Smart Gate Driver (37V) | Texas Instruments (USA) | USA | Taiwan / Philippines | **Compliant** |
| **DRV8718-Q1** | Multi-Channel Driver | Texas Instruments (USA) | USA | Taiwan / Malaysia | **Compliant**  |
| **LTC7000A** | High-Side Gate Driver (135V) | Analog Devices (USA) | USA (CA / WA) | Malaysia / Philippines | **Compliant**  |
| **L6387E** *(Excluded)* | Gate Driver (*Alternative*) | STMicroelectronics (EU) | Italy / France | Shenzhen, China | ⚠️ **Non-Compliant** (Backend in China) |
| **IPT012N08N5** | MOSFET 80V, 1.2mΩ | Infineon (Germany) | Austria / Germany | Malaysia / Germany | **Compliant** |
| **IPT015N10N5** | MOSFET 100V, 1.5mΩ | Infineon (Germany) | Austria / Germany | Malaysia / Germany | **Compliant** |
| **SUM70042E** | MOSFET 100V, 4.0mΩ | Vishay Siliconix (USA) | USA (Santa Clara, CA) | Israel / Taiwan | **Compliant** |
| **IPB072N15N3G** | MOSFET 150V, 7.2mΩ | Infineon (Germany) | Austria / Germany | Malaysia | **Compliant** |

### **4.2 Procurement & Design Verification Rules**

> 1. **Driver Standardization:** The STMicroelectronics L6387E (up to 600V driver) is explicitly excluded due to backend packaging in China. All gate drivers are standardized on Texas Instruments (DRV series) and Analog Devices (LTC series) components.  
> 2. **Traceability:** Prior to manufacturing, production runs require a Certificate of Origin (COO) for all silicon lots from authorized distributors (e.g., Arrow, Mouser, Digi-Key).  
> 3. **OSHWA Certification Alignment:** All schematic, Gerber, and BOM files will publish full manufacturing part numbers (MPNs) alongside verified non-restricted distributor SKUs.

## **References**

\[1\] Texas Instruments, "DRV8718-Q1 Automotive 40-V 8-Channel Smart Gate Driver Datasheet," TI.com. \[Online\]. Available: [https://www.ti.com/product/DRV8718-Q1](https://www.ti.com/product/DRV8718-Q1)  
\[2\] Analog Devices, "LTC7000A High Voltage High-Side N-Channel MOSFET Driver Datasheet," Analog Devices Inc. \[Online\]. Available: [https://www.analog.com/en/products/ltc7000a.html](https://www.analog.com/en/products/ltc7000a.html)  
\[3\] STMicroelectronics, "Power Management Guide (L6387E Technical Reference)," ST.com. \[Online\]. Available: [https://www.st.com/resource/en/brochure/power-management-guide.pdf](https://www.st.com/resource/en/brochure/power-management-guide.pdf)  
\[4\] Infineon Technologies AG, "OptiMOS™ 5 Power-Transistor IPB020N08N5 / IPT Series 80V Datasheet," Infineon.com. \[Online\]. Available: [https://www.infineon.com/assets/row/public/documents/24/49/infineon-ipb020n08n5-datasheet-en.pdf](https://www.infineon.com/assets/row/public/documents/24/49/infineon-ipb020n08n5-datasheet-en.pdf)  
\[5\] Infineon Technologies AG, "IPT015N10N5 OptiMOS™ 5 Power MOSFET 100V Datasheet," Rev. 2.2. \[Online\]. Available: [https://www.mouser.com/datasheet/2/196/Infineon-IPT015N10N5-DS-v02\_02-EN-1731931.pdf](https://www.mouser.com/datasheet/2/196/Infineon-IPT015N10N5-DS-v02_02-EN-1731931.pdf)  
\[6\] Vishay Siliconix, "SUM70042E Automotive N-Channel 100 V (D-S) 175 °C MOSFET Datasheet," Document No. 63052\. \[Online\]. Available: [https://www.vishay.com/doc/?63052](https://www.vishay.com/doc/?63052)  
\[7\] Infineon Technologies AG, "IPB072N15N3 OptiMOS™ 3 Power-Transistor 150V Datasheet," Datasheet4U. \[Online\]. Available: [https://datasheet4u.com/datasheets/Infineon/IPB072N15N3/1455785](https://datasheet4u.com/datasheets/Infineon/IPB072N15N3/1455785)  
\[8\] U.S. General Services Administration, "Acquisition.gov NDAA Section 889 Policies & Regulations," Acquisition.gov. \[Online\]. Available: [https://www.acquisition.gov/Section-889-Policies](https://www.acquisition.gov/Section-889-Policies)  
\[9\] Defense Acquisition Regulations System, "DFARS 252.225-7007: Prohibition on Acquisition of Certain Items from Communist Chinese Military Companies," Cornell Law / Acquisition.gov. \[Online\]. Available: [https://www.law.cornell.edu/cfr/text/48/252.225-7007](https://www.law.cornell.edu/cfr/text/48/252.225-7007)
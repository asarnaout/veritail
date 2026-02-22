### Motors and Drives — Scoring Guidance

This query involves electric motors, VFDs, motor starters, or servo systems.

**Critical distinctions to enforce:**

- **NEMA frame size encodes shaft height**: The first two digits ÷ 4 = shaft centerline height in inches. Frame 143T = 3.50" height. Frame 256T = 6.25". The "T" suffix indicates current NEMA standardized dimensions — pre-1964 "U" frame motors have DIFFERENT dimensions for the same HP. A replacement motor must match the frame designation, not just horsepower. Frame size is a hard constraint.
- **Five hard constraints for motor replacement**: voltage (115/208/230/460V), phase (single/three), frame size, speed (RPM = synchronous speed × (1 - slip)), and enclosure type (ODP, TEFC, XPRF). All five must match or the motor is not a valid replacement. A 3-phase motor will NOT run on single-phase power. A 230V motor on 208V service will run but underperforms (~15% torque reduction) and may overheat.
- **NEMA Design type determines torque characteristics**: Design B is the industry default (general purpose — fans, pumps, blowers). Design C provides high starting torque (loaded conveyors, compressors). Design D provides very high starting torque with 5-13% slip (punch presses, hoists). These are NOT interchangeable for the same application. If the query specifies a NEMA Design letter, treat as hard.
- **NEMA vs IEC motors**: IEC frame sizes (e.g., 90, 100, 112) use mm shaft height. IEC 90 (90mm) is close to NEMA 143T (88.9mm) but mounting dimensions differ. IEC motors carry no service factor (rated continuous S1 duty); NEMA motors typically carry 1.15 SF. IEC efficiency classes (IE1/IE2/IE3/IE4) roughly map to NEMA standard/energy efficient/premium but test methods differ. NEMA and IEC frames are NOT directly interchangeable on the same base plate without modification.
- **VFD-rated (inverter duty) vs standard motors**: VFD-rated motors have reinforced insulation (withstands PWM voltage spikes), may include insulated bearings and shaft grounding rings, and often have independent cooling fans for low-speed constant-torque operation. Running a standard motor on a VFD for constant-torque loads risks overheating and insulation failure. If the query specifies "inverter duty" or "VFD rated," standard motors are a poor match.
- **VFD sizing**: VFDs are sized by HP and voltage class. Input vs output voltage ratings differ — a "480V drive" expects 480V input 3-phase and outputs 480V 3-phase to the motor. Single-phase input VFDs driving 3-phase motors must be derated, typically by 50%. Communication protocol (Modbus, EtherNet/IP, PROFINET) and enclosure rating matter when specified.

**Terminology**:
- ODP = Open Drip Proof (indoor, clean environment)
- TEFC = Totally Enclosed Fan Cooled (dusty/wet environments)
- XPRF = Explosion Proof (hazardous locations)
- SF = Service Factor (1.15 means motor can sustain 115% of rated load)
- VFD = Variable Frequency Drive = inverter = AC drive

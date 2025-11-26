  # ESP32 UWB DW3000

  The DW3000 library in this repository was developed by NConcepts.

  This project uses MakerFabs DW3000 UWB ESP32 modules.

  This code is written for our [work](https://www.arxiv.org/abs/2505.09393) "UMotion: Uncertainty-driven Human Motion Estimation from Inertial and Ultra-wideband Units".

  ## Description

  Anchor-tag (AT): measuring the distance from one tag to multiple anchors
  ![Anchor tag](fig/AT.png)

  Distance-matrix (DM): measuring the distance matrix among all nodes
  ![Distance matrix](fig/DM.png)

  ```bash
  src
  ├── at_dstwr  # Anchor tag: double-sided two way ranging
  │   ├── main.cpp  # setup() and loop()
  │   ├── uwb.cpp  # ranging protocal
  │   └── uwb.h  # constants, declaration
  ├── at_sstwr # Anchor tag: single-sided two way ranging
  │   ├── main.cpp
  │   ├── uwb.cpp
  │   └── uwb.h
  ├── dm_dstwr  # Distance matrix: double-sided two way ranging
  │   ├── main.cpp
  │   ├── uwb.cpp
  │   └── uwb.h
  ├── dm_sstwr  # Distance matrix: single-sided two way ranging
  │   ├── main.cpp
  │   ├── uwb.cpp
  │   └── uwb.h
  ├── ui/         # ESP32 UI (IMU + UWB) for ESP32 with display support
  │   ├── main.cpp  # ESP32 setup and main loop for combined IMU + UWB
  │   ├── uwb.cpp    # UWB protocol implementation for initiator/responder
  │   ├── uwb.h      # UWB settings, message layout and prototypes
  │   ├── imu.cpp    # IMU (BNO086) setup and data handling
  │   └── imu.h      # IMU pin/config and declarations
  └── platformio.ini

  ## Visualizer (Python)

  This repository now includes a simple Python-based real-time visualizer to plot tag positions computed from UWB distances. The script lives in `visualizer/visualizer.py` and listens for serial distance outputs coming from the ESP32 UWB firmware.

  Quick overview:
  - The visualizer reads lines like `"18 1.032 m 22 3.630 m ..."` from a serial port and expects at least three anchor distances to estimate position using a least-squares multilateration method.
  - It supports exponential smoothing, outlier rejection, and shows a short trail of recent positions.

  Key settings (edit inside `visualizer/visualizer.py`):
  - `SERIAL_PORT` – e.g. `COM3` on Windows, `/dev/ttyUSB0` on Linux
  - `BAUD_RATE` – default 115200
  - `anchors` – a Python dictionary mapping anchor IDs to their (x, y) positions in meters
  - `SMOOTHING`, `OUTLIER_THRESHOLD`, `TRAIL_LENGTH` – visualization tuning parameters

  Dependencies (Python 3.x):

  Use pip to install manually:

  ```bash
  python -m pip install pyserial numpy matplotlib
  ```

  Or use the provided `visualizer/requirements.txt`:

  ```bash
  python -m pip install -r visualizer/requirements.txt
  ```

  Run the visualizer (on Windows, macOS or Linux):

  ```bash
  python visualizer/visualizer.py
  ```

  Notes & tips:
  - Make sure the ESP32 serial output prints distances in the format `ID value m` and at least three anchors are visible to the visualizer.
  - Example serial output from the UWB firmware is printed as: `<ID>\t<value> m\t` (e.g `18\t1.032 m\t`). The Visualizer expects `ID value m` per anchor on the same line.
  - Update the anchor coordinates inside `visualizer.py` to match your deployment.
  - The visualizer is intended for quick debugging and demonstrations. It is not a full-featured tracking UI but should help validate ranges and positioning visually.

  ## UI folder (ESP32 display/IMU controllers)

  The `src/ui` folder contains code which integrates the Sparkfun BNO08x IMU and the DW3000 UWB firmware to provide a UI-capable application for ESP32 devices (for example, ESP32 boards with small displays).

  Files and short descriptions:

  - `main.cpp`
    - Sets up UART, SPI and the UWB/IMU subsystems. Creates an IMU handler FreeRTOS task and enters the UWB initiator/responder loop. Prints the ESP MAC address and uses macros to pick the role (initiator vs responder).
  - `uwb.h`
    - Contains UWB-specific macros, message layout (indices), node and UID definitions, constants for antenna delay/intervals, and prototype declarations for `start_uwb()`, `initiator()` and `responder()`.
  - `uwb.cpp`
    - Implements the UWB configuration, initialization (`start_uwb()`), and the core initiator/responder ranging state machines.
    - Serial output is used to emit measured ranges in a format consumed by `visualizer/visualizer.py`.
  - `imu.h`
    - Declares pins, configuration macros and exported variables used by the IMU integration, and functions like `start_imu()` and `imu_handler()`.
  - `imu.cpp`
    - Implements the IMU initialization and reading using the SparkFun BNO08x library. The IMU handler records linear acceleration and rotation (quaternion) and prints timestamps and sensor data to Serial.

  If you are using the `src/ui` code, make sure to configure `USE_VSPI`, `USE_HSPI`, or `USE_I2C` to match your board wiring for the IMU (see `src/ui/imu.h`).

  ```

  ## Getting started

  1. Clone the repository onto your local system.
  2. Connect the ESP32 UWB3000 and modify `upload_port` and `monitor_port` in `platformio.ini`.
      > U1 is the initiator
      - AT: `env:at_sstwr/dstwr_u<1-6>`. 
      - DM: `env:dm_sstwr/dstwr_u<1-6>`
  3. Modify `NUM_NODES` and `INTERVAL` in `uwb.h`
  4. Upload the code `pio run -e <env name>` to each device

  ## Citation

  If you find this code useful in your research, please cite:

  ```bibtex
  @inproceedings{liu2025umotion,
    title={UMotion: Uncertainty-driven Human Motion Estimation from Inertial and Ultra-wideband Units},
    author={Liu, Huakun and Ota, Hiroki and Wei, Xin and Hirao, Yutaro and Perusquia-Hernandez, Monica and Uchiyama, Hideaki and Kiyokawa, Kiyoshi},
    booktitle={Proceedings of the Computer Vision and Pattern Recognition Conference},
    pages={7085--7094},
    year={2025}
  }
  ```

  ## TODO

  - [ ] IMU (BNO086)-UWB (DW3000) sensing

  ## Misc

  Note: If you encounter any issues or have questions, feel free to open an issue. You may also contact me via the email address: liu.huakun.li0@is.naist.jp.

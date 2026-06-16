# Examples

Two complete, runnable scripts take real recordings from common motion-capture
systems all the way to a valid BIDS dataset. Each script is **self-contained**:
on first run it downloads a small sample recording into a `data/` folder next to
the script, builds the channel metadata, validates, and exports the BIDS files.

!!! tip "Run them directly"
    Both scripts live in the [`examples/`](https://github.com/JuliusWelzel/motionbids/tree/main/examples)
    folder of the repository:

    ```bash
    python examples/from_c3d_vicon.py     # optical mocap (Vicon, .c3d)
    python examples/from_xdf_movella.py   # IMU sensors (Movella DOT, .xdf)
    ```

## Optical motion capture — Vicon (`.c3d`)

Converts 3D marker trajectories from a Vicon C3D recording into BIDS.

**This example shows how to:**

- Load a C3D file with [`ezc3d`](https://github.com/pyomeca/ezc3d)
- Read marker trajectories and the capture frame rate
- Convert marker units from millimetres (C3D default) to metres (BIDS)
- Build consistent `POS` channel metadata — one channel per marker and axis
- Validate, export, and plot a marker trajectory to sanity-check the result

!!! note "Requirements"
    ```bash
    pip install motionbids ezc3d numpy pandas matplotlib
    ```

```python title="examples/from_c3d_vicon.py"
--8<-- "examples/from_c3d_vicon.py"
```

## Inertial sensors — Movella DOT (`.xdf`)

Batch-converts Movella DOT IMU streams stored in XDF (LabStreamingLayer) files.

**This example shows how to:**

- Load XDF files with multiple streams using [`pyxdf`](https://github.com/xdf-modules/pyxdf)
- Detect the Movella DOT IMU stream automatically
- Compute the true sampling rate from timestamps (Movella reports a `0 Hz` nominal rate)
- Build `ACCEL` + `GYRO` channel metadata for each sensor
- Batch-process several subjects in a single run

!!! note "Requirements"
    ```bash
    pip install motionbids pyxdf numpy
    ```

```python title="examples/from_xdf_movella.py"
--8<-- "examples/from_xdf_movella.py"
```

## Next Steps

- [Workflow Guide](workflow.md) — step-by-step explanation of each stage
- [Class Reference](class-reference.md) — `MotionData` and `Channel` API
- [Schema Fields](schema-fields.md) — all available BIDS motion fields

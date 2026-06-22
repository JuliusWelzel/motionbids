# Examples

Two complete, runnable scripts take real recordings from common motion-capture
systems all the way to a valid BIDS dataset. Each script is **self-contained**:
on first run it downloads a small sample recording into a `data/` folder next to
the script, builds the channel metadata, validates, and exports the BIDS files.

<div class="grid cards" markdown>

-   :material-cctv:{ .lg .middle } **Optical motion capture — Vicon**

    ---

    Convert 3D marker trajectories from a Vicon `.c3d` recording.

    [:octicons-arrow-right-24: Vicon (C3D)](vicon-c3d.md)

-   :material-watch:{ .lg .middle } **Inertial sensors — Movella DOT**

    ---

    Batch-convert Movella DOT IMU streams from `.xdf` files.

    [:octicons-arrow-right-24: Movella DOT (XDF)](movella-xdf.md)

</div>

!!! tip "Run them directly"
    Both scripts live in the [`examples/`](https://github.com/JuliusWelzel/motionbids/tree/main/examples)
    folder of the repository:

    ```bash
    python examples/from_c3d_vicon.py     # optical mocap (Vicon, .c3d)
    python examples/from_xdf_movella.py   # IMU sensors (Movella DOT, .xdf)
    ```

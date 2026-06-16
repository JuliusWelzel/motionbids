---
title: 'motionbids: A lightweight Python package for BIDS Motion data curation'
tags:
  - Python
  - neuroscience
  - motion capture
  - BIDS
  - reproducibility
  - MoBI
  - multimodal
authors:
  - name: Julius Welzel
    orcid: 0000-0001-8958-0934
    affiliation: "1, 2"
  - name: Sein Jeung
    orcid: 0000-0002-0247-087X
    affiliation: 3
  - name: Ilaria D'Ascanio
    orcid: 0009-0000-1568-7149
    affiliation: 4
  - name: Francesca Tampellini
    orcid: 0000-0000-0000-0000 # Replace with your ORCID
    affiliation: 4
  - name: Sarah Blum
    orcid: 0000-0000-0000-0000 # Replace with
    affiliation: 2
  - name: Martin Geiger
    orcid: 0000-0000-0000-0000 # Replace with your ORCID
    affiliation: 5
    
affiliations:
 - name: University of Kiel, Department of Neurology, Kiel, Germany
   index: 1
 - name: University of Oldenburg, Department of Neuropsychology, Oldenburg, Germany
   index: 2
 - name: Technische Universität Berlin, Berlin, Germany
   index: 3
 - name: Department of Electrical, Electronic, and Information Engineering "Guglielmo Marconi", University of Bologna, Bologna, Italy
   index: 4 
 - name: Institute for Visualization and Interactive    Systems, University of Stuttgart, Stuttgart, Germany
   index: 5

date: 02 June 2026
bibliography: paper.bib
---

# Summary

`motionbids` is a Python package designed to facilitate the standardization of motion data according to the Brain Imaging Data Structure (BIDS). While BIDS was originally developed for neuroimaging (magnetic resonance imaging, MRI) [@Gorgolewski:2016], it has recently been extended to include motion data (Motion-BIDS) to support the growing field of behavioral neuroscience and Mobile Brain/Body Imaging (MoBI) [@Jeung:2024].

The package provides a lightweight, schema-driven interface for converting raw motion data, such as time series from optical motion capture systems or inertial measurement units (IMUs), into BIDS-compliant datasets including all relevant metadata. It aims to simplify the complexity of the BIDS file hierarchy and metadata requirements, allowing researchers to programmatically define channel attributes and export valid `.tsv` and `.json` sidecar files with minimal overhead.

# Statement of Need

The recording of body movements is increasingly central to neuroscientific research, particularly in MoBI experiments where participants move freely while their brain activity is recorded using mobile electroencephalography (EEG) or functional near-infrared spectroscopy (fNIRS). In these multimodal setups, precise synchronization and data organization are important for subsequent analysis. However, unlike neuroimaging data, which has benefited from mature standardization protocols, motion data has historically lacked a unified format [@welzel2024unisepunifiedsensorplacement]. While the C3D format is widely used in the biomechanics community, its usage is mostly limited to marker-based motion capture systems. On the other hand, more versatile data formats such as EDF or XDF lack metadata standards appropriate for representing motion data. This fragmentation has made data sharing and reproducibility difficult, as datasets often rely on proprietary formats or ad-hoc directory structures.

The theoretical framework for standardizing this data was recently formalized in the "Motion-BIDS" extension proposal (BEP029), described by @Jeung:2024. While this publication established *how* motion data should be organized, the scientific community still lacks a dedicated, standalone tool to implement this standard practically.

`motionbids` addresses this need by providing a dedicated, standalone Python tool for converting generic motion data to the BIDS standard. It is designed for researchers who need to curate motion datasets for publication or archiving. By ensuring that datasets are strictly compliant with the Motion-BIDS schema, `motionbids` promotes the Findability, Accessibility, Interoperability, and Reusability (FAIR) [@Wilkinson:2016] of behavioral data as well as respecting the current BIDS version.

# Multimodal Integration and Synchronization

A key feature of the Motion-BIDS extension—and a primary focus of `motionbids`—is its ability to facilitate multimodal integration. In complex experimental designs involving simultaneous recordings (e.g., EEG + Motion + Eye Tracking), data streams often have different sampling rates and start times.

`motionbids` supports the generation of the `scans.tsv` file, a critical component for multimodal alignment in BIDS. As specified in the BIDS standard, this file records the acquisition time (`acq_time`, an ISO 8601 timestamp) of each data file. By accurately documenting these timestamps, `motionbids` enables downstream analysis tools to temporally align motion trajectories with neural time series, effectively bridging the gap between behavioral kinematics and neural dynamics. This capability makes `motionbids` an essential utility for the MoBI community, ensuring that motion data can be seamlessly integrated into broader neuroimaging datasets.

# State of the Field

The Python ecosystem for neuroimaging data management is robust, with widely cited packages such as `NiBabel` [@Brett:2020] for file I/O, `Nipype` [@Gorgolewski:2011] for pipeline orchestration, and `PyBIDS` [@Yarkoni:2019] for querying BIDS datasets.

However, a gap exists for the specific task of *creating* Motion-BIDS datasets:
1.  **Lack of Standalone Converters:** Currently, there is no dedicated package in Python or MATLAB solely for converting motion data to BIDS. Existing BIDS conversion tools are embedded within larger, modality-specific suites (e.g., `MNE-BIDS` [@Appelhoff:2019] or `FieldTrip` [@Oostenveld:2011]). While FieldTrip's `data2bids` can write Motion-BIDS compatible files, robust conversion of motion data constitutes a substantial effort involving domain-specific information, making it impractical to expect maintainers of M/EEG toolboxes to fully support and sustain evolving motion-specific extensions.
2.  **Complexity of Existing Tools:** General-purpose converters like `HeuDiConv` or `BIDScoin` are primarily optimized for DICOM-to-NIfTI conversion in MRI workflows. Adapting them for motion data often requires significant "hacking" or manual intervention, which increases the risk of error and reduces accessibility for behavioral researchers who may not be familiar with MRI workflows.
3.  **Schema Compliance:** `motionbids` is explicitly "schema-driven." Unlike ad-hoc scripts, it validates user input against the BIDS schema definitions for motion data, ensuring that required metadata fields (e.g., `SamplingFrequency`, `TrackedPointsCount`) are present and correctly formatted before the data is written to disk.



# Acknowledgements

We acknowledge the foundational work of the whole BIDS community.

# References
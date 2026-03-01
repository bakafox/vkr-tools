# ASA pictures to brain zone activity converter

A simple tool that allows extracting ROI power data from EEG pictures created with ASA using exported heatmap.

For example, this picture:

![./readme-img.jpg]()

Can easily be turned into this:

```yaml
zone1: 12.34
zone2: 34.56
zone3: 56.78
...
```

## Usage

1. Create new Conda env: `conda env create -f asa2power.yml`

2. Enter into the created env: `conda activate asa2power`

3. Write a zones ROI file (easier than it seems):
    ```yaml
        # For proper scaling support, all scales are set in width\height
        # percentiles (from 0.0 to 1.0). All ROIs are set as rectangles,
        # for which you'll need its top-left and bottom-right coordinates.
        # For example, a 65th by 177th pixel in a 800 x 600px picture
        # will be set (65 / 800) = 0.08125 and (177 / 600) = 0.295 values.
        
        # These two fields correspond to yellow and blue rectangles on
        # a picture above, and are used to exctract maximum and minimum
        # brain activity values from image using character recognition.
        # They are always required to be present.
        HMAP_MAX:
            # Correspond to a top-left corner on a yellow rectangle to
            # its width and height respectively:
            - x1: 0.03536068
            - y1: 0.33795712
            # Correspond to a bottom-right corner on a yellow rectangle
            # to its width and height respectively:
            - x2: 0.11315417
            - y2: 0.36065574

        HMAP_MIN:
            # Correspond to a top-left corner on a blue rectangle to
            # its width and height respectively:
            - x1: 0.03536068
            - y1: 0.38713745
            # Correspond to a bottom-right corner on a blue rectangle
            # to its width and height respectively:
            - x2: 0.27361564
            - y2: 0.40983607

        # All fields below are completely optional, each describing one
        # ROI, and using the same notation. Their names should be unique.
        zone1:
            - x1: 0.14427157
            - y1: 0.11727616
            - x2: 0.21923621
            - y2: 0.18032787

        zone2:
            ...
    ```

4. Launch like this:
    ```bash
        python3 ./main.py \
            -i PATH_TO_IMAGES \ # Note that this is a path to a directory, not a file
            -z ZONE_ROIS.yaml \ # Your YAML file containing description for each zone
            -o PATH_TO_OUTPUT \ # Output YAMLs will have same names as input pictures
            -d # Whether to use debugging, omit to skip
    ```

5. Profit!

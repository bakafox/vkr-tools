# ASA pictures to brain zone activity converter

A simple tool that allows extracting ROI current density ($am/m$) data from EEG pictures created with [ASA (Advanced Source Analysis)](https://www.ant-neuro.com/products/asa) software using exported heatmap.

For example, this picture:

![asa output image](./example/imagesreadme-img.jpg)

Can easily be turned into this:

```yaml
zone1: 12.34
zone2: 34.56
zone3: 56.78
...
```

## Usage

1. Create new Conda env: `conda env create -f env.yaml`

2. Enter into the created env: `conda activate asa2power`

3. Launch like this:
    ```bash
        python3 ./main.py \
            PATH/TO/IMAGES \ # Note that this is a path to a directory, not a file
    ```

4. After that you will see the preview window. For now, you only need it to create your own zones file — moving your mouse will cursor coordinates on a chosen image, both in pixels and 0…1 relative units this program uses, and clicking will copy cursor's current position it last ones. Please note that, as this program automatically crops empty (black) space, coordinates created using 3rd-party tools are likely to be incorrect! You can find a template for zones file with more details in the examples directory.

5. Once you're done, launch like this:
    ```bash
        python3 ./main.py \
            PATH/TO/IMAGES \ # Note that this is a path to a directory, not a file
            ZONE_ROIS.yaml \ # Your YAML file containing description for each zone
            PATH/TO/OUTPUT \ # Output YAMLs will have same names as input pictures
    ```

6. Re-check that the zones are correct, and click on process button.

7. Profit!

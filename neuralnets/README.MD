All the neural networks used in my thesis.


## hypothesis1

Prove or disprove connections between odour categories and subjects' EEG brain zones' activations/deactivations, and possibly determine their reliability and/or strength.

The zones activity was extracted from EEG records using `eeg-cutter`, so the same 9 zones were used:

![zones](./attach/zones.png)

For the usage in the output later, a mean value from all vertices was found for each zone.

As of architecture, I used fully connected (FC) networks for simplicity. Augmentations were used to a low degree.

- **v1** — restore correlations directly between odour groups and brain zones' activity
- **v2** — also use spectral characteristics for the input layer
- **v3** — also use subject's ghedonic assessments for the input layer


## experiment

TO BE DONE!

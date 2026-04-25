All the neural network experiments used in my thesis, notebooks written in Russian.


## hypothesis

Prove or disprove connections between odour categories and subjects' EEG brain zones' activations/deactivations, and possibly determine their reliability and/or strength.

The zones activity was extracted from EEG records using `eeg-cutter`, so the same 9 zones were used:

![zones](./attach/zones.png)

For the usage in the output later, a mean value from all vertices was found for each zone.

As of architecture, I used fully connected (FC) networks for simplicity. Augmentations were used to a low degree.

- **1.0** — initial implementation
- **1.1** — adapted to work with updated project structure


## newgoal

The actual goal of my thesis, find and maximize correlations between ghedonic assesments of subjects and various characteristics obtained from their EEG records (and which exactly characteristics or their parts should be used, either together or separately).

- **1.0** — basic implementation, code still majorly based on `hypothesis` notebook
- **1.1** — added data scaling and sLORETA percentile clipping, which improved accuracy significantly
- **2.0** — simplified code, added weighted loss and metrics, various hyperparameters tweaking

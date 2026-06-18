All the neural network experiments used in my thesis, notebooks written in Russian.

The .py scripts are helper functions, so you're only interested in .ipynb files.


## hypothesis

Prove or disprove connections between odour categories and subjects' EEG brain zones' activations/deactivations, and possibly determine their reliability and/or strength.

The zones activity was extracted from EEG records using `eeg-cutter`, so the same 9 zones were used:

![zones](./attach/zones.png)

For the usage in the output later, a mean value from all vertices was found for each zone.

As of architecture, I used fully connected (FC) networks for simplicity. Augmentations were used to a low degree.

- **`1.0`** — initial implementation
- **`1.1`** — adapted to work with modern (as of `newgoal 2.X`) project structure


## newgoal

The final goal of my thesis we agreed with my prof on: find and maximize correlations between ghedonic assesments of subjects and various characteristics obtained from their EEG records (and which exactly characteristics or their parts should be used, either together or separately).

To make the results more objective even despite a limited dataset, versions **`3.1`**, **`3.2`**, **`3.3`** and **`3.4`** were ran 10 times, with 10 randomly chosen (but the same across each session) seeds.

- **`1.0`** — basic implementation, code still majorly based on `hypothesis` notebook
- **`1.1`** — added data scaling and sLORETA percentile clipping, which improved accuracy significantly
- **`2.0`** — simplified code, added weighted loss and metrics, various hyperparameters tweaking
- **`2.1`** — experiments with data scaling and using distinct seeds for ebsemble models, which improved overall accuracy but has also biased error correlations matrix
- **`2.2`** — added features importance analysis and rose of winds visualizarion, more hyperparameters and loss functions tuning, fixed critical bug in final metric
- **`3.0`** — use dataset pruning based on FIA (resulted in noticeable accuracy improvement), add metainfo-only model comparison, small tweaks to feature analysis visualizations
- **`3.1`** — replaced K-Fold cross-validation strategy with LeaveOneGroupOut (LOGO) to check the "model doesn't actually need categories" hypothesis, better ensemble weighing (both improved the accuracy notably), other improvements
- **`3.2`** — version `3.1` with K-Fold instead of LOGO cross-validation
- **`3.3`** — version `3.1` with K-Fold instead of LOGO, without dataset pruning and dummy model
- **`3.4`** — version `3.1` without dataset pruning and dummy model

If you're interested in using the code for the further research, I recommend using **`3.1`** (or **`3.2`** if you cannot divive your data by subjects), as, based on both metrics and my tests, it should give you the best accuracy. There are also a few notable variations available for some versions:

- **_CB** — uses CatBoostClassifier as a baseline, not used in thesis directly but has been added to the final defense presentaion based on feedback I received on pre-defence
- **_export** — final verified versions I submitted for my thesis, based on `3.1` and `3.2`, mostly only different in having more clear Markdown explanations and redundant code / comments removed

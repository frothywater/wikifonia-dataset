# Wikifonia MIDI Dataset

Convert Wikifonia MusicXML lead sheet dataset to MIDI dataset with chord markers.

## Usage
Currently, user has to revise path to dataset and output directories in `src/main.py` before converting the whole dataset. Then run:
```bash
python3 src/main.py
```

## Repo Structure
All source codes are placed in `src` folder.
- `main.py`: Convert the whole dataset.
- `convert.py`: Logic of converting scores.
- `chord.py`: Logic of handling chord markers.
- `test.py`: Debug functions of this repo.


## About Dataset
Wikifonia is a lead sheet dataset containing over 6000 human-written scores in MusicXML format. The dataset is in public domain and can be downloaded [here][3].

### Known Issues
One problem about this dataset so far is, few symbolic music processing package can handle *repeat signs* in the scores, which is very common in score writing convention. [`music21`][1] is one package can handle repetition, however, in practice, over 1000 scores in Wikifonia dataset failed to convert to MIDI file when taking account to repeat signs. Therefore, expansion to repeat signs is disabled by default. But it can still be enabled by setting `expand_repeat` flag in `convert.convert_score()`, though it's no recommended.

Another problem is realization of musical expressions, including appoggiatura, fermatas, mordents, trills, turns, etc. Those musical elements can be expressed and performed with human-written score easily, but can hardly be well notated in MIDI file format. Also, for only computational task of this dataset, such as machine learning, expressions related to performance may not be desirable. Likewise, realization of expressions is disabled by default and can be enabled by setting `realize_expression` flag in `convert.convert_score()`.

Moreover, as currently known, one score file in Wikifonia dataset will produce MIDI file with a extra long note, which cause it unusable: `Les Kettley - Don't Ask.mxl`. User may consider to remove it before converting.

## Dependencies
Dependencies of this repo are:
- [`music21`][1]: Processing multiple formats of symbolic music file.
- [`mido`][2]: Processing MIDI files.

## Contribution
This repo is licensed under MIT, and any contribution is welcome!

[1]: https://web.mit.edu/music21/doc/index.html
[2]: https://mido.readthedocs.io/en/latest/
[3]: http://www.synthzone.com/files/Wikifonia/Wikifonia.zip
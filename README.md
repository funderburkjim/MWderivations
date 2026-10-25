# MWderivations

_Created: 14-06-2026 · Last updated: 11-07-2026_

Derivations of headwords in the **Monier-Williams (1899)** Sanskrit–English
dictionary — a computational investigation that identifies, for each substantive
headword (noun, adjective, indeclinable), how it is derived from a parent form.

> This repository is a research workspace, not a software product. It holds a
> multi-stage text pipeline (Python scripts + tab-delimited data files) plus the
> `.org`/`.md` sub-directory readmes that document each stage's method and data
> sources.

## What it does

Monier-Williams designed the dictionary to make the interrelations of Sanskrit
words obvious, as he explains in the preface —
[Section II of the MW preface](http://www.sanskrit-lexicon.uni-koeln.de/scans/csldoc/dictionaries/prefaces/mwpref/mwpref11.html).
The Cologne digitization encodes this **4-level system** in its markup, which
makes computer-assisted study feasible. The primary relations are visible in the
Cologne list displays, e.g. the
[MWScan webtc1 list](http://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2014/web/webtc1/index.php)
and the
[apidev sample list](http://www.sanskrit-lexicon.uni-koeln.de/scans/awork/apidev/sample/list-0.2.html).

This repository is one such investigation: it aims to give a systematic
identification of the derivation of the substantives, using the 4-level system
as much as possible. Each analyzed headword is classified by the last analysis
step that explained it (secondary-suffix addition, two-part compound, prefix +
known headword, feminine of a sibling, etc.), and marked `DONE` when explained or
`TODO` when not.

## Pipeline layout

The computation runs in numbered stages; each stage's directory has its own
readme with the full method, field definitions, and data provenance.

| Directory | Role | Key readme | Main output |
|---|---|---|---|
| [`step2/`](https://github.com/gasyoun/MWderivations/tree/master/step2) | Earlier version — **now considered obsolete** (see [`redo_all.sh`](https://github.com/gasyoun/MWderivations/blob/master/redo_all.sh)) | [`step2/readme.md`](https://github.com/gasyoun/MWderivations/blob/master/step2/readme.md), [`step2/readme_procedure.org`](https://github.com/gasyoun/MWderivations/blob/master/step2/readme_procedure.org) | [`step2/analysis.txt`](https://github.com/gasyoun/MWderivations/blob/master/step2/analysis.txt) |
| [`step3/`](https://github.com/gasyoun/MWderivations/tree/master/step3) | Use the H-code to help with *samāsa* (compound) analysis | [`step3/readme.org`](https://github.com/gasyoun/MWderivations/blob/master/step3/readme.org) | [`step3/analysis2.txt`](https://github.com/gasyoun/MWderivations/blob/master/step3/analysis2.txt) |
| [`step4/`](https://github.com/gasyoun/MWderivations/tree/master/step4) | Revise H-codes to further help the analysis (latest stage) | [`step4/readme.org`](https://github.com/gasyoun/MWderivations/blob/master/step4/readme.org), [`step4/notes.org`](https://github.com/gasyoun/MWderivations/blob/master/step4/notes.org) | [`step4/analysis2.txt`](https://github.com/gasyoun/MWderivations/blob/master/step4/analysis2.txt) |
| [`compounds/`](https://github.com/gasyoun/MWderivations/tree/master/compounds) | Gather the compounds from `step4/all.txt` into a simplified list | [`compounds/readme.txt`](https://github.com/gasyoun/MWderivations/blob/master/compounds/readme.txt) | [`compounds/compounds.txt`](https://github.com/gasyoun/MWderivations/blob/master/compounds/compounds.txt), [`compounds/compounds.html`](https://github.com/gasyoun/MWderivations/blob/master/compounds/compounds.html) |

Current data sizes: [`step3/analysis2.txt`](https://github.com/gasyoun/MWderivations/blob/master/step3/analysis2.txt)
and [`step4/analysis2.txt`](https://github.com/gasyoun/MWderivations/blob/master/step4/analysis2.txt)
each hold **220,248** records; [`compounds/compounds.txt`](https://github.com/gasyoun/MWderivations/blob/master/compounds/compounds.txt)
holds **12,609** entries. In the step4 analysis, **5,667** records remain
unexplained (`TODO`).

### Output format (`analysis2.txt` / `analysis.txt`)

Each line is one MW record, tab-delimited (fields per
[`step2/readme.md`](https://github.com/gasyoun/MWderivations/blob/master/step2/readme.md)):
H-code · L-number · key1 · key2 (normalized) · `lex` · analysis · status
(`NTD`/`DONE`/`TODO`) · note (the last analysis step applied, e.g. `wsfx`,
`cpd1`, `srs1`, `pfx1`, `gender`).

## Reproducing the computation

```sh
sh redo_datasources.sh   # copy the external data sources into place (see below)
sh redo_all.sh           # recompute step3 then step4; log to step4/redo_log.txt
```

[`redo_datasources.sh`](https://github.com/gasyoun/MWderivations/blob/master/redo_datasources.sh)
copies inputs from sibling repositories, so the pipeline assumes those are cloned
alongside this one:

- `lexnorm-all.txt` — from
  [funderburkjim/MWlexnorm](https://github.com/funderburkjim/MWlexnorm)
  (`step1b/lexnorm-all.txt`), 198,467 nominal/indeclinable records.
- `verb_step0a.txt` — from
  [funderburkjim/MWvlex](https://github.com/funderburkjim/MWvlex) (`step0/`).
- `mw.xml` — the Cologne MW digitization, from the `mwxml` source repository.

Scripts are Python 2-era (`.pyc` artifacts for `partition`, `scharfsandhi`,
`scharfsandhiWrapper` are checked in); run in the environment the original stage
readmes assume.

## Provenance

The analysis and pipeline are the work of **Jim Funderburk** (upstream
[funderburkjim/MWderivations](https://github.com/funderburkjim/MWderivations));
this repository is the [gasyoun](https://github.com/gasyoun) fork, part of the
[Cologne Digital Sanskrit Dictionaries](https://www.sanskrit-lexicon.uni-koeln.de/)
ecosystem. It is distinct from the sibling repos **MWinflect** (inflectional
forms), **MWlexnorm** (lexical-category normalization — a *data source* here),
and **MWvlex** (verb lexicon — also a data source here); do not conflate them.

Historical status note (from the original README, Feb 9 2016): at that time about
9,000 records (~5%) remained without a derivation, many expected to resolve via an
external source of `kta` forms and gerunds of roots.

_Dr. Mārcis Gasūns_

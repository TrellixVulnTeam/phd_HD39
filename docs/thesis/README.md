# Deep Learning for Compilers

[Chris Cummins](https://chriscummins.cc). PhD Thesis.

<a href="https://chriscummins.cc/u/ed/phd-thesis.pdf" style="border: solid 1px #000">
  <img src="thesis.png" height="325" style="border: solid 1px #000">
</a>

> Constructing compilers is hard. Optimising compilers are
> multi-million dollar projects spanning years of development, yet
> remain unable to fully exploit the available performance, and are
> prone to bugs. The rapid transition to heterogeneous parallelism and
> diverse architectures has raised demand for aggressively-optimising
> compilers to an all time high, leaving compiler developers
> struggling to keep up. What is needed are better tools to simplify
> compiler construction.
>
> This thesis presents new techniques that dramatically lower the cost
> of compiler construction, while improving robustness and
> performance. The enabling insight for this research is the
> leveraging of deep learning to model the correlations between source
> code and program behaviour, enabling tasks which previously required
> significant engineering effort to be automated. This is demonstrated
> in three domains:
>
> First, a generative model for compiler benchmarks is developed. The
> model requires no prior knowledge of programming languages, yet
> produces output of such quality that professional software
> developers cannot distinguish generated from handwritten
> programs. The efficacy of the generator is demonstrated by
> supplementing the training data of predictive models for compiler
> optimisations. The generator yields an automatic improvement in
> heuristic performance, and exposes weaknesses in state-of-the-art
> approaches which, when corrected, yield further performance
> improvements.
>
> Second, a compiler fuzzer is developed which is far simpler than
> prior techniques. By learning a generative model rather than
> engineering a generator from scratch, it is implemented in 100x
> fewer lines of code than the state-of-the-art, yet is capable of
> exposing bugs which prior techniques cannot. An extensive testing
> campaign reveals 67 new bugs in OpenCL compilers, many of which have
> now been fixed.
>
> Finally, this thesis addresses the challenge of feature design. A
> methodology for learning compiler heuristics is presented that, in
> contrast to prior approaches, learns directly over the raw textual
> representation of programs. The approach outperforms
> state-of-the-art models with hand-engineered features in two
> challenging optimisation domains, without requiring any expert
> guidance. Additionally, the methodology enables models trained in
> one task to be adapted to perform another, permitting the novel
> transfer of information between optimisation problem domains.
>
> The techniques developed in these three contrasting domains
> demonstrate the exciting potential of deep learning to simplify and
> improve compiler construction. The outcomes of this thesis enable
> new lines of research to equip compiler developers to keep up with
> the rapidly evolving landscape of heterogeneous architectures.


```
@phdthesis{Cummins2020,
  author = {Cummins, Chris},
  school = {University of Edinburgh},
  title = {{Deep Learning for Compilers}},
  year = {2020}
}
```

[**Download PDF**](https://chriscummins.cc/u/ed/phd-thesis.pdf).

Build using:

```sh
$ bazel build //docs/thesis
```

Requires `bazel`, `pdflatex`, `biber` and `Pygments`. On macOS:

```sh
$ brew install bazel
$ brew cask install mactex
$ python -m pip install -U Pygments
```

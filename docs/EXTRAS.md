### Extra: Installing Pillow-SIMD for faster performance

Only affects MMVSkia

While this package is not required and you can keep the default Pillow package, using [pillow-simd](https://github.com/uploadcare/pillow-simd) instead of the vanilla package, as you can see [here](https://python-pillow.org/pillow-perf/), is indeed faster, however Pillow isn't the biggest bottleneck in the code, so you'd get performances (guessing) at most 10% faster.

Currently only rotating the images uses the PIL project.

Install the listed [prerequisites](https://pillow.readthedocs.io/en/stable/installation.html#building-from-source) according to your platform on their documentation, and as mentioned on the main repo README, install `pillow-simd` with:

```bash
$ pip uninstall pillow
$ pip install pillow-simd
```

If you want you can use AVX2 enabled build installation with:

```bash
$ pip uninstall pillow
$ CC="cc -mavx2" pip install -U --force-reinstall pillow-simd
```

You can safely skip this section and use regular Pillow, but with longer render times this few performance gains can stack a lot.
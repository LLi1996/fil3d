# Fil3D

### TODO
- quick start addition: how to mitigate potential memory issues
- Search for all GALFA related constants and remove/make them user configurable
- Add a faster algorithm for mask matching
- Add a class wrapper for using trees to access data from underlying data cubes (nice to have)
- Add a class wrapper for constructing trees from masks (nice to have)
- Add a few example notebooks with non-injected filaments and images (nice to have)
- Cleanup around the visualization modules (nice to have)


### Links
- [Docs](https://lli1996.github.io/fil3d/)


### Project Structure
- Project under `fil3d`
- Sphinx source under `docsrc`
    - Structure mainly following [this nice blog](https://www.docslikecode.com/articles/github-pages-python-sphinx/).
- Sphinx pages under `docs`
    - Jekyll bypass with [this trick](https://github.blog/2009-12-29-bypassing-jekyll-on-github-pages/).
    - Sphinx make & artifact copy tricks following [this nice comment](https://github.com/sphinx-doc/sphinx/issues/3382#issuecomment-470772316).
    - This is a compromise - we don't really want to push _any_ build artifacts to github but we have to do this to use
    github pages.

#### Docs Updates
Sphinx is initialized under `docsrc` and the config file is under the usual location `docsrc/conf.py`.

To build docs / refresh artifacts under `docs`, simply go to `docsrc` and do:
```shell
make github
```
This will build the pages and then copy them into `docs`, the root of github pages.

If you want to locally see the site before pushing things up, you can do something like this:
```shell
python -m http.server 8000
```
And point your browser at `localhost:8000`.

Once happy, just don't forget to check in changes under `docs` and `docsrc` before pushing to github (the `_build`
directory under `docsrc` should be ignored by default so you don't have to worry about pushing garbage up).

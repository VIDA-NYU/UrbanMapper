<div align="center">
   <h1>UrbanMapper</h1>
   <h3>Enrich Urban Layers Given Urban Datasets</h3>
   <p><i>with ease-of-use API and Sklearn-alike Shareable & Reproducible Urban Pipeline</i></p>
</div>

___

> [!IMPORTANT]
> - The current implementation is meant to find only execution exceptions. No evaluation of the output quality has been done yet.
> - In the future, github actions can be added to run more automatic tests.  

# Overview of the test folder

We use [pytest](https://docs.pytest.org/en/stable/) library to implement UrbanMapper Unit Tests.

Test files are located in the `UrbanMapper/test` folder and follow a structure similar to that of `UrbanMapper/src`.

There is an additional `UrbanMapper/test/data_files` folder with simple dataset versions used in the tests. 

# Beginning tests

After cloning `UrbanMapper` repository and  installing it, you should run

 ```bash
 cd UrbanMapper
 pytest test/
 ```

If you want to disable warnings, add the following flag 

 ```bash
 pytest --disable-warnings test/
 ```

 You can also use `uv`

 ```bash
 uv run pytest
 ```

# Simple tips

As the tests are implemented with `pytest` library, you should use the same naming prefix standards to add new test cases, such as 

1. Python files: `test_` 

2. Classes: `Test`

3. Functions: `test_`

Here is an example based on `test_pipeline.py`

 ```python
 class TestUrbanPipeline:
    def test_compose(self):
       ...

    def test_transform(self):
       ...

    def test_save(self):
       ...
 ```

If necessary, you can skip some function test by using the `skip` decorator, for example

 ```python
 import pytest

 class TestUrbanPipeline:
    def test_compose(self):
       ...

    @pytest.mark.skip()
    def test_transform(self):
       ...

    def test_save(self):
       ...
 ```

Or even skip a whole class

 ```python
 import pytest

 @pytest.mark.skip()
 class TestUrbanPipeline:
    def test_compose(self):
       ...

    def test_transform(self):
       ...

    def test_save(self):
       ...
 ```

More information can be found on the [pytest](https://docs.pytest.org/en/stable/) webpage.

## Licence

`UrbanMapper` is released under the [MIT Licence](./LICENCE).

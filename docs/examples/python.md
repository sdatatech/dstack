# Python

The [`bash`](../reference/providers/bash.md), [`code`](../reference/providers/code.md), 
[`lab`](../reference/providers/lab.md), and [`notebook`](../reference/providers/notebook.md) providers
come with Python and Conda pre-installed.

Create the `.dstack/workflows.yaml` and `hello.py` files in your project directory:

```yaml
workflows:
  - name: hello-py
    provider: bash
    commands:
      - python hello.py
```

Now, use the `dstack run` command to run it:

```shell
dstack run hello-py
```

You'll see the output in real-time as your workflow is running:

```shell
RUN           WORKFLOW  STATUS     APPS  ARTIFACTS  SUBMITTED  TAG 
slim-shady-1  hello     Submitted                   now 
 
Provisioning... It may take up to a minute. ✓

To interrupt, press Ctrl+C.

Hello, world
```

#### Python packages

You can use the `pip` or the `conda` executables to install Python packages:

```yaml
workflows:
  - name: hello-pandas
    provider: bash
    commands:
      - conda install pandas -y
      - python hello_pandas.py
```

!!! tip "NOTE:"
    You can create custom Conda environments using `conda env create --prefix` 
    and save them as artifacts. This way you can reuse pre-built environments from other workflows.

#### Python version

By default, the workflow uses the same Python version that you use locally. 
You can override the major Python version using the `python` property.

```yaml
workflows:
  - name: hello-py-39
    provider: bash
    python: 3.9
    commands:
      - python hello.py
```
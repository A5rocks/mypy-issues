## `mypy` issues

Find how your `mypy` change affects `mypy`'s open issues.

Use cases:
 - `mypy-primer` on a more varied corpus.
 - broad changes that might fix several issues.
 - seeing what issues might be fixed between two revisions.
 - statistics on issues by editing `compare.py`.

Future ideas:
 - compare crashes
   - do paths change?
   - did one version crash and the other didn't?
 - decrease noisiness of results
 - decrease startup costs
   - bulk generate temp files for issues before running `mypy` on all of them?
   - upstream changes? (copy sorbet and have typeshed already cached?)
   - maybe there's a flag?
 - remove closed issues when running `main.py`

#### usage: generation

There are two modes: downloading everything from `mypy`'s issue tracker and getting the diff in output. To download everything from `mypy`'s issue tracker, all you need is:

```sh
$ python -m venv generation-venv
$ . ./generation-venv/bin/activate
$ pip install -r requirements.txt
$ python main.py
```

If you run into ratelimits, then create a [GitHub Personal Access Token](https://github.com/settings/tokens?type=beta). The ratelimits are as follows:
 - without a PAT: 60 requests an hour
 - with a PAT: 5000 requests an hour, across your whole account


`main.py` should only make 3600 requests an hour at most, meaning it should never hit a ratelimit. Additionally, it will only fetch new issue comments if rerun.

#### usage: comparing `mypy`s

```sh
$ python -m venv venv1
$ python -m venv venv2
# NOTE: The above names are hardcoded in the script.
$ ./venv1/bin/pip install git+https://github.com/python/mypy.git
$ ./venv2/bin/pip install git+https://github.com/[you]/mypy.git@[whatever]
# get a specific PR with:
$ ./venv2/bin/pip install git+https://github.com/python/mypy.git@refs/pull/[whatever]/head

# ... and finally:
$ python compare.py
```

`compare.py` doesn't need any dependencies. Additionally, I'm not sure how long it takes to compare `mypy`s; I've just left my computer running overnight in the past.

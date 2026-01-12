# Local install for CLI use

This repo is a fork of `atopile/atopile`. The steps below show how to install it into another repository with `uv` so you can use the `ato` CLI from that repo.

## Install this fork into another repo

From the target repo where you want to use the CLI:

```sh
# Add this fork as an editable dependency
uv add --editable /path/to/atopile

# Zig build helper used by the editable install
uv add "ziglang==0.14.1"

# Verify the CLI is available
uv run ato --help
```

Notes:
- `--editable` keeps the install linked to your local checkout so changes in this repo are reflected immediately.
- If your project uses a `pyproject.toml` workspace or a custom `uv` setup, keep the dependency in the same environment you use to run commands.

## Pull upstream changes from the original repo

This repo is a fork of `https://github.com/atopile/atopile`. Add the upstream remote once, then fetch and merge when you need updates:

```sh
# In this repo

git remote add upstream https://github.com/atopile/atopile

# Get upstream changes
git fetch upstream

# Merge (or rebase) from upstream main
# Pick one of these

git merge upstream/main
# or
git rebase upstream/main
```

If you keep a fork on GitHub, push the updated branch as usual:

```sh
git push origin main
```

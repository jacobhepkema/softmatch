# Installation

SoftMatch requires Python 3.8 or later.

## Using pip

You can install SoftMatch directly from the source or via pip (if published):

```bash
pip install softmatch
```

## Using uv (Recommended)

If you are using `uv` for package management, you can add it to your project:

```bash
uv add softmatch
```

Or run it directly without installing:

```bash
uv run --with softmatch softmatch --help
```

## Development Installation

To set up a development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/youruser/softmatch.git
   cd softmatch
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

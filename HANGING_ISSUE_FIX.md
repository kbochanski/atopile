# Command Hanging Issue - Fix Documentation

## Issue Summary

The `ato create project` command was hanging indefinitely, preventing users from creating new projects.

## Symptoms

- Command `ato create project` or `ato create project --path <path>` would hang without any output
- No error messages or progress indicators
- Process would consume CPU but never complete
- Required manual termination with Ctrl+C

## Root Cause Analysis

Through debugging, the issue was traced to the `configure.setup()` function being called for all commands, including those that don't require KiCad setup (like `create project`).

### Specific Problems Identified

1. **KiCad Plugin Setup Blocking**: The `configure.setup()` function attempts to:
   - Import KiCad IPC modules (`faebryk.libs.kicad.ipc`)
   - Install KiCad plugins
   - Enable KiCad plugin API
   
   These operations could hang when:
   - KiCad configuration files are inaccessible
   - KiCad paths cannot be resolved
   - File system operations block
   - Import statements trigger blocking operations

2. **Unnecessary Setup for Create Command**: The `create project` command doesn't require KiCad to be set up, yet it was waiting for KiCad setup to complete.

3. **Interactive Prompt Issues**: The original implementation used `questionary.path()` which creates an interactive file browser that can hang in certain terminal environments.

## Solution

### 1. Skip KiCad Setup for Non-Build Commands

Modified `src/atopile/cli/cli.py` to conditionally skip KiCad setup for commands that don't need it:

```python
# Skip KiCad setup for commands that don't need it to avoid hanging
skip_kicad_setup = ctx.invoked_subcommand in ("create", "dependencies", "add", "remove", "sync")

if not skip_kicad_setup:
    configure.setup()
else:
    # Still do basic setup (cleanup legacy config) but skip KiCad plugin
    from faebryk.libs.paths import get_config_dir
    try:
        _LEGACY_CFG_PATH = get_config_dir() / "configured_for.yaml"
        if _LEGACY_CFG_PATH.exists():
            _LEGACY_CFG_PATH.unlink()
    except Exception:
        pass
```

**Commands that skip KiCad setup:**
- `create` - Creating projects/packages doesn't need KiCad
- `dependencies` - Dependency management doesn't need KiCad
- `add` - Adding dependencies doesn't need KiCad
- `remove` - Removing dependencies doesn't need KiCad
- `sync` - Syncing dependencies doesn't need KiCad

**Commands that still run KiCad setup:**
- `build` - Requires KiCad for PCB generation
- `view` - May require KiCad for viewing schematics/PCBs
- Other commands that interact with KiCad

### 2. Fixed Path Display Bug

Fixed `_open_in_editor_or_print_path()` in `src/atopile/cli/create.py` to handle paths outside the current working directory:

```python
def _open_in_editor_or_print_path(path: Path):
    # check if running in vscode / cursor terminal
    if code_bin := get_code_bin_of_terminal():
        # open in vscode / cursor
        subprocess.Popen([code_bin, path])
    else:
        # Use absolute path if relative path would fail
        try:
            rel_path = path.relative_to(Path.cwd())
            rich_print_robust(f" \n[cyan]cd {rel_path}[/cyan]")
        except ValueError:
            # Path is not a subpath of current directory, use absolute path
            rich_print_robust(f" \n[cyan]cd {path}[/cyan]")
```

### 3. Improved Interactive Prompts

Replaced `questionary.path()` with Python's built-in `input()` for Path queries in `src/atopile/cli/create.py`:

- More reliable across different terminal environments
- Simpler interface for users
- Avoids hanging issues with interactive file browsers

### 4. Made KiCad Setup More Resilient

Updated `src/atopile/cli/configure.py` to:
- Use lazy imports for KiCad modules
- Wrap all KiCad operations in try-except blocks
- Use threading with timeout (though skipped for create command)
- Log warnings instead of failing when KiCad setup has issues

## Files Modified

1. `src/atopile/cli/cli.py` - Conditional KiCad setup skipping
2. `src/atopile/cli/create.py` - Fixed path display, improved prompts
3. `src/atopile/cli/configure.py` - Made KiCad setup more resilient

## Verification

To verify the fix works:

```bash
# Test creating a project
ato create project --path /tmp/test-project

# Should complete successfully with output:
# ✨ Created new project "my_first_ato_project"! ✨
```

The command should complete in seconds without hanging.

## Prevention

To prevent similar issues in the future:

1. **Lazy Loading**: Import heavy dependencies (like KiCad modules) only when needed
2. **Conditional Setup**: Only run setup operations for commands that require them
3. **Error Handling**: Wrap potentially blocking operations in try-except blocks
4. **Timeouts**: Consider using timeouts for operations that might hang
5. **Testing**: Test commands in environments where dependencies might not be available

## Related Issues

- Interactive prompts hanging in certain terminal environments
- KiCad setup blocking commands that don't need KiCad
- Path display errors when project is created outside current directory

## Date Fixed

Fixed in commit addressing hanging issue with `ato create project` command.

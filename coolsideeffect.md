# Cool Side Effect: One-Time Script Execution

⚠️ **This is emergent behavior, not an intended feature!**

## What Happened

While designing yanked v2.0's dual installation methods, an interesting side effect emerged: the `inst` method can be used to run single-file scripts **once** without installing them permanently.

## How It Works

Due to yanked's process replacement architecture:

1. **User runs**: `yanked` → chooses `inst` method → provides script URL
2. **yanked downloads** the script to `/tmp/yanked/installer_scriptname_pid`
3. **yanked saves** basic tracking info (just app name, no file location)  
4. **yanked exec's** the script using `os.execv()`
5. **Script runs directly** - gets full terminal control, then exits
6. **No permanent installation** - script runs once and disappears from `/tmp/yanked/` on next yanked startup

## Example Use Case

```bash
# Run a one-time analysis script without installing it
yanked
# URL: https://github.com/user/repo
# File: analyze-logs.py  
# Method: inst  # ← The key!
# App: log-analyzer

# Script runs immediately, processes your data, shows results, exits
# No permanent files left behind (except in yanked's tracking database)
```

## Why This Works (Architecture)

The `inst` method was designed for **custom installers** that:
- Take full control of the terminal
- Handle their own file placement
- Exit when done

But since `os.execv()` simply **replaces the current process**, it works equally well for:
- Scripts that just run and exit
- One-time utilities
- Analysis tools
- Temporary data processors

The emergent behavior comes from the fact that **not all executables are installers** - some are just programs that run and exit!

## Limitations & Warnings

⚠️ **This is not a supported use case:**

1. **Tracking pollution**: yanked's database will contain "installed" entries for scripts that aren't actually installed
2. **Confusing uninstall**: `yanked uninstall script-name` will only remove database entry, not files (because there are no files)
3. **Upgrade weirdness**: `yanked upgrade script-name` will re-download and re-run the script
4. **Not designed for this**: May break in future versions as `inst` method evolves

## Better Alternatives

For one-time script execution, consider:

```bash
# Direct execution (if you trust the source)
curl -s https://raw.githubusercontent.com/user/repo/main/script.py | python3

# Download and run manually
wget https://raw.githubusercontent.com/user/repo/main/script.sh
chmod +x script.sh
./script.sh
rm script.sh
```

## Why We're Not "Fixing" This

This emergent behavior demonstrates good architectural design:
- **Process replacement** works for any executable, not just installers
- **Clean separation** between yanked and executed code
- **No assumptions** about what the executed script does

The side effect exists because the architecture is **correctly generic** - `os.execv()` replaces processes, regardless of whether they're installers or regular programs.

## Architectural Insight

This reveals that yanked v2.0's `inst` method is actually a **generic script runner** that happens to be optimized for installation use cases. The process replacement pattern creates a clean execution environment that works for any executable script.

---

**Remember**: This is emergent behavior, not a feature. If you rely on it, future yanked updates might break your workflow. Use standard script execution methods for one-time runs!
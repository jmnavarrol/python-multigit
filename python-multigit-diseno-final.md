# Final Design Snapshot: python-multigit Split

## Working Repository

- GitHub repository to modify: https://github.com/jmnavarrol/python-multigit

## Final Objective

Split the current single Python distribution into two independent distributions, kept in a single Git repository and still built with hatchling:

1. A reusable library distribution.
2. A command-line distribution.

Both distributions must evolve and be versioned independently.

## Final Naming Decisions

### Distribution names (PyPI level)

1. multigit-lib: library distribution.
2. multigit: command-line distribution.

### Import package names (Python level)

1. multigit: import package for the library.
2. multigit_cli: internal import package for the CLI application.

### Shell command name

1. multigit: command exposed by the CLI distribution.

## Architecture Boundaries

### Library responsibilities (multigit-lib)

1. Receive already-processed native Python data structures.
2. Validate domain-level input coherence.
3. Execute repository status/update logic.
4. Return structured results and raise domain exceptions.

### Library non-responsibilities

1. No direct reading of config files.
2. No environment variable lookup.
3. No console rendering.
4. No sys.exit process termination behavior.

### CLI responsibilities (multigit)

1. Parse command-line arguments.
2. Resolve config sources (file, env vars, flags, future providers).
3. Parse YAML and map it to library input structures.
4. Call library services.
5. Render output and decide exit codes.

## Data Flow Contract

1. Input adapters live in CLI (for example YAML loader).
2. CLI transforms input into native domain objects accepted by library.
3. Library processes and returns structured result objects.
4. CLI formats those results for end users.

## Target Repository Layout

		python-multigit/
			pyproject.toml                    # CLI distribution: multigit
			README.md
			src/
				multigit_cli/
					__init__.py
					__about__.py
					__main__.py
					console.py
					config.py
					loaders/
						__init__.py
						yaml_loader.py

			lib/
				pyproject.toml                  # Library distribution: multigit-lib
				README.md
				src/
					multigit/
						__init__.py
						__about__.py
						models.py
						exceptions.py
						gitrepo.py
						processor.py

## Packaging Rules

### Library (lib/pyproject.toml)

1. project.name = multigit-lib
2. Build backend: hatchling
3. Version source independent from CLI
4. Package to build: lib/src/multigit

### CLI (root pyproject.toml)

1. project.name = multigit
2. Build backend: hatchling
3. Console entry point command: multigit
4. Console entry point target: multigit_cli.__main__:main
5. Dependency on library with compatibility range

## Dependency Contract Between Distributions

CLI distribution depends on library distribution using a compatible major range:

1. multigit depends on multigit-lib>=1.0,<2

This allows independent evolution while protecting runtime compatibility.

## Versioning Policy

### Independent versions

1. multigit-lib version is independent.
2. multigit version is independent.

### Initial baseline

1. multigit-lib: 1.0.0
2. multigit: 0.12.0

### Update rules

1. Library internal changes without API break: bump only multigit-lib.
2. CLI behavior/features without library API change: bump only multigit.
3. Library API breaking change: major bump in multigit-lib and update CLI dependency range.

## Release Order

For each release cycle:

1. Build and publish multigit-lib first.
2. Validate installation and compatibility.
3. Build and publish multigit.

## Functional Design Requirements Preserved

1. CLI remains responsible for user-facing behavior and output.
2. Library remains reusable by external programs without CLI installation.
3. Future extensions, such as configurable subrepos file naming, are handled in CLI adapters unless they require library API evolution.

## Implementation Sequence (Approved)

1. Introduce library domain models and exceptions.
2. Extract Git operations into reusable library service.
3. Add pure Processor API in library.
4. Move YAML parsing/validation into CLI adapter layer.
5. Move console rendering into CLI layer.
6. Keep CLI entry point as thin orchestrator.
7. Split packaging into two hatchling projects in one repository.
8. Enable independent versioning and release flow.

## Definition of Done for the Split

1. Installing multigit-lib does not install or expose the multigit shell command.
2. Installing multigit exposes the multigit shell command and pulls multigit-lib.
3. Library can be imported and used directly from external Python programs.
4. CLI works as adapter over library, with no business logic coupling back into CLI internals.

# Contributing

This guide will help you understand the overall organization of the project. It's the single source of truth for how to contribute to the code base.

---

_The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document
are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119)._

---

## Dev-Container

All tools, libraries, and prerequisites needed to _test_, _build_ and _dev_ the components MUST be added to the Dev-Container image (`.devcontainer/Dockerfile`) to provide a consistent environment for development and CI.

The container is compatible with [VS Code Remote](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) and [GitHub Codespaces Container Definitions](https://github.com/features/codespaces) to ease development.

## Test, Build, Dev, Dist, Push, and Clean

Every component MUST come with `Makefile` and define a `lint`, `test`, `build`, `dist`, `push`, `dev`and `clean` target. The Makefile is used to set up and configure how to _lint_, _test_, _build_, _dist_ (package), _dev_ (develop locally), and _push_ (publish) a component. The file MUST also `-include` the `.devcontainer/targets.mk` to add targets which will execute within the dev-container.

For ease of development, all components MUST provide a _dev_ target that defines how to run it locally, e.g docker-compose up -d or a jupyter-notebook run. If any component-dependency exists mocks MUST be provided, and be available and documented to be run side-by-side with the component. The same way, a _clean-dev_ target MUST be provided to stop/destroy the locally run component, e.g docker-compose stop && docker-compose rm -f.

The root Makefile SHALL be used to _test_, _build_, _dist_, _push_ or _clean_ all components at once and is used in CI.

All targets can be executed within the dev-container by prefixing the target with `devcontainer-` or the shorthand `+` i.e. `make +build` or `make devcontainer-build`.

⚠️ KNOWN ISSUE: `push` and `all` work only on the host system for the time being.

ℹ️ Make determines which files it needs to update, based on which source files have changed and which output files already exist. To force a re-build one should run `clean` before `build`.

## Components

All component MUST be included under the `components/` directory.

When a component is meant to run in kubernetes it MUST provide a set of kustomize manifests, under the `kustomize/` directory, to be able to deploy them in Kubernetes. When creating the kustomize manifests, components SHOULD assume that Istio, Knative and/or Kubeflow are already provisioned and the manifests need to be compatible with the versions provided.

Component dependencies like databases, queues, etc that are deployed inside Kubernetes MUST be included in the manifests. ⚠️ TODO: figure out a more concrete approach for this.

All these components will be bundled in a "super" kustomize manifest that combines each "sub" component, e.g:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ./components/kubeflow/kustomize
  - ./components/component-1/kustomize
  - ./components/component-2/kustomize
  - ./components/component-3/kustomize
# ...
```

To minimize security-vulnerabilities all components deployed in Kubernetes SHOULD be maintained to support the latest Kubernetes, Istio and/or Knative versions.

## End-to-end testing

Every new feature introduced into Katulu-FL, via the components, SHOULD include an end-to-end test, e.g A new anomaly detected in the factory sends an alert to the corresponding organization.

## Version Control

Changes SHOULD be committed frequently in small logical chunks that MUST be consistent, work independently of any later commits, and pass the linter plus the tests. Doing so eases rollback and rebase operations.

Commit message SHALL follow the guidelines stated here, as they provide a framework to write explicit messages that are easy to comprehend when looking through the project history and enable automatic changelog generation.

The Guidelines are based on
[AngularJS Git Commit Message Conventions](https://goo.gl/27wkkO).

This project uses `commitlint` to ensure that messages follow the guidelines.
Run `yarn install` in the project root to install the respective git hooks.

### Commit-Message

Each commit message MUST consist of a header (type, subject), a body
and a footer separated by empty lines:

```
<type>: <subject>

<message>

<footer>
```

Any line of the commit message MUST NOT be longer than 100 characters to ensure
that the messages are easy to read.

#### Subject

The subject contains a succinct description of the change. It SHOULD use the
imperative and present tense; “change” not “changed” nor “changes”.
The first letter SHALL NOT be capitalized, and MUST NOT end it with a dot.

#### Type

The following commit types are allowed:

- **feat** -
  use this type for commits that introduce new features or capabilities
- **fix** - use this one for bug fixes
- **docs** - use this one to indicate documentation adjustments and improvements
- **refactor** -
  use this type for adjustments to improve maintainability or performance
- **test** - use this one for commits that add missing tests
- **chore** - use this type for _maintenance_ commits e.g. removing old files
- **ci** - use this type for CI adjustments
- **style** - use this one for commits that fix formatting and linting errors

#### Message

The message SHOULD describe the motivation for the change and contrast it with previous behavior. It SHOULD use the imperative and present tense.

#### Referencing Issues

Closed issues MUST be listed on a separate line in the footer prefixed with
"Closes" keyword.

#### Breaking Changes

All breaking changes MUST be mentioned in the footer with the description of
the change, justification, and migration notes. Start the block explaining the
breaking changes with the words `BREAKING CHANGE:` followed by a space.

### Examples

```
fix: remove UI log statements

Remove console log statements to prevent IE4 errors.

Closes ACME-123, ACME-456
```

```
fix: gracefully handle HTTP connections

Gracefully handle 4xx and 5xx status codes to allow for retries when applicable.

Closes ACME-123
```

```
feat: add new Graphana data sources

Introduce a new Graphana data source

Closes ACME-123
```

```
refactor: change constant names

Adjust constant names, following the new naming conventions.

Closes ACME-123
```

```
refactor: simplify video control interface

Simplify the video player control interface as the current
interface is somewhat hard to use and caused bugs due
to accidental misuse.

BREAKING CHANGE: VideoPlayer control interface has changed
to simplify the general usage.

To migrate the code follow the example below:

Before:

VideoPlayer.prototype.stop({pause:true})

After:

VideoPlayer.prototype.pause()
```

## Releases

The release process is automated using [semantic-release](https://github.com/semantic-release/semantic-release). It uses the commit messages, which MUST follow the commit message guidelines, to determine the type of changes and automatically determines the next semantic version number. Once all tests have passed it will generate a changelog and publishes the release for pushes on `dev`, `main`.

### Example _releases_ based on commit messages

| Commit Message                               | Release Type               | Version |
| -------------------------------------------- | -------------------------- | ------- |
| `fix: gracefully handle HTTP connections`    | Patch Release              | 1.0.1   |
| `feat: add new Graphana data source`         | ~~Minor~~ Feature Release  | 1.1.1   |
| `refactor: simplify video control interface` | ~~Major~~ Breaking Release | 2.0.0   |

_Please see the Commit-Message [examples](#commit-message) for the full message._

### Release Branches

The project is configured to automatically release pushes to the `dev`, and `main` branch. The `dev` branch serves as the _main_ integration branch and should be the default base. Pushes to `dev` will result in automatic pre-releases for early testing. The `main` branch will be updated after the `dev` tests were successful and hosts the _main_ releases.

### Manual (local) Release

Run the make `env` target to create a `.env`-file with all configurations needed to build and release a new version.

```sh
make env
```

_NOTE: You need to provide a Github token with \_read_ access as an environment variable `export GITHUB_TOKEN=<ACCESS_TOKEN>`.\_

Once you've created the `.env` file export the contents to make them available.

```sh
export $(cat .env)
```

Now run make `build`, `dist`, `push` and `release`.

```sh
make build dist push release
```

_NOTE: You might want to run some of the targets in the devcontainer to provide the correct tooling._

## Upgrade Dependencies

All dependencies SHALL be updated regularly to maintain an up-to-date and secure product. Updates SHOULD consider backward compatibility and MUST document compatibility issues as documented.

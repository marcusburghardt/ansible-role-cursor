## Purpose

Install and update Cursor IDE on Linux across RPM, DEB, and AppImage formats,
with version-aware idempotency and AppImage desktop integration.

## Requirements

### Requirement: Cursor installation is opt-in through role inclusion
The role SHALL install Cursor only when it is included in a playbook, and SHALL
NOT require an internal enable flag because the role itself is the opt-in
boundary.

#### Scenario: Role invocation installs Cursor
- **WHEN** a playbook lists `ansible-role-cursor` in its roles
- **THEN** the role SHALL resolve the target version and install or update Cursor

#### Scenario: Role omission leaves the host unchanged
- **WHEN** a playbook does not list `ansible-role-cursor`
- **THEN** the host SHALL NOT be modified by this role

### Requirement: Support configurable installation method with auto-detection
The role SHALL provide `cursor_install_method` defaulting to `auto`. Auto
detection SHALL map RedHat to `rpm`, Debian to `deb`, and every other OS family
to `appimage`. Consumers SHALL be able to force `rpm`, `deb`, or `appimage`
regardless of OS family.

#### Scenario: Auto-detect RPM on RedHat family
- **WHEN** `cursor_install_method` is `auto` and the OS family is RedHat
- **THEN** the resolved method SHALL be `rpm`

#### Scenario: Auto-detect DEB on Debian family
- **WHEN** `cursor_install_method` is `auto` and the OS family is Debian
- **THEN** the resolved method SHALL be `deb`

#### Scenario: Auto-detect AppImage on unsupported OS family
- **WHEN** `cursor_install_method` is `auto` and the OS family is neither RedHat nor Debian
- **THEN** the resolved method SHALL be `appimage`

#### Scenario: Consumer overrides install method
- **WHEN** `cursor_install_method` is `appimage` on a RedHat host
- **THEN** the resolved method SHALL be `appimage`

### Requirement: Support version pinning and latest tracking
The role SHALL provide `cursor_version` defaulting to `latest`. `latest` SHALL
resolve the current release; a major.minor value SHALL resolve the newest patch
of that line. The resolved full version SHALL drive idempotency comparisons.

#### Scenario: Resolve latest version
- **WHEN** `cursor_version` is `latest`
- **THEN** the role SHALL request `<base_url>/<platform_slug>/cursor/latest` and extract the version from the redirect filename

#### Scenario: Resolve pinned version
- **WHEN** `cursor_version` is `3.0`
- **THEN** the role SHALL request `<base_url>/<platform_slug>/cursor/3.0` and extract the full version such as `3.0.16`

#### Scenario: Version extraction failure
- **WHEN** the redirect filename does not match `Cursor-<major>.<minor>.<patch>`
- **THEN** the role SHALL fail with a message naming the unexpected URL

### Requirement: Configurable download base URL
The role SHALL provide `cursor_download_base_url` so consumers can use a mirror
and tests can target a local endpoint without code changes.

#### Scenario: Mirror override
- **WHEN** `cursor_download_base_url` is set to an internal mirror
- **THEN** every version and package request SHALL use that base URL

#### Scenario: Default endpoint
- **WHEN** `cursor_download_base_url` is not set
- **THEN** the role SHALL use `https://api2.cursor.sh/updates/download/golden`

### Requirement: Idempotent installation with version comparison
The role SHALL compare the resolved target version with the installed version
and SHALL skip download and installation when they match.

#### Scenario: Skip when versions match (RPM or DEB)
- **WHEN** the resolved method is `rpm` or `deb` and the installed package version matches the target
- **THEN** the role SHALL report no changes and SHALL NOT download

#### Scenario: Skip when versions match (AppImage)
- **WHEN** the resolved method is `appimage` and the version marker matches the target
- **THEN** the role SHALL report no changes and SHALL NOT download

#### Scenario: Install when versions differ
- **WHEN** the installed version differs from the target or Cursor is absent
- **THEN** the role SHALL download and install the target version

### Requirement: Platform slug resolution from method and architecture
The role SHALL resolve a download platform slug from the resolved method and
`ansible_facts['architecture']`, supporting `x86_64` and `aarch64` for all three
methods.

#### Scenario: Resolve RPM slug
- **WHEN** the method is `rpm` and the architecture is `x86_64`
- **THEN** the platform slug SHALL be `linux-x64-rpm`

#### Scenario: Resolve DEB slug
- **WHEN** the method is `deb` and the architecture is `aarch64`
- **THEN** the platform slug SHALL be `linux-arm64-deb`

#### Scenario: Resolve AppImage slug
- **WHEN** the method is `appimage` and the architecture is `x86_64`
- **THEN** the platform slug SHALL be `linux-x64`

### Requirement: Unsupported input fails with guidance
An unsupported install method or CPU architecture SHALL stop the role with a
message listing the accepted values.

#### Scenario: Unsupported install method
- **WHEN** `cursor_install_method` is not `auto`, `rpm`, `deb`, or `appimage`
- **THEN** the role SHALL fail before any network request

#### Scenario: Unsupported architecture
- **WHEN** the architecture has no platform mapping for the resolved method
- **THEN** the role SHALL fail and list the supported architectures

### Requirement: Download Cursor package to temporary location
For RPM and DEB installs the role SHALL download the package to a temporary path
over HTTPS and SHALL remove the temporary file after installation.

#### Scenario: Temporary package cleanup
- **WHEN** an RPM or DEB package is downloaded and installed
- **THEN** the temporary file SHALL be removed after the install task completes

### Requirement: Install RPM and DEB packages via system package manager
RPM packages SHALL be installed with `ansible.builtin.dnf` and `become: true`.
DEB packages SHALL be installed with `ansible.builtin.apt` using the `deb`
parameter and `become: true`.

#### Scenario: RPM install escalates privileges
- **WHEN** the resolved method is `rpm`
- **THEN** the install task SHALL run with `become: true`

#### Scenario: DEB install escalates privileges
- **WHEN** the resolved method is `deb`
- **THEN** the install task SHALL run with `become: true`

### Requirement: Desktop entry for AppImage installations
For AppImage installs the role SHALL render `cursor.desktop` into
`cursor_desktop_dir` with an `Exec` line pointing at the AppImage binary. RPM
and DEB installs SHALL NOT deploy a desktop entry.

#### Scenario: Desktop entry created for AppImage
- **WHEN** the resolved method is `appimage`
- **THEN** `cursor.desktop` SHALL exist in `cursor_desktop_dir` and reference the AppImage path

#### Scenario: No desktop entry for RPM or DEB
- **WHEN** the resolved method is `rpm` or `deb`
- **THEN** the role SHALL NOT deploy a desktop entry

### Requirement: AppImage version marker file
For AppImage installs the role SHALL maintain `.cursor-version` in
`cursor_appimage_dir` containing only the installed version, and SHALL read it
on later runs for comparison.

#### Scenario: Marker written on install
- **WHEN** a new AppImage version is installed
- **THEN** `.cursor-version` SHALL contain the installed version string

#### Scenario: Marker read for comparison
- **WHEN** `.cursor-version` exists
- **THEN** its contents SHALL be used as the installed version

### Requirement: Platform mapping variables are internal
`vars/main.yml` SHALL define `_cursor_platform_map` and `_cursor_method_map`.
Variables internal to the role SHALL use the `_cursor_` prefix.

#### Scenario: Platform map covers every format and architecture
- **WHEN** `vars/main.yml` is loaded
- **THEN** `_cursor_platform_map` SHALL contain `rpm`, `deb`, and `appimage`, each with `x86_64` and `aarch64`

### Requirement: User-facing variables use cursor_ prefix
All user-facing variables SHALL use the `cursor_` prefix and SHALL be defined
with defaults in `defaults/main.yml`.

#### Scenario: Cursor variables have cursor_ prefix
- **WHEN** examining `defaults/main.yml`
- **THEN** every variable name SHALL start with `cursor_`

### Requirement: README documents Cursor installation
The `README.md` SHALL document the role, its variables, install methods,
examples, the AppImage desktop entry, the built-in updater caveat, and the
migration from `ansible-role-ai`.

#### Scenario: README is actionable
- **WHEN** a new consumer reads the README
- **THEN** it SHALL contain a copy-pasteable playbook and a variable reference

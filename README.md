ansible-role-cursor
===================

Installs and updates [Cursor](https://cursor.com) IDE on Linux through Ansible,
making the system package manager (or a versioned AppImage) the single source of
truth for the installed version.

This role resolves the current release through the Cursor download API and skips
download and installation when the installed version already matches. Supported
formats:

| Method | When used | Requires root? | Update source |
|--------|-----------|----------------|---------------|
| `rpm` | RedHat/Fedora (auto-detected) | Yes | System package database |
| `deb` | Debian/Ubuntu (auto-detected) | Yes | System package database |
| `appimage` | Any Linux distro / fallback | No | `.cursor-version` marker file |

Requirements
------------

None for the role itself. The target host needs `curl` or Python for Ansible's
built-in download modules, which Ansible already requires.

Role Variables
--------------

| Variable | Default | Description |
|----------|---------|-------------|
| `cursor_version` | `latest` | `latest` or a major.minor pin (e.g., `3.0`). The full version is resolved from the API. |
| `cursor_install_method` | `auto` | `auto`, `rpm`, `deb`, or `appimage` |
| `cursor_appimage_dir` | `~/.local/bin` | Directory for the AppImage binary |
| `cursor_desktop_dir` | `~/.local/share/applications` | Directory for the AppImage desktop entry |
| `cursor_download_base_url` | `https://api2.cursor.sh/updates/download/golden` | Download API base; override for mirrors or offline tests |

All variables are optional; the defaults work on any supported Linux host.

### Version pinning

`cursor_version: latest` tracks the newest release on every run. A major.minor
pin resolves the newest patch of that minor line:

```yaml
cursor_version: "3.0"    # resolves the current 3.0.x
```

The resolved full version (for example `3.0.16`) is compared against the
installed version, so the ~150 MB package is downloaded only when it changes.

### AppImage desktop integration

For `appimage` installs the role also deploys `cursor.desktop` so Cursor appears
in desktop application launchers. RPM and DEB packages already ship their own
desktop entry and are left untouched.

> **Cursor's built-in updater:** Cursor may still display update prompts even
> when the version is managed by Ansible. That is expected: for RPM/DEB installs
> the system package is authoritative and the internal updater cannot override
> it. Dismiss the prompts.

Example Playbooks
-----------------

**Minimal (auto-detect the install format):**

```yaml
---
- hosts: my_linux
  roles:
    - ansible-role-cursor
```

**Pin a version and force AppImage (no root):**

```yaml
---
- hosts: my_linux
  vars:
    cursor_version: "3.0"
    cursor_install_method: appimage
    cursor_appimage_dir: "{{ ansible_facts['user_dir'] }}/.local/bin"
  roles:
    - ansible-role-cursor
```

**Compose with other AI tooling roles:**

```yaml
---
- hosts: my_linux
  roles:
    - ansible-role-ai
    - ansible-role-cursor
```

Testing
-------

```bash
make lint              # yamllint, ansible-lint, syntax check
make test              # contract + integration tests
make test-contract     # resolution logic, no network
make test-integration  # real AppImage flow against a local fake API
make clean             # remove the integration test sandbox
```

The integration test starts `tests/fake_cursor_api.py`, a stdlib HTTP server
that mirrors the real API's redirect behavior. It requires no internet access
and no root, and the second run must report `changed=0`, proving idempotency.
RPM and DEB installs are not testable without a package manager and root; run
the role once on a disposable host to verify those branches.

Migration from ansible-role-ai 0.6.0
------------------------------------

Cursor installation moved out of `ansible-role-ai` into this role. Rename the
variables and add this role to the playbook:

| Old (`ansible-role-ai`) | New (`ansible-role-cursor`) |
|-------------------------|-----------------------------|
| `ai_cursor_version` | `cursor_version` |
| `ai_cursor_install_method` | `cursor_install_method` |
| `ai_cursor_appimage_dir` | `cursor_appimage_dir` |
| `{ enabled: true, name: 'install_cursor' }` in `ai_tasks` | `ansible-role-cursor` in `roles` |

The `ansible-role-ai` task never uninstalled Cursor, so switching roles does not
remove an existing installation.

Release Process
---------------

This role uses [release-please](https://github.com/googleapis/release-please)
with [Conventional Commits](https://www.conventionalcommits.org/).
Merging a release PR creates a tag and GitHub Release, and the same workflow
imports the role into Ansible Galaxy. The `GALAXY_API_KEY` repository secret is
required. Galaxy derives the role name `marcusburghardt.cursor` from the
repository name.

License
-------

Apache-2.0

Author Information
------------------

Marcus Burghardt
- [https://github.com/marcusburghardt](https://github.com/marcusburghardt)
- [https://www.linkedin.com/in/marcusburghardt](https://www.linkedin.com/in/marcusburghardt)

---
name: flutter-release-flow
description: Reusable standard release setup for Mike's Flutter apps. Use before creating or modifying Flutter Fastlane, mise, CocoaPods, Apple signing, TestFlight, App Store, or Play Store release automation.
---

# Flutter Release Flow

Use this skill for **any current or future Flutter app** that needs a repeatable release setup.

Known apps using this standard:

- Catty2/PurrSafe: `<path-to-purrsafe-or-existing-app>`
- Mr. Carson mobile: `<path-to-mr-carson-or-existing-app>`
- CoupleCup: `<path-to-couplecup-or-existing-app>`

For a new Flutter app, copy this standard unless there is a specific reason not to.

## Standard toolchain

Use project-local, reproducible tools. Do not rely on whichever Ruby/Fastlane/CocoaPods happens to be installed globally.

### Required files for a new Flutter releaseable app

At the Flutter app root:

```text
.mise.toml
Gemfile
Gemfile.lock
pubspec.yaml
ios/fastlane/Fastfile
ios/fastlane/Appfile
ios/fastlane/Matchfile
ios/fastlane/.env.example
ios/fastlane/.env        # local only, gitignored
```

If the project already has root-level `fastlane/` and it works, do not move it casually. For new projects, prefer `ios/fastlane/`.

### mise

Prefer `mise` for Ruby and other runtime versions.

Recommended `.mise.toml`:

```toml
[tools]
ruby = "3.3.11"
```

Use:

```bash
mise install
mise exec -- bundle install
mise exec -- bundle exec fastlane lanes
```

Do **not** manually patch `PATH` for Ruby when `mise exec` is available.

### Bundler / Fastlane / CocoaPods

Recommended app-root `Gemfile`:

```ruby
source "https://rubygems.org"

gem "fastlane", "~> 2.225"
gem "cocoapods", "~> 1.16"
```

Use Bundler commands:

```bash
mise exec -- bundle install
mise exec -- bundle exec pod --version
mise exec -- bundle exec fastlane lanes
```

For iOS pods:

```bash
cd ios
mise exec -- bundle exec pod install
```

If `Gemfile` is at app root and you run from `ios/`, use one of:

```bash
BUNDLE_GEMFILE=../Gemfile mise exec -- bundle exec fastlane lanes
BUNDLE_GEMFILE=../Gemfile mise exec -- bundle exec pod install
```

or keep a simple `ios/Gemfile` only if the project already follows that convention.

## Standard release model

All apps should follow the same release spine even when app-specific lanes exist.

1. Load App Store Connect API key from env.
2. Sync signing with `match` from the shared Apple-team branch.
3. Keep normal lanes read-only for signing assets.
4. Ensure App Store compliance metadata is present before building.
5. Bump build number from TestFlight or CI run number.
6. Build Flutter release artifacts with Ruby/Bundler env stripped.
7. Archive/export with Fastlane/Xcode signing.
8. Upload to TestFlight for `beta`.
9. Submit/upload to App Store for `release` only when explicitly requested.

## Release notes / What to Test metadata

Before any TestFlight/App Store release, update the maintained release-note file from recent commits/changelogs. Do this for **every active Fastlane project**, not just the repo currently in focus.

Discovery command:

```bash
find /Users/mikewong/workspace -path '*/fastlane/Fastfile' \
  -not -path '*/.claude/worktrees/*' \
  -not -path '*/node_modules/*' \
  -print | sort
```

Current active projects and metadata conventions:

- PurrSafe/Catty2: `/Users/mikewong/workspace/catty2/purrsafe_flutter/fastlane/metadata/whats_new.txt` is the TestFlight changelog used by `ios beta`; also keep `fastlane/metadata/en-US/release_notes.txt` aligned for App Store metadata.
- CoupleCup: `/Users/mikewong/workspace/CoupleCup/app/couple_cup/ios/fastlane/metadata/en-US/release_notes.txt`; `ios beta` should read this file for `upload_to_testflight(changelog:)`.
- Mr. Carson mobile: `/Users/mikewong/workspace/mr-carson/apps/mobile/ios/fastlane/metadata/en-US/release_notes.txt`; `ios beta` should read this file for `upload_to_testflight(changelog:)`.

Metadata workflow:

1. Inspect branch/status and recent commits: `git status --short --branch` and `git log --oneline --decorate -30`.
2. Prefer changes since the last release/build bump when obvious; otherwise summarize the most recent user-facing feature/fix commits.
3. Write tester-facing bullets: features first, then fixes/reliability, then a short `Please test:` checklist for TestFlight.
4. Ensure the relevant beta lane passes the file content into `upload_to_testflight(changelog: File.read(...).strip)` instead of hardcoded text like `"Latest build"`.
5. Keep release notes free of internal-only details, secrets, private URLs, and excessive implementation jargon unless testers need it.
6. Verify with `ruby -c <fastlane/Fastfile>` and inspect `git diff` before reporting.

## Standard env names

Use these names across all apps. Legacy names can exist as fallbacks only.

```env
APP_IDENTIFIER=<bundle id>
APP_NAME=<display/app-store name>
APP_SKU=<sku>
APPLE_TEAM_ID=<apple team id>
TEAM_ID=<apple team id>
ITC_TEAM_ID=
APPLE_ID=
ASC_KEY_ID=
ASC_ISSUER_ID=
ASC_KEY_FILEPATH=
ASC_KEY_CONTENT=
MATCH_GIT_URL=<match git url>
MATCH_GIT_BRANCH=apple-team-<team id>
MATCH_TYPE=appstore
MATCH_READONLY=true
MATCH_PASSWORD=***
```

Never commit real `.env`, `.p8`, certificates, profiles, provisioning profiles, or secret output.

## Signing policy

- Distribution certificate is Apple-team/account-level.
- Provisioning profiles are app/bundle-ID-level.
- Shared match branch: `apple-team-<team id>`.
- Normal `beta`, `build`, and `release` lanes use `readonly: true`.
- Local lanes must not create, switch, unlock, delete, reset, or pass explicit keychain settings. Never call `setup_ci`, `create_keychain`, `unlock_keychain`, `delete_keychain`, or `match(..., keychain_name:/keychain_password:)` for local dev. Temporary keychain setup is only allowed in explicitly CI-only paths guarded by `ENV["CI"] == "true"`.
- One-time `certificates` / `create_profile` lanes may use `readonly: false` only to create missing app profiles.
- Do not revoke, nuke, rotate, or regenerate team distribution certificates without explicit approval.

## App Store compliance metadata

For iOS apps that only use standard HTTPS/TLS encryption and do not use non-exempt/custom cryptography, set this in `ios/Runner/Info.plist` **before building**:

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

This prevents future TestFlight/App Store builds from showing **Missing Compliance** for export compliance. It only affects builds created after the key is present; already-uploaded builds may still need compliance answered manually in App Store Connect or a new build uploaded.

When adding this for a project, verify with:

```bash
/usr/libexec/PlistBuddy -c 'Print :ITSAppUsesNonExemptEncryption' ios/Runner/Info.plist
```

Only set it to `false` when the app does not use non-exempt encryption. If the app has custom crypto, VPN, secure messaging, proprietary encryption, or regulated crypto features, stop and get the correct compliance answer instead of assuming exemption.

## Standard Fastlane files

Canonical templates are provided in this skill directory:

- `templates/.mise.toml`
- `templates/Gemfile`
- `templates/Appfile`
- `templates/Matchfile`
- `templates/Fastfile`
- `templates/.env.example`

For new projects, copy these templates first and replace placeholders (`<bundle id>`, `<app name>`, `<sku>`). Then adapt only app-specific dart-defines, metadata, IAP, Sentry, or dependency workarounds.

### Appfile

```ruby
app_identifier(ENV["APP_IDENTIFIER"] || "<bundle id>")
team_id(ENV["APPLE_TEAM_ID"] || ENV["TEAM_ID"] || "<apple team id>")
apple_id(ENV["APPLE_ID"])
itc_team_id(ENV["ITC_TEAM_ID"])
```

### Matchfile

```ruby
git_url(ENV["MATCH_GIT_URL"] || "<match git url>")
git_branch(ENV["MATCH_GIT_BRANCH"] || "apple-team-<team id>")
storage_mode("git")
type(ENV["MATCH_TYPE"] || "appstore")
app_identifier(ENV["APP_IDENTIFIER"] || "<bundle id>")
team_id(ENV["APPLE_TEAM_ID"] || ENV["TEAM_ID"] || "<apple team id>")
readonly(ENV["MATCH_READONLY"].nil? ? true : ENV["MATCH_READONLY"] == "true")
```

## Fastfile standard helpers

Prefer this helper shape in each app, adapted only for app-specific defaults:

```ruby
def app_identifier
  ENV["APP_IDENTIFIER"] || "<bundle id>"
end

def apple_team_id
  ENV["APPLE_TEAM_ID"] || ENV["TEAM_ID"] || "<apple team id>"
end

def asc_api_key
  opts = {
    key_id: ENV.fetch("ASC_KEY_ID"),
    issuer_id: ENV.fetch("ASC_ISSUER_ID"),
    in_house: false
  }
  if ENV["ASC_KEY_FILEPATH"].to_s.strip != ""
    opts[:key_filepath] = ENV["ASC_KEY_FILEPATH"]
  else
    opts[:key_content] = Base64.decode64(ENV.fetch("ASC_KEY_CONTENT"))
  end
  app_store_connect_api_key(**opts)
end

def clean_flutter_subprocess_env!
  %w[GEM_HOME GEM_PATH BUNDLE_GEMFILE BUNDLE_BIN_PATH RUBYOPT RUBYLIB].each { |k| ENV.delete(k) }
  ENV["PATH"] = "/opt/homebrew/bin:#{ENV['PATH']}" unless ENV["PATH"].to_s.include?("/opt/homebrew/bin")
end

def match_profile_name
  mapping = Actions.lane_context[SharedValues::MATCH_PROVISIONING_PROFILE_MAPPING] || {}
  mapping[app_identifier] || "match AppStore #{app_identifier}"
end

def ensure_ios_export_compliance_metadata!
  plist = "Runner/Info.plist"
  value = `/usr/libexec/PlistBuddy -c 'Print :ITSAppUsesNonExemptEncryption' #{plist} 2>/dev/null`.strip
  return if value == "false"

  sh("/usr/libexec/PlistBuddy -c 'Add :ITSAppUsesNonExemptEncryption bool false' #{plist} 2>/dev/null || /usr/libexec/PlistBuddy -c 'Set :ITSAppUsesNonExemptEncryption false' #{plist}")
  UI.message("Set ITSAppUsesNonExemptEncryption=false for standard HTTPS/TLS export compliance")
end

def install_signing_assets(api_key, readonly: true)
  # Local dev must not touch keychains: do not create, switch, unlock, delete,
  # reset, or pass explicit keychain settings. Temporary keychain setup belongs
  # only in CI=true-only lanes, never in local beta/build/release lanes.
  # App Store Connect API-key auth avoids Apple ID/2FA, but macOS codesigning
  # still requires the distribution private key to be available through the
  # existing macOS signing environment.
  match(type: "appstore", readonly: readonly, api_key: api_key, app_identifier: app_identifier)
end
```

If an existing app uses `load_asc_api_key`, either keep it as an alias or make it equivalent.

## Standard iOS beta lane spine

The lane body can differ for app-specific needs, but the order should remain. Use `install_signing_assets(api_key)` for local project lanes. Local dev must never create, switch, unlock, delete, reset, or pass explicit keychain settings; temporary keychains are only acceptable in explicitly CI-only paths guarded by `ENV["CI"] == "true"`.

```ruby
lane :beta do
  api_key = asc_api_key
  install_signing_assets(api_key)

  update_code_signing_settings(
    use_automatic_signing: false,
    path: "Runner.xcodeproj",
    team_id: apple_team_id,
    code_sign_identity: "Apple Distribution",
    profile_name: "match AppStore #{app_identifier}",
    targets: ["Runner"]
  )

  begin
    latest = latest_testflight_build_number(api_key: api_key, app_identifier: app_identifier)
    increment_build_number(xcodeproj: "Runner.xcodeproj", build_number: latest + 1)
  rescue => e
    UI.important("Could not read TestFlight build number (#{e.message}); falling back to local increment.")
    increment_build_number(xcodeproj: "Runner.xcodeproj")
  end

  ensure_ios_export_compliance_metadata!
  sh("cd ../.. && env -u GEM_HOME -u GEM_PATH -u BUNDLE_GEMFILE -u BUNDLE_BIN_PATH -u RUBYOPT flutter build ios --release --no-codesign")

  clean_flutter_subprocess_env!
  ipa_path = build_app(
    workspace: "Runner.xcworkspace",
    scheme: "Runner",
    export_method: "app-store",
    export_options: {
      provisioningProfiles: {
        app_identifier => "match AppStore #{app_identifier}"
      }
    }
  )

  upload_to_testflight(
    api_key: api_key,
    ipa: ipa_path,
    skip_waiting_for_build_processing: true
  )
end
```

Use `skip_waiting_for_build_processing: false` only when a later step truly needs processed build state or external tester distribution.

## Standard Android lane spine

For Android, prefer AAB and Play internal track:

```ruby
platform :android do
  desc "Build and upload to Play Store internal track"
  lane :beta do
    sh("cd .. && flutter build appbundle --release")
    upload_to_play_store(
      track: "internal",
      aab: "../build/app/outputs/bundle/release/app-release.aab",
      skip_upload_screenshots: true,
      skip_upload_images: true
    )
  end
end
```

Keep Android signing secrets in Gradle/CI secret stores, not in tracked Fastlane files.

## App-specific exceptions to preserve

- PurrSafe has App Store metadata/IAP/Sentry/managed-profile logic. Do not delete those lanes.
- CoupleCup has an `objective_c.framework` min-iOS patch in its archive/export flow. Preserve it until the dependency issue is fixed.
- Mr. Carson currently has the cleanest reference implementation for the base iOS TestFlight flow.

## New-project setup checklist

1. Add `.mise.toml` with Ruby.
2. Add `Gemfile` with Fastlane and CocoaPods.
3. Run `mise install && mise exec -- bundle install`.
4. Add `ios/fastlane/Appfile`, `Matchfile`, `Fastfile`, `.env.example`.
5. Add `.gitignore` rules for:
   - `ios/fastlane/.env`
   - `*.p8`
   - `*.mobileprovision`
   - `*.cer`
   - `*.p12`
6. Verify `git check-ignore -v ios/fastlane/.env`.
7. Run `mise exec -- bundle exec fastlane lanes` from the chosen Fastlane working directory.
8. Do not run Apple-side write lanes until the app record/bundle ID/profile creation is intentionally requested.

## Verification checklist

Before saying release automation is ready:

```bash
ruby -c <app fastlane Fastfile>
git -C <repo> check-ignore -v <path-to-fastlane/.env> || true
git -C <repo> diff -- <fastlane files>
cd <fastlane working dir> && mise exec -- bundle exec fastlane lanes
```

If the repo does not use mise yet, add it rather than falling back to system Ruby for a new project.

Do not run `beta`, `release`, `create_profile`, or `certificates` unless the user explicitly asks for Apple-side side effects.

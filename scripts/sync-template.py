#!/usr/bin/env python3
"""Keeps translations/template.xml in sync with the latest released app build.

Pulls strings.xml from the tag of the newest non-prerelease GitHub release, so the
template on the site never contains keys that no shipped build has. Canary builds are
published as prereleases and are ignored on purpose.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

REPO = "savo-o/resona"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "translations", "template.xml")
CATALOG_PATH = os.path.join(ROOT, "translations", "catalog.json")

STRINGS_PATH = "app/src/main/res/values/strings.xml"
GRADLE_PATH = "app/build.gradle.kts"
VERSION_NAME_RE = re.compile(r'versionName\s*=\s*"([^"]+)"')


def fetch(url, accept=None):
    request = urllib.request.Request(url)
    request.add_header("User-Agent", "resona-template-sync")
    if accept:
        request.add_header("Accept", accept)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def latest_release_tag():
    try:
        payload = fetch(
            f"https://api.github.com/repos/{REPO}/releases/latest",
            accept="application/vnd.github+json",
        )
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise
    return json.loads(payload).get("tag_name")


def raw(tag, path):
    return fetch(f"https://raw.githubusercontent.com/{REPO}/{tag}/{path}")


def counts(xml_bytes):
    root = ET.fromstring(xml_bytes)
    return len(root.findall("string")), len(root.findall("string-array"))


def main():
    tag = latest_release_tag()
    if not tag:
        print("no published release yet, nothing to sync")
        return 0

    strings_xml = raw(tag, STRINGS_PATH)
    string_count, array_count = counts(strings_xml)

    version = tag.lstrip("v")
    try:
        match = VERSION_NAME_RE.search(raw(tag, GRADLE_PATH).decode("utf-8"))
        if match:
            version = match.group(1)
    except urllib.error.HTTPError:
        pass

    changed = []

    current = open(TEMPLATE_PATH, "rb").read() if os.path.exists(TEMPLATE_PATH) else None
    if current != strings_xml:
        with open(TEMPLATE_PATH, "wb") as handle:
            handle.write(strings_xml)
        changed.append(f"template.xml ({string_count} strings, {array_count} arrays)")

    with open(CATALOG_PATH, encoding="utf-8") as handle:
        catalog = json.load(handle)

    template_entry = catalog.setdefault("template", {})
    wanted = {
        "file": "template.xml",
        "appVersion": version,
        "strings": string_count,
        "arrays": array_count,
    }
    if {k: template_entry.get(k) for k in wanted} != wanted:
        template_entry.update(wanted)
        with open(CATALOG_PATH, "w", encoding="utf-8") as handle:
            json.dump(catalog, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        changed.append(f"catalog.json (appVersion {version})")

    if changed:
        print("updated: " + ", ".join(changed))
    else:
        print(f"already up to date with {tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

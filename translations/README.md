# Resona translations

Community translations for [Resona](https://github.com/savo-o/resona), published at
<https://savo-o.github.io/resona-status/translations/>.

A translation is a single `strings.xml` file. The app loads it at runtime, so you do not
need to build anything or wait for a release.

## Making one

1. In the app: **Settings → Language → Custom → Save template**. That template always matches
   the version you have installed, which is why it is the preferred starting point.
   `template.xml` in this folder is the same file for app version 1.5.
2. Translate the text **between** the tags. Leave everything else alone:
   - do not rename or remove `name="..."` attributes, unknown names are skipped;
   - keep placeholders exactly as they are (`%s`, `%d`, `%1$s`, `%2$d`), including their order
     where the string is positional;
   - escape apostrophes as `\'`;
   - `<string-array>` blocks are the home screen greetings, translate every `<item>`.
3. Load it back through **Settings → Language → Custom → Load translation**.

Anything you leave out falls back to the built-in language, so a partial translation is fine.

## Contributing

Open a pull request adding:

- `<id>.xml` with your file;
- an entry in `catalog.json`.

Keep `id` short and lowercase (`ja`, `de`, `pt-br`). Set `appVersion` to the app version your
template came from, so people can see when a translation is behind.

## Checklist before opening a PR

- the file is valid XML (a mismatched tag rejects the whole file, the app will refuse to load it)
- no duplicate `name` attributes
- no leftover text in the language you translated from

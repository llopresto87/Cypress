# freemarker — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Apache FreeMarker is a general-purpose Java template engine: a template (FTL)
merged with a data model produces text, whether HTML pages, email bodies,
configuration files or source code. Coordinates: `org.freemarker:freemarker`
(a few releases of the 2.3 line were published with an `-incubating` version
suffix); the Spring Boot BOM manages its version. Spring applications add it
with `org.springframework.boot:spring-boot-starter-freemarker`; on the Boot 4
line the auto-configuration is the `spring-boot-freemarker` module, and
`org.springframework.boot:spring-boot-starter-freemarker-test` exists.
FreeMarker has one live line, 2.3; behaviour changes inside it are gated by the
`incompatible_improvements` setting rather than by a major version. Upstream
home: https://freemarker.apache.org, with the Manual at
https://freemarker.apache.org/docs/.

## Install, setup and configuration
- **One `Configuration`.** Create one `freemarker.template.Configuration` at
  startup (`new Configuration(Configuration.VERSION_2_3_xx)`), set the template
  loader, default encoding and exception handler there, and use it as an
  application-wide singleton. Re-creating it is expensive (the template cache
  is lost). After setup it must not be modified in a multi-threaded
  application; it is then effectively immutable and safe to share.
- **`incompatible_improvements`** defaults to 2.3.0 (maximum backward
  compatibility), which the Manual calls usually a bad idea. New projects set
  it to the fixed version in use when they start, and raise it deliberately
  after checking what each increase turns on. Never use a dynamic value such
  as `Configuration.getVersion()`, since an upgrade could then change
  behaviour; a value above the running library fails.
- **Auto-escaping by file extension.** With
  `recognize_standard_file_extensions` true, a template named `.ftlh` gets the
  HTML output format and `.ftlx` the XML format, both auto-escaping. It
  defaults to true only when `incompatible_improvements` is 2.3.24 or higher.
  Plain `.ftl` does not auto-escape unless the template sets an output format
  (`<#ftl output_format="HTML">`). `template_configurations` maps other name
  patterns to formats, and `auto_escaping_policy` can turn escaping off or
  force it.
- **Spring Boot versus plain Spring.** Boot's auto-configuration always sets
  `recognize_standard_file_extensions=true` (user settings can override it).
  Plain Spring Framework's `FreeMarkerConfigurationFactory` builds the
  `Configuration` with `DEFAULT_INCOMPATIBLE_IMPROVEMENTS` and does not set it,
  so outside Boot the `.ftlh` extension alone does not escape: set the setting,
  or set the output format in the template. That factory also prefers
  file-system access by default, where Boot's property defaults to false.
- **Exception handler.** `template_exception_handler` defaults to
  `DEBUG_HANDLER`, which prints a stack trace with FTL details into the output
  and rethrows; the Manual warns against it in production and recommends
  `RETHROW_HANDLER`. Its quick-start configuration also sets
  `log_template_exceptions=false` (no double logging) and
  `wrap_unchecked_exceptions=true`.
- **Template updates** are checked after a 5-second delay by default;
  class-loader based loaders may not see changes at all.
- **Boot properties and defaults:** `spring.freemarker.template-loader-path`
  `classpath:/templates/`, `suffix` `.ftlh`, `prefix` empty, `charset` UTF-8,
  `content-type` `text/html`, `check-template-location` true,
  `prefer-file-system-access` false, `cache` false (the MVC view cache only),
  `expose-request-attributes`/`expose-session-attributes` and the
  `allow-*-override` flags false, `expose-spring-macro-helpers` true;
  `spring.freemarker.settings.*` passes FreeMarker settings through.

## Core API / usage shape
- `cfg.getTemplate(name)` returns a cached, parsed `Template`;
  `template.process(dataModel, writer)` renders it. The data model is usually a
  `Map`, or beans wrapped by the configured `ObjectWrapper` (default
  `DefaultObjectWrapper`).
- Spring MVC: `FreeMarkerConfigurer` plus `registry.freeMarker()` (or Boot's
  auto-configuration) resolve view names to templates. For non-web text such as
  email, use the `Configuration` bean directly; no view layer is needed.
- **Missing values:** referring to a variable or hash entry that does not exist
  is an error that aborts processing (unless configured otherwise). Java `null`
  counts as missing, since FTL has no null; handle optional values with
  `name!default` or `name??`.

## Idioms & best practices
- Keep templates as resource files separate from Java code, and drive them
  from a data model passed at render time.
- Name HTML and email templates `.ftlh` (XML `.ftlx`), or declare the output
  format, so interpolations are escaped by default; use `?no_esc` only for
  values known to be safe markup.
- Pin `incompatible_improvements` to a constant and raise it on purpose.
- Configure the template loader once at startup. Observed in practice: calling
  `setClassForTemplateLoading` (or any setter) per render mutates the shared
  singleton, which the Manual forbids after setup.
- Render with `RETHROW_HANDLER` and let the caller decide. Observed in practice:
  a caught-and-logged `TemplateException` silently drops the output, so the
  email is never sent and nobody notices.

## General pitfalls
- **Plain `.ftl` does not auto-escape,** so interpolated user values land
  unescaped in HTML unless the template sets an output format.
- **Outside Boot `.ftlh` is not special** (plain Spring factory, or a hand-built
  `Configuration` left at the default `incompatible_improvements`).
- **Errors appear only at render time:** a missing or misspelled variable
  aborts processing, and templates are not checked against the model at build
  time.
- **Cross-service contracts.** Observed in practice: when the template name and
  model keys travel on a message from another service, nothing ties the
  producer's keys to the template's references, so a key rename is a
  cross-service change and per-template render tests are the only guard.
- **Boot upgrades from before the 2.2 line:** the default view suffix changed
  from `.ftl` to `.ftlh`, so existing `.ftl` views are not found until renamed.
- **`DEBUG_HANDLER` in production** prints technical details into the rendered
  output.

## Testing
- One render test per template, with a representative model, through the same
  `Configuration` the application uses, asserting on the output: it is the only
  check that model and template agree.
- In HTML templates, test that a user-supplied value containing `<` comes out
  escaped; it catches a `.ftl` name or a missing output format.
- Boot 4 ships `spring-boot-starter-freemarker-test`; its content was not
  checked for this page.

## Security defaults
- Templates are code. The FAQ says not to let users upload templates unless
  they are developers, administrators or other highly trusted people.
- If less trusted people can edit templates: restrict the object wrapper
  (`SimpleObjectWrapper`, or `DefaultObjectWrapper` with a
  `WhitelistMemberAccessPolicy`) and never rely on the built-in "unsafe method"
  blacklist; keep `?api` off (`api_builtin_enabled` defaults to false);
  restrict `?new` with `new_builtin_class_resolver` set to
  `TemplateClassResolver.ALLOWS_NOTHING_RESOLVER` (the FAQ says
  `SAFER_RESOLVER` is not restrictive enough); set `DOMNodeSupport=false` on
  the default wrapper; use a template loader that refuses paths outside the
  template root. FreeMarker cannot limit CPU or memory, so a template can loop
  forever.
- Observed in practice: the data model often carries secrets (activation codes,
  reset links, addresses), so log template names, never parameters. Upstream
  is silent on logging the model.
- Boot's view defaults keep request and session attributes out of the model.

## Operational behaviour
- Parsed templates are cached in the `Configuration` and re-checked for changes
  after the update delay.
- `Configuration` methods that do not change settings are thread-safe; treat
  shared `Template` instances and data models as read-only.

## Interop
- Spring Boot (auto-configuration, `spring.freemarker.*`, the `.ftlh` suffix,
  the BOM) and Spring Framework (`FreeMarkerConfigurer`,
  `FreeMarkerConfigurationFactory`, the Spring macro library through
  `expose-spring-macro-helpers`); Boot also auto-configures resource URL
  rewriting for FreeMarker views.
- Email: render the body, then send it with
  [`jakarta-mail.md`](./jakarta-mail.md).

## Major lines
### FreeMarker 2.3, `incompatible_improvements` 2.3.24 and higher
- Output formats, auto-escaping and `.ftlh`/`.ftlx` recognition; below that
  value only the deprecated `#escape` directive exists.

### Boot 2 (from its 2.2 release)
- The default view suffix changes from `.ftl` to `.ftlh`, which Boot's notes
  describe as aligning with safe defaults; earlier Boot lines resolve `.ftl`.

### Spring Boot 4
- FreeMarker auto-configuration is its own module (`spring-boot-freemarker`,
  package `org.springframework.boot.freemarker.autoconfigure`); properties and
  defaults are unchanged.

## Upstream docs
- https://freemarker.apache.org/docs/
- https://freemarker.apache.org/docs/dgui_misc_autoescaping.html
- https://freemarker.apache.org/docs/pgui_config_incompatible_improvements.html
- https://freemarker.apache.org/docs/app_faq.html
- https://docs.spring.io/spring-boot/appendix/application-properties/index.html

# thymeleaf — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Thymeleaf is a server-side Java template engine built around natural
templates: an HTML template stays a valid page a browser can open as a static
prototype, and the `th:*` attributes replace its mock content when the engine
processes it. It renders six template modes: HTML and XML (markup), TEXT,
JAVASCRIPT and CSS (textual), and RAW (no processing). In a Spring MVC or
WebFlux application it is the view layer, with Spring EL as its expression
language. Upstream home: https://www.thymeleaf.org, source at
https://github.com/thymeleaf/thymeleaf (one repository for the core, the
Spring and Spring Security integrations, the testing libraries and the
examples, from the 3.1 line).

- `org.thymeleaf:thymeleaf`: the core engine and the Standard Dialect
  (OGNL as the expression language when no Spring integration is present).
- `org.thymeleaf:thymeleaf-spring6`: the Spring Framework 6 integration
  (`SpringTemplateEngine`, `SpringResourceTemplateResolver`,
  `ThymeleafViewResolver`, the SpringStandard Dialect); needed for Spring 6 and
  later applications. Requires JDK 17.
- `org.thymeleaf:thymeleaf-spring5`: the same integration for Spring Framework
  5; needed only on the Spring 5 line.
- `org.thymeleaf.extras:thymeleaf-extras-springsecurity6`: the `sec:` dialect
  and the `#authentication` and `#authorization` expression objects for Spring
  Security 6; needed only when templates show or hide content by the signed-in
  user's authorities. `thymeleaf-extras-springsecurity5` is its Spring
  Security 5 counterpart.
- `org.springframework.boot:spring-boot-starter-thymeleaf`: the Boot starter,
  which auto-configures the engine, resolver and view resolver; needed in a
  Boot application. From Boot 4 the auto-configuration lives in its own module,
  `org.springframework.boot:spring-boot-thymeleaf`, which the starter pulls in.

Neighbour engine on this corpus: [`freemarker.md`](./freemarker.md).

## Install, setup and configuration
- **Boot:** add the starter; the BOM manages the Thymeleaf version, and adding
  `thymeleaf-extras-springsecurity6` beside the Thymeleaf and Security starters
  is enough for Boot to register the `sec:` dialect.
- **Boot keys (`spring.thymeleaf.*`), with their defaults:** `prefix`
  `classpath:/templates/`, `suffix` `.html`, `mode` `HTML`, `encoding` UTF-8,
  `cache` true, `check-template` true (checks the template exists before
  rendering), `check-template-location` true, `enable-spring-el-compiler`
  false, `servlet.content-type` `text/html`,
  `servlet.produce-partial-output-while-processing` true (writes output as
  soon as possible instead of buffering until the template finishes),
  `render-hidden-markers-before-checkboxes` false, `view-names` and
  `excluded-view-names` (patterns), `template-resolver-order` (set only when
  other template resolver beans exist), and for WebFlux
  `reactive.max-chunk-size` (0B; setting it switches templates to CHUNKED mode)
  with `reactive.chunked-mode-view-names` and `reactive.full-mode-view-names`.
- **Without Boot:** declare a `SpringResourceTemplateResolver` (prefix, suffix,
  template mode, cacheable), a `SpringTemplateEngine` on it (it applies the
  SpringStandard Dialect and Spring's `MessageSource` resolution), and a
  `ThymeleafViewResolver` on the engine. Plain Java uses `TemplateEngine` with a
  template resolver and a `Context`, or with a web context built from the
  3.1 line's web-API abstraction (Major lines).
- **Template cache:** parsed templates are cached by default (the cache manager
  holds 200 by default); `setCacheable(false)` on the resolver or the Boot
  `cache` key turns it off for development. Entries can be evicted with
  `clearTemplateCache()` and `clearTemplateCacheFor(name)`.
- **SpringEL compiler:** off by default because it can break expressions that
  are reused across different data types; turning it on speeds most templates.

## Core API / usage shape
- **Expressions:** `${...}` variables (OGNL, or SpEL under Spring), `*{...}`
  selection on the object set by `th:object`, `#{...}` messages, `@{...}` link
  URLs (context path prepended; parameters in parentheses), `~{...}` fragments.
  Literals, `+` concatenation, `|...|` literal substitution, arithmetic,
  comparators, `cond ? a : b`, the Elvis default `a ?: b`, and the no-operation
  token `_` that leaves the prototype content in place.
- **Text:** `th:text` escapes; `th:utext` writes unescaped markup. Inlining
  `[[...]]` escapes and `[(...)]` does not.
- **Attributes:** specific processors (`th:href`, `th:src`, `th:value`,
  `th:action`, `th:class`, ...), `th:attr` for several at once,
  `th:attrappend`/`th:classappend`, fixed-value boolean attributes
  (`th:checked`, `th:disabled`, `th:selected`, ...: set when true, absent when
  false), and the default attribute processor: any `th:<name>` (for example
  `th:aria-label`, `th:data-id`) renders `<name>`.
- **Control:** `th:each="item, stat : ${items}"` (with the status variable's
  index, count, odd, first, last), `th:if`/`th:unless`, `th:switch`/`th:case`,
  `th:with` for local variables, `th:block` as a tag that disappears.
- **Layout:** `th:fragment` (optionally with parameters), `th:insert` (the whole
  fragment, its host tag included, inside the host) and `th:replace` (the
  fragment instead of the host), `th:remove` with `all`, `body`, `tag`,
  `all-but-first` or `none`.
- **Spring MVC:** `th:object="${command}"` on the form (a model-attribute name
  only, no property navigation, no nested `th:object` inside the form),
  `th:field="*{prop}"` binds an input to a command property and applies the
  conversion service, `th:errors`/`th:errorclass`/`#fields` show binding
  errors, `${{...}}` and `*{{...}}` format through the conversion service, and
  `${@bean.method()}` reaches application-context beans. A controller can return
  a fragment as the view name: `"page :: fragment"` or `"page :: #id"`.
- **Web namespaces:** `${param.x}` (a `String[]` of request-parameter values),
  `${session.x}` (session attribute), `${application.x}` (servlet-context
  attribute); request attributes are plain context variables (`${x}`).
- **Spring Security extras:** `sec:authorize="hasRole('ADMIN')"` (the same as
  `th:if` on an authorization expression), `sec:authorize-url`,
  `sec:authentication="name"`, `${#authentication}`, `${#authorization}`.

## Idioms & best practices
- Default to `th:text`. Use `th:utext` only for markup the application itself
  produced or sanitised; it is also evaluated in restricted mode (Security
  defaults).
- Put what a template needs from the request, the session or the servlet
  context into the model in the controller (`model.addAttribute`,
  `@ModelAttribute`, `@ControllerAdvice`), which is upstream's recommended
  replacement for the expression objects the 3.1 line removed.
- Use `th:insert` or `th:replace` with the `~{template :: fragment}` envelope;
  the bare `template :: fragment` form is deprecated on the 3.1 line, and so
  is `th:include` (its replacement is `th:insert` plus `th:remove="tag"` on the
  fragment, or a `th:block` fragment).
- Make an element's removal conditional with an expression:
  `th:remove="${cond} ? tag : none"`. `th:remove` treats null as `none`, so
  `th:remove="${cond} ? tag"` does the same. Removing with `tag` keeps the
  children, so a link can degrade to its plain text.
- Leave an optional attribute out by giving its `th:` form a null value (an
  `aria-current` that should exist only on the active item, say); see the
  pitfall on empty strings below.
- Return HTML fragments for partial-page updates straight from controller
  methods with the `"view :: fragment"` view name, so a fragment and its full
  page share one template.
- **Records and accessor methods.** Under the Spring integration, SpEL's
  reflective property accessor falls back, after `getX()` and `isX()`, to a
  plain accessor method named like the property, so a record component reads
  as `${r.name}` and as `${r.name()}`; the Spring Framework source carries this
  on its 5.3, 6 and 7 lines. Any public method of a model object can be called
  (`${page.isSignedIn()}`), as long as its class is not in one of the
  restricted JDK or Jakarta packages. Observed in practice: a team called the
  accessor explicitly (`${r.name()}`) in every template, so a reader never
  wonders whether a getter exists.

## General pitfalls
- **The 3.1 line removed `#request`, `#response`, `#session` and
  `#servletContext` from expressions.** Templates written for 3.0 fail at
  runtime; move the data into the model. The web namespaces `${param}`,
  `${session}` and `${application}` are still documented in the 3.1 tutorial,
  and `${#ctx.exchange}` exposes Thymeleaf's own exchange abstraction, not a
  servlet object.
- **Classes in core packages are restricted from 3.1.** Method and
  constructor calls and static references on classes in `java.*`, `javax.*`,
  `jakarta.*`, `jdk.*`, `com.sun.*`, `sun.*`, `org.w3c.dom.*`, `org.xml.sax.*`,
  `org.ietf.jgss.*` and `org.omg.*` are forbidden, except an allow-list of basic
  `java.lang`/`java.math` types, the common collection types, `Optional`,
  `Stream`, `Locale`, `Date` and `Calendar`. Wrap any other JDK object in an
  application class if a template truly needs it.
- **Restricted mode surprises.** In the restricted contexts (Security defaults)
  `${param.*}`, `new`, static access (`T(...)`), `@bean` references and
  `#execInfo` raise a template processing exception. Because the default
  attribute processor always runs restricted, `th:aria-label="${param.q[0]}"`
  fails where `th:text="${param.q[0]}"` works. An upgrade that starts raising
  restriction errors is upstream's signal to move the computation into the
  controller.
- **An empty string removes a generic attribute too.** The default attribute
  processor drops the attribute when the expression yields null *or* an empty
  string (and removes the prototype's static attribute of the same name), so
  `th:data-x="''"` cannot render `data-x=""`. Observed in practice and
  confirmed by the processor's source.
- **A CSRF field appears only through `th:action`.** Spring Security's CSRF
  support adds the hidden `_csrf` input to a form through Spring's
  `RequestDataValueProcessor`, which Thymeleaf calls from `th:action` on a
  `<form>` with an unsafe method such as POST. A form with a plain `action=`
  attribute gets no token and is rejected (Spring Security's docs list
  Thymeleaf among the view technologies that include the token automatically).
  Observed in practice: a POST sign-out form with `th:action` carried the field
  and the same form with a literal `action` did not.
- **`th:field` always escapes;** there is no switch to turn it off, unlike the
  JSP form tags' `htmlEscape`.
- **`th:object` on a form takes only a model-attribute name** (`${command}`,
  never `${command.part}`), and its name must match the controller's model
  attribute (by default the uncapitalised class name).
- **Partial output on error.** With `produce-partial-output-while-processing`
  on (Boot's default), part of the page can already be written when an
  expression fails later in the template; set it to false to buffer the whole
  render.

## Testing
- `MockMvc` renders Thymeleaf views to the response body (unlike JSP, which
  needs a forward), so a controller test can assert on real HTML: parse the
  body with an HTML parser and check the elements and attributes a template is
  responsible for. Observed in practice: a suite that renders every template
  this way, through the servlet MVC context, asserted that optional attributes
  are absent, that POST forms carry the CSRF field and that conditional
  removals keep the right text.
- Upstream keeps its own testing libraries in the main repository (under
  `lib/testing`) for template-level tests outside a Spring context.

## Security defaults
- `th:text`, `th:value`, `th:field` and `[[...]]` inlining escape by default;
  `th:utext` and `[(...)]` do not.
- **Restricted expression evaluation mode** applies to: preprocessing
  (`__...__`), unescaped output (`th:utext`, unescaped inlining), `th:on*`
  event-handler attributes (which also accept only numeric or boolean values),
  `th:attr` creating attributes with arbitrary names, the default attribute
  processor, template and fragment names and fragment parameters, the base
  part of URL expressions (`@{...}`, `th:href`, `th:src`; URL parameters are not
  restricted), and every output expression in TEXT mode. It is a security
  feature, not a setting, and cannot be turned off.
- Upstream states the restrictions are defence in depth, not a substitute for
  validating input: an expression outside those contexts runs unrestricted,
  and the engine cannot tell whether a context value came from a user.
  Never build template names, fragment selectors or preprocessed expressions
  from request data, and never pass user input to `th:utext`.
- Spring Security's CSRF token reaches forms only through `th:action` (General
  pitfalls).
- RAW template mode inserts external content without executing any Thymeleaf
  code it contains.

## Operational behaviour
- The template cache makes the first render of each template the expensive
  one (read and parse); later renders clone the cached event sequence. Turning
  the cache off for development costs a parse on every request.
- WebFlux streams templates in CHUNKED mode when `reactive.max-chunk-size` is
  set; the `chunked-mode-view-names` and `full-mode-view-names` lists narrow
  or exempt views.
- Rendering failures, restriction violations among them, surface at runtime
  as a template processing exception, not at startup: only rendering a
  template proves it.

## Interop
- Spring Framework MVC and WebFlux (view resolution, `MessageSource`,
  conversion service, `RequestDataValueProcessor`), Spring Boot
  (auto-configuration, `spring.thymeleaf.*`), Spring Security (CSRF field, the
  extras dialect).
- HTML partial-update libraries that request fragments over HTTP pair with the
  `"view :: fragment"` controller return.
- An HTML parser is the natural assertion tool for rendered output in tests.
- [`freemarker.md`](./freemarker.md): the other server-side template engine
  on this corpus.

## Major lines
### 3.0
- The line before 3.1: `javax.*` Servlet API only, Spring integrations up to
  `thymeleaf-spring5` and `thymeleaf-extras-springsecurity5`, and the web
  expression objects `#request`, `#session`, `#servletContext` and `#response`
  available to expressions.

### 3.1
- Adds `jakarta.*` Servlet API support (keeping `javax.*`), the
  `thymeleaf-spring6` and `thymeleaf-extras-springsecurity6` modules (JDK 17),
  an abstraction over the web API (`org.thymeleaf.web`: application,
  exchange, request and session interfaces, built with
  `JakartaServletWebApplication.buildApplication(servletContext)` and its
  `buildExchange(request, response)`; Spring applications never see it). Drops Spring
  and Spring Security support older than 5. JDK 8 is the general minimum.
- `#temporals` (`java.time`) moves into the core, so the
  `thymeleaf-extras-java8time` module is no longer needed. `th:each` iterates
  a `java.util.stream.Stream` directly.
- Removes the web expression objects and restricts core-package classes
  (General pitfalls); deprecates `th:include` and unwrapped fragment
  expressions; removes `th:substituteby` and `${execInfo}`.
- Spring Boot 3 and later configure 3.1 through the starter with no change;
  outside Boot, replace the `-spring5` and `-springsecurity5` artifacts with
  their `6` forms.

## Upstream docs
- Tutorial, Using Thymeleaf (3.1): https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html
- Tutorial, Thymeleaf + Spring (3.1): https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html
- What's new in 3.1 and migration: https://www.thymeleaf.org/doc/articles/thymeleaf31whatsnew.html
  (source: https://github.com/thymeleaf/thymeleaf-docs/blob/master/docs/articles/thymeleaf31whatsnew.md)
- Spring Security extras: https://github.com/thymeleaf/thymeleaf/tree/3.1-master/lib/thymeleaf-extras-springsecurity6
- Spring Boot properties (`spring.thymeleaf.*`): https://docs.spring.io/spring-boot/appendix/application-properties/index.html
- Spring Security CSRF in HTML forms: https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html
- MockMvc and view rendering: https://docs.spring.io/spring-framework/reference/testing/mockmvc/vs-end-to-end-integration-tests.html
- Source: https://github.com/thymeleaf/thymeleaf

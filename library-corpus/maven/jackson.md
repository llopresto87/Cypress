# jackson — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
FasterXML Jackson is the standard JSON library of the JVM: a streaming parser
and generator (`jackson-core`), data binding between JSON and Java objects
(`jackson-databind`, with `ObjectMapper` / `JsonMapper`), the annotations
(`jackson-annotations`), and datatype and format modules. It is Spring Boot's
default JSON engine, so it usually arrives through the Boot JSON starter rather
than by direct declaration. Two generations coexist under different
coordinates:

- Jackson 2: `com.fasterxml.jackson.core:jackson-databind`,
  `com.fasterxml.jackson.core:jackson-core`,
  `com.fasterxml.jackson.datatype:jackson-datatype-jsr310`, Java packages
  `com.fasterxml.jackson.*`;
- Jackson 3: `tools.jackson.core:jackson-databind`,
  `tools.jackson.core:jackson-core`, Java packages `tools.jackson.*`;
- both generations use `com.fasterxml.jackson.core:jackson-annotations`
  (package `com.fasterxml.jackson.annotation`, kept on the 2 line).

Home: https://github.com/FasterXML/jackson. Support: upstream names LTS lines
in both generations (each with about a two-year window); within Jackson 3 the
first release line is transitional and not LTS. The project README lists the
current LTS lines.

## Install, setup and configuration
- In a Boot application, let the Boot BOM manage the whole family and add no
  versions of your own. The Boot JSON starter already brings the `java.time`
  support on the 2 line, so a separate `jackson-datatype-jsr310` declaration is
  redundant (observed in practice).
- **Boot's mapper.** Customize the Spring-managed mapper with
  `spring.jackson.*` properties (feature switches such as
  `spring.jackson.serialization.<feature>`,
  `spring.jackson.default-property-inclusion`) or with builder customizer beans
  (`JsonMapperBuilderCustomizer` for Jackson 3,
  `Jackson2ObjectMapperBuilderCustomizer` for Jackson 2), which can be ordered
  around Boot's own (order 0). Beans of type `JacksonModule` are registered
  automatically, and `ServiceLoader` modules are found unless
  `spring.jackson.find-and-add-modules=false`.
- **Replacing the mapper** (a `JsonMapper` or `JsonMapper.Builder` bean)
  disables all of Boot's mapper auto-configuration; mark a replacement
  `@Primary`. Prefer customizers.
- Standalone: build one mapper, configure it once, and share it. On the 2 line
  `ObjectMapper` is configured with `enable` / `disable` / `configure` before
  first use; on the 3 line mappers are immutable and built with
  `JsonMapper.builder()`.

## Core API / usage shape
- `mapper.readValue(source, Type.class)` and `mapper.writeValueAsString(value)`
  bind JSON to and from objects; a `TypeReference` carries generic types that
  erasure would lose (`new TypeReference<Map<String, Item>>() {}`).
- The tree model: `mapper.readTree(json)` returns a `JsonNode`
  (`ObjectNode`, `ArrayNode`) for JSON whose shape is not fixed.
- Annotations shape the binding: `@JsonProperty`, `@JsonIgnore`,
  `@JsonInclude`, `@JsonFormat`, `@JsonCreator` (constructor or factory
  binding, which suits immutable types), `@JsonPropertyOrder`, `@JsonTypeInfo`
  for polymorphic types.
- Feature enums switch behaviour: `SerializationFeature`,
  `DeserializationFeature`, `MapperFeature`, and on the 3 line
  `DateTimeFeature` for date and time handling.

## Idioms & best practices
- **One mapper, three wire paths** (observed in practice). In a Spring
  application, the mapper Spring MVC uses also backs Feign's default
  `SpringEncoder` / `SpringDecoder`, so a service's Jackson choice governs both
  its HTTP responses and every call it makes through Feign. A library that
  embeds its own Jackson (a JWT library's Jackson module, say) and any
  hand-built `new ObjectMapper()` are separate and follow none of Spring's
  settings. On late 2 releases such a bare mapper registers no modules
  either, so it fails on `java.time` and `Optional` values (earlier releases
  write them as plain beans, a wrong shape with no error) until it calls
  `findAndRegisterModules()` (or registers the modules by hand). Code that
  serializes only to observe (an audit or logging aspect) must catch its own
  failure, or a value it cannot render fails the business call it watches.
- Spring Data `Page` and `Sort` over Feign need the OpenFeign Jackson modules
  (`PageJacksonModule`, `SortJacksonModule`); their serialized shape depends on
  the mapper generation (observed in practice). See
  [`spring-cloud-openfeign`](./spring-cloud-openfeign.md).
- Prefer annotations on DTOs to mapper-wide settings when only some types need
  the behaviour; annotations survive a generation change (the annotation package
  does not move).

## General pitfalls
- **Core and databind skew.** An explicit `jackson-core` or `jackson-databind`
  pin that diverges from the BOM produces core/databind version skew and keeps
  old databind lines alive. Let the BOM manage the family (observed in
  practice).
- **Raw-string assertions.** Compare **parsed** JSON in tests, not strings,
  unless byte order is the contract: property order and date rendering change
  with mapper defaults, and the 3 line changes both.
- **`@Jacksonized` and two generations.** Lombok's `@Jacksonized` must be told
  which generation's annotations to generate once both may be in play; see
  [`lombok`](./lombok.md).
- **A field initializer is not a default under a creator.** When Jackson binds
  a DTO through a constructor (an `@JsonCreator`, or the all-args constructor it
  picks for a getter-only type), a property missing from the JSON is passed as
  the type's null value (`FAIL_ON_MISSING_CREATOR_PROPERTIES` is off by
  default), and the constructor overwrites the initializer. So
  `Boolean flag = Boolean.FALSE` ends up `null`, and unboxing it throws later.
  A no-args constructor does not help a type with no setters. Use a primitive,
  or apply the default inside the constructor.
- **Unchecked on 3.** All Jackson 3 exceptions are `RuntimeException`s, so code
  that relied on the compiler to force handling of `IOException` loses that
  prompt.

## Testing
- Freeze serialization: a test per wire type that serializes a fixed object and
  compares the parsed result with a committed fixture. It is the only test that
  notices a mapper default or a customizer silently stop applying (observed in
  practice, where an inert customizer passed every existing test).
- Spring Boot's `@JsonTest` slice auto-configures the application's JSON mapper
  for focused serialization tests.

## Security defaults
- **Polymorphic deserialization.** Upstream's criteria for a security problem
  are: content from untrusted senders, *and* "default typing" turned on (or
  `@JsonTypeInfo` with base type `java.lang.Object`), *and* "gadget" classes on
  the class path. Later 2 releases replaced the old block list with a validator
  (`PolymorphicTypeValidator`). Keep default typing off; when polymorphism is needed,
  use `@JsonTypeInfo` on a specific base type and a restrictive validator
  (`BasicPolymorphicTypeValidator.builder()`).
- `FAIL_ON_TRAILING_TOKENS` is on by default in Jackson 3; upstream recommends
  keeping it on for security and correctness.
- Report vulnerabilities through the coordinated-disclosure process the
  project README describes.

## Operational behaviour
- Jackson 3 defaults to a deque-based buffer `RecyclerPool`, which can add
  overhead in some cases compared with the 2 line's thread-local pool, and its
  trailing-token check adds a small cost per read. Upstream documents both and
  how to switch them; measure before changing.
- No measured numbers are recorded here.

## Interop
- [`spring-boot`](./spring-boot.md) and
  [`spring-framework`](./spring-framework.md): Boot 4 and Framework 7 default to
  Jackson 3 and deprecate Jackson 2 support.
- [`spring-cloud-openfeign`](./spring-cloud-openfeign.md): Feign codecs share
  the Spring mapper.
- [`lombok`](./lombok.md): builders and `@Jacksonized`; the 3 line's property
  naming affects Lombok-style accessors.
- [`jjwt`](./jjwt.md): its Jackson module carries its own Jackson.

## Major lines
### Jackson 2
`com.fasterxml.jackson.*`, Java 8 baseline. `java.time`, `Optional` and
parameter-name support are separate modules to register. Mutable
`ObjectMapper` with setters.

### Jackson 3
- **Coordinates and packages** move to `tools.jackson.*`;
  `jackson-annotations` stays on `com.fasterxml.jackson.annotation`, so
  `@JsonInclude`, `@JsonIgnore`, `@JsonFormat` and `@JsonProperty` survive
  unchanged. Databind annotations such as `@JsonSerialize` and
  `@JsonDeserialize` do move.
- Java 17 baseline. Everything deprecated on the last 2 line before the split
  is removed. The parameter-names, JDK 8 and `java.time` modules are built into
  databind.
- **Immutable mappers** built with `JsonMapper.builder()`; format mappers are
  mandatory (`new YAMLMapper()`, not `new ObjectMapper(new YAMLFactory())`).
  Mapper-wide setters go: `setSerializationInclusion(...)` becomes
  `JsonMapper.builder().changeDefaultPropertyInclusion(...)`.
- Renames: `JsonMappingException` → `DatabindException`,
  `SerializerProvider` → `SerializationContext`, `TextNode` → `StringNode`;
  date features move into `DateTimeFeature`.
- **Changed defaults, each able to change a payload silently:**
  `WRITE_DATES_AS_TIMESTAMPS` off (ISO-8601 strings);
  `FAIL_ON_UNKNOWN_PROPERTIES` off (lenient, which can mask contract drift);
  `FAIL_ON_TRAILING_TOKENS` on; `FAIL_ON_NULL_FOR_PRIMITIVES` on (can break
  `@JsonCreator` with missing primitives); `SORT_PROPERTIES_ALPHABETICALLY` on
  (the most likely to break raw-string tests); `DEFAULT_VIEW_INCLUSION` off
  (matters for `@JsonView`); `FIX_FIELD_NAME_UPPER_CASE_PREFIX` on, and
  standard bean naming always. Observed in practice: an all-caps accessor such
  as `getOTP()` serializes as `OTP` where the 2 line gave `otp`.
- **Spring Boot 4.** Both generations can sit on the class path, and Jackson 3
  is the default HTTP mapper. `spring.jackson.use-jackson2-defaults=true` makes
  the Jackson 3 mapper follow Boot's former Jackson 2 defaults as closely as it
  can. Keeping Jackson 2 for HTTP needs `spring-boot-jackson2` plus
  `spring.http.converters.preferred-json-mapper=jackson2` (servlet) or
  `spring.http.codecs.preferred-json-mapper` (reactive); that support is
  deprecated for removal in a later Boot 4 release.
- **The inert customizer** (observed in practice, at run time). Under the
  Jackson 3 default, a Jackson 2 `Jackson2ObjectMapperBuilderCustomizer`
  compiles and every existing test passes, yet it applies to nothing; only the
  output changes. A frozen-fixture test is what catches it.
- **A partial pin is worse than none** (observed in practice). Keep every
  service in a cross-service call on the same generation, since the mapper also
  drives the Feign encoder: one side on 3 and the other on 2 disagree on
  property names, and the receiver answers 400 "Invalid request content",
  which looks like a validation failure.

## Upstream docs
- https://github.com/FasterXML/jackson
- https://github.com/FasterXML/jackson-databind
- https://github.com/FasterXML/jackson-databind/wiki/Deserialization-Features
- https://github.com/FasterXML/jackson/blob/main/jackson3/MIGRATING_TO_JACKSON_3.md
- https://github.com/FasterXML/jackson/wiki/Jackson-Polymorphic-Deserialization-CVE-Criteria
- The Spring blog post "Introducing Jackson 3 support in Spring" (https://spring.io/blog)
- https://docs.spring.io/spring-boot/reference/features/json.html
- https://docs.spring.io/spring-boot/how-to/spring-mvc.html (customizing the mapper)

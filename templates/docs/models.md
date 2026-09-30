<!-- Placed once by install.sh when missing; the plant owns it from then on.
     An unfilled row means "inherit the caller's model", so the graft audit
     discloses an unfilled map and passes it (graft.gate.scaffolds). -->

# Model map

This page names the model this plant runs for each model class and effort,
on each host that can choose one. It is the one home of that choice
(`delegation.model-map`): nodes, protocols and briefs name the class and the
effort, and read the model here. Agents run only the models this page lists.

An agent's `model:` field holds one of four aliases, and each reads one row
below: `opus` the authoring row of the agent's effort, `sonnet` the
investigation row of its effort, `haiku` the investigation-low row whatever its
effort, and `inherit` no row, so the agent runs on its caller's model. Claude
Code reads the alias itself and picks the version, so it has no column here.

## Providers

The providers this plant runs, one per line: `<provider>`.

## Map

Write each selector as the host's catalog prints it: on Prime Agent, the
`.selector` that `rlm.find_models("<name>")` returns; on opencode, the
`provider/model` string. A `-` cell, or a row still holding its placeholder,
means "inherit the caller's model": the spawn omits the model and its routing
evidence records `model: inherited (map row unfilled)`. A filled selector that
does not resolve stops the spawn, which reports it.

| Class | Effort | Prime Agent | opencode |
|---|---|---|---|
| authoring | high | `<provider/model-id>` | `<provider/model-id>` |
| authoring | medium | `<provider/model-id>` | `<provider/model-id>` |
| authoring | low | `<provider/model-id>` | `<provider/model-id>` |
| investigation | medium | `<provider/model-id>` | `<provider/model-id>` |
| investigation | low | `<provider/model-id>` | `<provider/model-id>` |

High-effort steps run in the authoring class, so the map has no
investigation-high row.

## When a model changes

Edit the row, then re-run `install.sh opencode` so the opencode agents pick it
up. Prime Agent reads this page on each spawn.

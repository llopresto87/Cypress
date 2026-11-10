#!/usr/bin/env bash
# Fixture: a shell test. worth-check.py reads Python and TypeScript or
# JavaScript only, so it lists this file as not checked (shell).
grep -q "Send" web/submit.html

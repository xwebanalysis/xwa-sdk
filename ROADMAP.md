# XWA SDK Development Roadmap

This document tracks the strategic steps required to evolve the XWA SDK into the shared data and contract layer of the XWA ecosystem.
This file is formatted to be synced automatically with GitHub Issues using the `xgh` roadmap standard.

## Core Schemas <!-- phase:schemas -->

- [x] Define base result and finding schemas
- [x] Define scan and target descriptors
- [x] Define task and progress event schemas
- [x] Define error handling and status envelope

## API Contracts <!-- phase:contracts -->

- [ ] Define inter-module REST contract conventions
- [x] Define WebSocket streaming contracts for live analysis
- [x] Define import/export interchange formats (JSON)
- [x] Document versioning and compatibility policy

## Language Bindings <!-- phase:bindings -->

- [x] Generate Python package for FastAPI backends
- [ ] Generate Rust crate for Axum backends
- [x] Generate TypeScript types for Angular frontends
- [x] Add JSON Schema validation utilities

## Publishing & Adoption <!-- phase:publishing -->

- [ ] Set up package publishing pipeline (PyPI, crates.io, npm)
- [x] Create consumer examples for each language binding
- [ ] Write migration guide for existing modules
- [ ] Integrate xwa-sdk into samurai as first consumer

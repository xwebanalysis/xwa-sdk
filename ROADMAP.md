# XWA SDK Development Roadmap

This document tracks the strategic steps required to evolve the XWA SDK into the shared data and contract layer of the XWA ecosystem.
This file is formatted to be synced automatically with GitHub Issues using the `xgh` roadmap standard.

## Core Schemas <!-- phase:schemas -->

- [ ] Define base result and finding schemas
- [ ] Define scan and target descriptors
- [ ] Define task and progress event schemas
- [ ] Define error handling and status envelope

## API Contracts <!-- phase:contracts -->

- [ ] Define inter-module REST contract conventions
- [ ] Define WebSocket streaming contracts for live analysis
- [ ] Define import/export interchange formats (JSON)
- [ ] Document versioning and compatibility policy

## Language Bindings <!-- phase:bindings -->

- [ ] Generate Python package for FastAPI backends
- [ ] Generate Rust crate for Axum backends
- [ ] Generate TypeScript types for Angular frontends
- [ ] Add JSON Schema validation utilities

## Publishing & Adoption <!-- phase:publishing -->

- [ ] Set up package publishing pipeline (PyPI, crates.io, npm)
- [ ] Create consumer examples for each language binding
- [ ] Write migration guide for existing modules
- [ ] Integrate xwa-sdk into samurai as first consumer

# Hokm Platform – Kanban Epic & Phase Planning

This document maps the full project lifecycle into **epics**, **phases**, and actionable **user stories/tasks**, aligned with the implementation roadmap from the specification.

---

## Phase 1: MVP Core (Months 1–3)

### Epic: Real-Time Game Engine
- [ ] Design and implement Hokm game state machine (12 phases)
- [ ] Implement full Hokm rules (trick-taking, trump, scoring, Hakim)
- [ ] Build deterministic shuffle with ChaCha20 + seed audit log
- [ ] Create action validation system (turn, legality, timing, rate limits)
- [ ] Implement reconnect logic with state snapshot + event replay

### Epic: WebTransport Infrastructure
- [ ] Set up Rust game server with `quinn`/`quiche`
- [ ] Implement reliable/unreliable WebTransport channels
- [ ] Build session management (JWT handshake, Redis TTL)
- [ ] Add liveness probes and graceful shutdown
- [ ] Implement 0-RTT resumption support

### Epic: Basic Matchmaking
- [ ] Redis queue with ZSET (score = ELO)
- [ ] Matchmaker service with constraint relaxation
- [ ] Room Actor system (actor per game, in-memory)
- [ ] Party support (2–4 players, team assignment)
- [ ] Fill empty slots with placeholder AI bots

### Epic: Rule-Based AI
- [ ] Implement fallback AI with heuristics:
  - Follow suit
  - Play high-value cards
  - Preserve trumps
- [ ] Integrate into game loop with timeout guard (< 20ms)
- [ ] Add difficulty toggle (only "beginner" at MVP)

### Epic: User & Auth System
- [ ] JWT auth with refresh tokens (Argon2id hashing)
- [ ] PostgreSQL `users` table + CRUD APIs
- [ ] Basic profile (username, ELO, stats)
- [ ] Email verification flow

### Epic: Observability Baseline
- [ ] Structured JSON logging (INFO+)
- [ ] Prometheus metrics (latency, active games, errors)
- [ ] Grafana dashboard: Real-time ops + game health
- [ ] Basic alerts (error rate, latency spikes)

---

## Phase 2: Beta Launch (Month 4)

### Epic: Reinforcement Learning AI
- [ ] Build custom Hokm RL environment (partial observability)
- [ ] Implement observation space (331-dim)
- [ ] Train PPO agent via Ray RLlib (self-play → league)
- [ ] Export model to ONNX
- [ ] Integrate `tract` ONNX runtime in Rust server
- [ ] Add inference latency monitoring + fallback trigger

### Epic: Anti-Cheat System
- [ ] Behavioral analysis engine (timing, win rate, patterns)
- [ ] Immutable event log with HMAC chaining
- [ ] Report system + manual review queue
- [ ] Connection/IP fingerprinting + ban system

### Epic: Replay & Audit
- [ ] Record all `game_events` to PostgreSQL
- [ ] Compress + upload replays to S3
- [ ] Build replay viewer (client-side reconstruction)
- [ ] Admin tool: seed reveal + shuffle verification

### Epic: Load & Chaos Testing
- [ ] Simulate 5,000 concurrent users with K6/Locust
- [ ] Validate p95 latency < 100ms
- [ ] Run chaos experiments (pod kill, DB latency)
- [ ] Tune HPA based on `active_games` metric

---

## Phase 3: Full Launch (Month 5)

### Epic: Polished UX & Onboarding
- [ ] Tutorial mode for new players
- [ ] Matchmaking queue UI with wait time estimate
- [ ] Game results screen + ELO change
- [ ] Mobile-responsive web client

### Epic: Production Hardening
- [ ] Multi-zone Kubernetes deployment
- [ ] Zero-downtime rolling updates
- [ ] DR plan: RTO < 1h, RPO < 5m
- [ ] Security audit + penetration test

### Epic: Launch Readiness
- [ ] Final performance tuning
- [ ] Marketing landing page
- [ ] Support team training + runbooks
- [ ] Go/no-go checklist sign-off

---

## Phase 4: Growth (Months 6–12)

### Epic: Social Features
- [ ] Friends system + invites
- [ ] In-game chat (team + global)
- [ ] Spectator mode
- [ ] Replay sharing

### Epic: Competitive Play
- [ ] Ranked queue (separate ELO)
- [ ] Seasonal ranks + rewards
- [ ] Global + regional leaderboards
- [ ] Tournament engine (brackets, prizes)

### Epic: Advanced AI
- [ ] Multiple difficulty levels (intermediate, expert)
- [ ] AI hint system (optional suggestions)
- [ ] Retrain model monthly with production data

### Epic: Native Mobile Apps
- [ ] iOS app (Swift + WebTransport)
- [ ] Android app (Kotlin + WebTransport)
- [ ] Push notifications (turn reminder, invites)
- [ ] Cross-platform sync

### Epic: Monetization (If Applicable)
- [ ] Cosmetic store (card backs, avatars)
- [ ] Premium tier (ad-free, stats)
- [ ] Ethical design review (no P2W)

---

## Ongoing: Platform Maintenance

### Epic: Reliability & SRE
- [ ] Weekly incident reviews
- [ ] Quarterly chaos engineering
- [ ] Auto-scaling tuning
- [ ] Cost optimization (spot instances, S3 lifecycle)

### Epic: Community & Content
- [ ] Strategy guides + video tutorials
- [ ] Player councils + feedback loops
- [ ] Monthly feature voting
- [ ] Bug bounty program

---

> **Kanban Board Organization Suggestion**:
> - Columns: `Backlog` → `Ready` → `In Progress` → `Review` → `Done`
> - Labels: `backend`, `ai`, `frontend`, `infra`, `security`, `ux`
> - Prioritization: MVP stories must be completed before beta epics

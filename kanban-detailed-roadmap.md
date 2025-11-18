# Hokm Platform – Detailed Kanban Roadmap

This document provides a comprehensive, phase-by-phase breakdown of the Hokm platform development lifecycle. It is structured as:

- **Phase** → High-level milestone (e.g., MVP)
- **Epic** → Major feature area (e.g., Game Engine)
- **User Story** → User-centric capability
- **Tasks** → Technical implementation steps
- **Acceptance Criteria** → Definition of Done
- **Priority** → P0 (Critical), P1 (High), P2 (Medium)

All items are traceable to the system specification (`hokm-complete-prompt.md`).

---

## Phase 1: MVP Core (Months 1–3)  
*Goal: Functional real-time gameplay with rule enforcement, basic matchmaking, and reconnect.*

---

### Epic: Game State Machine & Rules Engine  
*Implement deterministic game logic and state transitions.*

#### User Story: As a player, I want the game to follow official Hokm rules so that matches are fair and consistent.  
**Tasks**:
1. Define enum for all card suits and ranks (Spades, Hearts, etc.)
2. Implement `Deck` struct with shuffle method using ChaCha20 PRNG
3. Create `GameState` struct with fields: current_phase, trump_suit, leader, trick_cards, scores, hands
4. Implement state machine with 12 phases (Lobby → Return to Lobby)
5. Enforce turn order: only current player can act
6. Implement trick-taking logic: suit-following, trump evaluation, winner determination
7. Implement scoring: 1 point for 7+ tricks, 2 points for "Kot" (all 13 tricks)
8. Write unit tests for edge cases (tie-breaking, empty hands, etc.)

**Acceptance Criteria**:
- ✅ All 13 cards dealt correctly (5 + 8)
- ✅ Hakim determined by highest initial card
- ✅ Trump declared only by Hakim within 30s
- ✅ Trick won by highest trump or led suit
- ✅ Game ends when team reaches 7+ tricks
- ✅ Score updates correctly
- ✅ Unit test coverage ≥ 90% (spec 10.1)

**Priority**: P0  
**Ref**: Spec 3.1, 3.2

---

#### User Story: As a developer, I want deterministic shuffling so that games can be audited and replayed.  
**Tasks**:
1. Generate 256-bit CSPRNG seed at game start
2. Store encrypted seed in PostgreSQL (`matches.shuffle_seed_hash`)
3. Compute and publish SHA-256 hash to clients
4. Implement Fisher-Yates shuffle using seeded ChaCha20
5. Log first 5 cards dealt to each player
6. Build CLI tool to verify shuffle from seed

**Acceptance Criteria**:
- ✅ Same seed → same deck order
- ✅ Seed not exposed to clients
- ✅ Hash published in GameStart message
- ✅ Audit log includes seed_hash and player cards
- ✅ Verification tool works

**Priority**: P0  
**Ref**: Spec 3.3

---

### Epic: WebTransport Real-Time Engine  
*Low-latency bidirectional communication between clients and server.*

#### User Story: As a player, I want sub-100ms latency so that gameplay feels instant.  
**Tasks**:
1. Set up Rust project with `quinn` or `quiche` for WebTransport over QUIC
2. Implement handshake: client sends JWT, server validates session
3. Create connection handler per player (async task)
4. Route messages to Room Actor via reliable/unreliable streams
5. Implement heartbeat (unreliable datagram every 5s)
6. Add 0-RTT resumption support for reconnect
7. Benchmark p95 latency under load

**Acceptance Criteria**:
- ✅ WebTransport connection established < 100ms
- ✅ Action round-trip latency < 60ms (p95)
- ✅ Heartbeat maintains connection
- ✅ Reconnect uses 0-RTT if possible
- ✅ Load test: 10k connections per instance

**Priority**: P0  
**Ref**: Spec 2.3, 2.4

---

### Epic: Matchmaking System  
*Queue players by skill and region, form balanced teams.*

#### User Story: As a player, I want to find a fair match quickly so I don’t wait long.  
**Tasks**:
1. Design Redis schema: `ZSET matchmaking_queue:{region}` (score = ELO)
2. Implement API endpoint: `/queue/join`
3. Write matchmaker service (polls every 100ms)
4. Apply constraints: ±200 ELO, latency < 80ms, party rules
5. Use Redlock to atomically claim 4 players
6. Relax constraints after 30/60/90s
7. Fill missing slots with AI bots

**Acceptance Criteria**:
- ✅ Player added to queue with timestamp
- ✅ Match found within 30s for average skill
- ✅ Teams balanced (ELO diff < 100)
- ✅ Party members stay together
- ✅ AI fills incomplete matches
- ✅ No double-matching (atomic lock)

**Priority**: P0  
**Ref**: Spec 5.2

---

### Epic: Rule-Based AI Fallback  
*Provide non-cheating bot players when humans are unavailable.*

#### User Story: As a player, I want to play immediately even if no humans are available.  
**Tasks**:
1. Define `AIBot` trait with `choose_action(&state)` method
2. Implement heuristic strategies:
   - Follow suit if possible
   - Play highest card unless trump
   - Preserve trumps unless winning trick
3. Integrate into game loop: call on AI turn
4. Set timeout guard: fall back to random play if >20ms
5. Add difficulty toggle (beginner only for now)

**Acceptance Criteria**:
- ✅ AI plays legal moves only
- ✅ Inference time < 20ms (p95)
- ✅ Falls back gracefully on error
- ✅ Can complete full game without stalling
- ✅ Beginner mode avoids aggressive trump use

**Priority**: P0  
**Ref**: Spec 4.1, 1.1

---

### Epic: Authentication & Session Management  
*Securely identify users and maintain sessions across disconnects.*

#### User Story: As a user, I want secure login so my account is protected.  
**Tasks**:
1. Implement `/auth/register`, `/auth/login`, `/auth/refresh`
2. Hash passwords with Argon2id
3. Generate JWT access token (15min expiry)
4. Store refresh token in DB (HTTP-only cookie)
5. Rotate refresh tokens on use
6. Validate JWT on WebTransport handshake

**Acceptance Criteria**:
- ✅ Passwords securely hashed
- ✅ Tokens properly signed (HS256)
- ✅ Refresh token rotation enforced
- ✅ XSS protection via HTTP-only cookies
- ✅ Failed logins rate-limited

**Priority**: P0  
**Ref**: Spec 7.1

---

### Epic: Reconnection & State Recovery  
*Allow players to rejoin after network issues without losing progress.*

#### User Story: As a player, I want to rejoin my game if I lose connection.  
**Tasks**:
1. On disconnect, keep session alive in Redis for 60s
2. Client attempts reconnect with exponential backoff (1s, 2s, 4s…)
3. Server sends full state snapshot + event log since disconnect
4. Client reconciles state and resumes
5. After 60s, replace with AI bot

**Acceptance Criteria**:
- ✅ Reconnect succeeds within 60s
- ✅ Full game state restored
- ✅ Event log allows reconciliation
- ✅ AI takes over after grace period
- ✅ No state desync

**Priority**: P0  
**Ref**: Spec 2.4, 1.1

---

## Phase 2: Beta Launch (Month 4)  
*Goal: Introduce RL-trained AI, anti-cheat, replays, and performance hardening.*

---

### Epic: Reinforcement Learning AI Agent  
*Train and deploy an AI capable of intermediate-level play.*

#### User Story: As a new player, I want to play against competent AI to learn strategy.  
**Tasks**:
1. Build custom Hokm environment in Python (PyTorch)
2. Define observation space (331-dim: hand, history, trump, score)
3. Implement action mask for legal moves
4. Design reward function: +0.1 per trick, +0.5 per win, cooperation bonus
5. Train PPO agent via self-play (Ray RLlib, 50k+ games)
6. Export model to ONNX format
7. Integrate `tract` ONNX runtime into Rust game server
8. Load model at startup, run inference off main thread

**Acceptance Criteria**:
- ✅ Model trains successfully (win rate >70% vs rule-based)
- ✅ ONNX export works
- ✅ Inference < 20ms (p95)
- ✅ Fallback to rule-based on failure
- ✅ AI plays strategically (not just random)

**Priority**: P1  
**Ref**: Spec 4.2–4.6

---

### Epic: Anti-Cheat & Integrity System  
*Detect and prevent cheating through behavioral analysis and audit logs.*

#### User Story: As a fair player, I want cheaters banned so the game remains competitive.  
**Tasks**:
1. Append every action to immutable event log (HMAC-signed)
2. Chain events: each includes hash of previous
3. Track player timing, win rate, pattern consistency
4. Flag suspicious behavior (sub-100ms actions, impossible win rates)
5. Build admin UI: view replays, event logs, stats
6. Implement report system → manual review queue
7. Add ban system: temp/permanent, hardware bans

**Acceptance Criteria**:
- ✅ Tamper-proof event chain
- ✅ Suspicious patterns detected
- ✅ Admin tools allow investigation
- ✅ Reports trigger review
- ✅ Bans enforceable

**Priority**: P1  
**Ref**: Spec 7.3

---

### Epic: Replay & Audit System  
*Record and store full game history for review and sharing.*

#### User Story: As a player, I want to watch replays of my games to improve.  
**Tasks**:
1. Persist all `game_events` to PostgreSQL (`game_events` table)
2. Compress and upload to S3 after game end
3. Path: `replays/YYYY/MM/DD/{match_id}.json.gz`
4. Build web-based replay viewer (client-side reconstruction)
5. Add "Watch Replay" button in match history

**Acceptance Criteria**:
- ✅ All events logged in order
- ✅ Replays reconstruct perfectly
- ✅ Available in UI within 5 minutes
- ✅ S3 retention: 90 days casual, 1 year ranked

**Priority**: P1  
**Ref**: Spec 6.1, 6.3

---

### Epic: Performance & Load Testing  
*Validate scalability and resilience under realistic load.*

#### User Story: As an operator, I want confidence the system won’t crash at launch.  
**Tasks**:
1. Simulate 5,000 concurrent users with K6/Locust
2. Measure p95 latency (< 100ms)
3. Run chaos experiments: kill pods, inject DB latency
4. Tune HPA based on `active_games` metric
5. Verify auto-scaling response < 2 minutes

**Acceptance Criteria**:
- ✅ p95 latency < 100ms under load
- ✅ Error rate < 0.1%
- ✅ Auto-scaling activates correctly
- ✅ Games survive pod failures
- ✅ No memory leaks

**Priority**: P0  
**Ref**: Spec 10.5, 14.1

---

## Phase 3: Full Launch (Month 5)  
*Goal: Polished UX, production hardening, and public release.*

---

### Epic: UI/UX Polish & Onboarding  
*Deliver a smooth, intuitive experience for new and returning players.*

#### User Story: As a new player, I want a tutorial so I can learn Hokm quickly.  
**Tasks**:
1. Design onboarding flow (signup → tutorial → first game)
2. Implement interactive tutorial (step-by-step guidance)
3. Add tooltips and help icons
4. Optimize matchmaking UI: show estimated wait time
5. Build results screen with ELO change animation
6. Make web client mobile-responsive

**Acceptance Criteria**:
- ✅ Tutorial explains rules clearly
- ✅ First game completed in < 5 minutes
- ✅ Mobile layout works on small screens
- ✅ Users rate UX ≥ 4/5 in survey

**Priority**: P1  
**Ref**: Spec 14.2

---

### Epic: Production Hardening  
*Ensure high availability, security, and disaster recovery.*

#### User Story: As an SRE, I want zero downtime during deployments.  
**Tasks**:
1. Configure Kubernetes rolling updates (maxUnavailable=0)
2. Set up multi-AZ cluster (3 zones)
3. Enable PostgreSQL streaming replication + PgBouncer
4. Implement DR plan: RTO < 1h, RPO < 5m
5. Conduct security audit + penetration test
6. Finalize runbooks and on-call procedures

**Acceptance Criteria**:
- ✅ Zero-downtime deploys verified
- ✅ Failover tested (zone loss)
- ✅ Backup restore drill successful
- ✅ Pen test shows no critical vulnerabilities
- ✅ On-call team trained

**Priority**: P0  
**Ref**: Spec 9.1–9.7

---

## Phase 4: Growth & Engagement (Months 6–12)  
*Goal: Expand social features, competition, and platform reach.*

---

### Epic: Social Features  
*Enable playing and interacting with friends.*

#### User Story: As a player, I want to play with my friends in parties.  
**Tasks**:
1. Implement `/party/create`, `/party/invite`, `/party/join`
2. Store friendships in `friendships` table
3. Modify matchmaking: prioritize party members
4. Add in-game chat (team + global channels)
5. Build spectator mode
6. Allow replay sharing (link or social)

**Acceptance Criteria**:
- ✅ Parties stay together in matches
- ✅ Friends list visible
- ✅ Chat messages delivered
- ✅ Spectators see live game
- ✅ Replays shareable

**Priority**: P1  
**Ref**: Spec 15.2

---

### Epic: Competitive Mode  
*Introduce ranked play, leaderboards, and tournaments.*

#### User Story: As a skilled player, I want to compete for rank and rewards.  
**Tasks**:
1. Implement separate ELO tracks: casual vs ranked
2. Update leaderboard materialized view (refresh every 5 min)
3. Add seasonal reset (every 3 months)
4. Design tournament engine (brackets, scheduling)
5. Award badges and titles

**Acceptance Criteria**:
- ✅ Ranked games affect separate rating
- ✅ Leaderboard accurate and fast
- ✅ Seasons reset cleanly
- ✅ Tournaments configurable
- ✅ Rewards awarded

**Priority**: P1  
**Ref**: Spec 15.2, 5.1

---

### Epic: Native Mobile Apps  
*Extend platform to iOS and Android with native performance.*

#### User Story: As a mobile user, I want push notifications so I don’t miss turns.  
**Tasks**:
1. Develop iOS app (Swift + WebTransport)
2. Develop Android app (Kotlin + WebTransport)
3. Integrate push notifications (Firebase/APNs)
4. Sync profiles and progress across devices
5. Optimize battery and data usage

**Acceptance Criteria**:
- ✅ App published on App Store and Play Store
- ✅ Notifications work reliably
- ✅ Cross-device sync seamless
- ✅ Performance on par with web

**Priority**: P2  
**Ref**: Spec 15.4

---

## Ongoing: Platform Maintenance

### Epic: Observability & SRE  
*Monitor, alert, and improve system health continuously.*

#### Tasks:
- [ ] Maintain Grafana dashboards (latency, errors, active games)
- [ ] Alert on p99 latency > 100ms
- [ ] Weekly incident reviews
- [ ] Monthly chaos engineering
- [ ] Cost optimization (spot instances, S3 lifecycle)

**Priority**: P0

---

### Epic: AI Retraining Pipeline  
*Continuously improve AI using production game data.*

#### Tasks:
- [ ] Collect anonymized game data to S3 (`ml/training/`)
- [ ] Retrain model monthly with new data
- [ ] A/B test new models (5% traffic)
- [ ] Deploy updated ONNX models
- [ ] Monitor win rate vs humans

**Priority**: P1

---

> **Kanban Board Setup Recommendation**:
> - **Columns**: `Backlog` | `Ready` | `In Progress` | `Review/QA` | `Done`
> - **Labels**: `backend`, `frontend`, `ai`, `infra`, `security`, `ux`, `db`
> - **Prioritization**: Sort by Priority (P0 → P2), then by Phase
> - **Tracking**: Use Jira, Linear, or GitHub Projects

# Debugging Anti-Patterns (Learned from Voice Agent Sessions)

## Anti-Pattern 1: Jumping to IP Ban Conclusions

**What happened:** Cloudflare tunnel failure (`control stream encountered a failure while serving`) was immediately diagnosed as "IP ban." Same with opencode-zen HTTP 403 — called IP ban, but Edel confirmed it was just rate limiting that cleared after update.

**Why it's harmful:** IP ban is the most severe diagnosis — it implies nothing can be done. It shuts down further investigation and leads to workarounds that may be unnecessary.

**What to do instead:**
1. Check if the error is intermittent (retry 2-3 times)
2. Test with different protocols (QUIC vs HTTP2 for Cloudflare)
3. Test with/without proxy (WARP vs direct)
4. Check account-level quotas and rate limits first
5. Search session history — was this diagnosed before?
6. Only after eliminating all other causes, consider IP reputation

## Anti-Pattern 2: Debugging Without Session History

**What happened:** This session (June 15) spent hours re-discovering issues that were already debugged on June 14:
- Deepgram timeout due to Hermes API slowness
- Model proxy routing issues
- Provider rate limits

**Why it's harmful:** Repeats failed experiments, wastes time, frustrates user.

**What to do instead:**
1. Before debugging: `session_search(query="<problem keywords>")` 
2. Read the compaction summary at the top of the current session
3. Check `references/voice-agent-architecture-research.md` for known benchmarks
4. If a past session found a dead end, DON'T re-enter it

## Anti-Pattern 3: Changing Models Mid-Session

**What happened:** Multiple `hermes config set model.default` changes during debugging polluted test results. Each change invalidated previous measurements.

**What to do instead:**
1. Set model ONCE at the start of testing
2. If switching is needed, restart gateway and re-benchmark baseline
3. Note the model in every test result

## Anti-Pattern 4: Testing Voice Without a Voice Platform

**What happened:** Built a voice proxy (port 8767), tested it with curl, declared "voice agent working" — but never connected it to Deepgram, LiveKit, or any actual voice platform.

**Why it's harmful:** The proxy returning JSON to curl is NOT the same as a voice agent handling real-time audio. End-to-end testing requires the actual platform.

**What to do instead:**
1. Define the voice platform FIRST (Deepgram, Vapi, LiveKit)
2. Build/test the integration incrementally
3. "curl test passed" ≠ "voice agent works"

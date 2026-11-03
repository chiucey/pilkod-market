---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 10417642ce9faeb6b275483a33b15707
    PropagateID: 10417642ce9faeb6b275483a33b15707
    ReservedCode1: 3046022100aba9f8b7eaca9328867cc6fa19fa2fe06f74aa79117684905dbb73fd82f960ec022100ace8de28a891069bd4a61ca6ed348f8b2201324d593978b4ded250f4e8b02c39
    ReservedCode2: 304502206fb74aebc2c365208b056fb23c5fe28f3773e12bf1dc9f8a67edaa17f7a9d71b02210089d18b08da9b7530735cfc364f81f888122f49a9664019213a8d9fe6cdc8764f
---

# Director Style Methods Library

> **Author**: 起始终下
> **Copyright**: © 2025 起始终下. All Rights Reserved.

---

## Method Library

| Method | Visual & Space | Information/Emotion | Action/Sound | Use Cases & Taboos |
|--------|----------------|---------------------|--------------|-------------------|
| 冷观察 (Cold Observation) | Fixed/very slow camera, medium-long shot, space-constrained | Delay reaction cuts, audience judges themselves | Complete environment sound, action unexplained by music | Reality drama, black comedy; not for action requiring quick geographic explanation |
| 主观贴身 (Subjective Following) | Close-up, limited vision, breathing follow | Information synchronized with character, errors visible | Body sounds, partial blocking, reaction before full view | Thriller, growth; loses space and contrast with long-term use |
| 精密秩序 (Precise Order) | Symmetry, repetitive positions, mechanical constant speed, clear geometry | Minor deviation becomes event | Regular audio patterns, clear action procedures | Sci-fi, system, satire; don't treat neatness as content |
| 空间悬疑 (Spatial Suspense) | Deep focus, negative space, door-window blocking, fixed axis | Audience may know more than character, reveal through space | Sound first, empty space described | Horror/suspense; cannot use darkness to hide unclear geography |
| 社会现实 (Social Reality) | Characters with system/labor space, normal observation height | Pressure from procedure, money, gazes | Location sound, professional actions, minimal explanation | Reality/literary; cannot use rough filter to fake reality |
| 抒情记忆 (Lyrical Memory) | Tactile details, time jumps, light-color shifts with memory | Association not explanation, repeated imagery changes meaning | Sound bridges, gaps and echoes | Romance/literary; must retain causal anchor |
| 动作地理 (Action Geography) | Wide establishing, coverage by action beats, stable direction | Audience always knows goal and risk | Impact sound connects editing, contact at cut point | Action/adventure; handheld and quick cuts cannot replace choreography |
| 商业证明 (Commercial Proof) | Clear product/service action surface, real assets priority | Claim first, then evidence, brand attribution and CTA clear | Material sounds, operational results, brand end point | Ads/products; aesthetics cannot replace evidence |
| 竖屏近场 (Vertical Near-field) | Depth composition, face and key action in safe zone, less reliance on horizontal wide shots | First-second question, visible change within 3 seconds, episode-end traction | Clear spoken/audio, subtitle safety zone for post | Short drama/social media; not horizontal video cropping |
| 纪实在场 (Documentary Presence) | Allows late repositioning, visible focus correction, natural light | Camera doesn't pre-know events, holds imperfect evidence | Location sound priority, continues holding after answers | Documentary/mockumentary; cannot only add shake |

---

## Style Fusion Contract

Maximum three levels:

- **Primary Method 60-80%**: Determines entire film's observation ethics, camera/space, editing, sound baseline
- **Secondary Method 20-40%**: Only takes explicit scenes, narrative levels, or two knobs
- **Accent Method 0-10%**: Only used at one turning point or imagery

Weights are decision proportions, not prompt percentage mixing. Each method must declare "owned knobs" and "invariants that cannot be changed."

---

## Conflict Matrix

| Conflict | Decision Questions | Default Solution |
|----------|-------------------|-----------------|
| Fixed observation vs handheld following | Who owns information: space or character body? | Choose one; switch using scene boundaries |
| Deep-space geography vs shallow-space isolation | Must audience see relationship clearly now or only feel character? | Establish geography first, then allow partial shallow focus |
| Long-take waiting vs quick-cut impact | Is promise waiting or speed? | Primary method sets baseline, turning point briefly deviates |
| Natural light authenticity vs expressive color | Is color world fact or subjective level? | Only switch at narratively marked level |
| Comedy honest wide vs thriller blocking | Should audience see punchline first or see danger later? | Decided by information axis, cannot do both simultaneously |
| Commercial brand accuracy vs generative stylization | Can product facts allow drift? | Real product/logo priority: real shoot or composite |

If two methods conflict on same knob, do not split the difference; choose one and explain what the other loses. When adjacent scenes change more than three craft knobs,必须有空间、时间、视角或情节转折作为理由.

---

## Combination Output Format

```yaml
style_stack:
  primary: {method: "", weight: 70, owns: [camera_space, editing, sound]}
  secondary: {method: "", weight: 30, scope: "scene or narrative level", owns: [lighting, palette]}
  accent: null
  invariants: [aspect, identity, geography, skin_tone]
  conflicts_resolved: []
```

---

> **Copyright Notice**: © 2025 起始终下. All Rights Reserved.
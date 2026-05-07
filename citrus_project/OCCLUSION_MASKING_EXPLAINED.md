# Occlusion Masking: Visual & Conceptual Guide

## What is Occlusion? (Picture This)

You're standing in an orchard, looking at a tree from two angles:

```
Angle 1 (target frame):          Angle 2 (source frame):
┌──────────────────┐             ┌──────────────────┐
│  [apple]         │             │                  │
│  [leaf] [leaf]   │             │  [sky]   [sky]   │
│  [branch]────────│             │  [branch]        │
│  [trunk]         │             │  [trunk]         │
└──────────────────┘             └──────────────────┘

From Angle 1, we see the apple.
From Angle 2, the apple is hidden behind the branch!
(It's occluded.)
```

---

## Why Does Standard Depth Learning Fail?

**The model tries to minimize error:**

```
Loss = |Angle1_frame - Reprojected_from_Angle2_using_predicted_depth|

Pixel-by-pixel:
┌─────────────────────────┬──────────────────────┬─────────────────┐
│ Location                │ What Angle 1 sees    │ What Angle 2 has│
├─────────────────────────┼──────────────────────┼─────────────────┤
│ Apple position          │ [apple]              │ [sky] ← hidden! │
│ After reprojection:     │ [apple]              │ [sky]           │
│ Error:                  │ HIGH! Apple≠sky      │                 │
└─────────────────────────┴──────────────────────┴─────────────────┘

Model thinks: "The reprojection is wrong. Predict deeper depth at apple!"
Reality: The apple is occluded. No depth can fix this mismatch!

Result: Model hallucinates depth.
```

---

## The Solution: Don't Penalize Occlusion Pixels

```
Step 1: DETECT where occlusions likely are
   ├─ Look for depth discontinuities (sharp changes)
   ├─ Mark those regions as "uncertain" (mask = 0)
   └─ Mark smooth regions as "confident" (mask = 1)

Step 2: APPLY the mask to the loss
   ├─ Loss = Error * Mask
   ├─ Uncertain pixels: Loss *= 0 → no penalty
   └─ Confident pixels: Loss *= 1 → full penalty

Step 3: RESULT
   ├─ Model ignores occluded pixels
   ├─ Doesn't waste learning effort on impossible pixels
   └─ Depth surfaces stay smooth and realistic
```

---

## Visualization: Before vs After Occlusion Masking

### BEFORE (Vanilla Loss):

```
Depth Map (depth)          Predicted Image       Target Image       Error
┌────────────────┐        ┌────────────────┐    ┌────────────────┐   ┌────────────────┐
│ 2.0  2.0  9.5  │        │ [leaf] [leaf]  │    │ [apple][leaf]  │   │ HIGH! → high   │
│ 2.0  5.0  9.0  │   →    │ [branch][sky]  │  - │ [branch][sky]  │ = │ ERROR at apple │
│ 3.0  3.0  10.0 │        │ [trunk][trunk] │    │ [trunk][trunk] │   │ Model: "Fix    │
└────────────────┘        └────────────────┘    └────────────────┘   │ this by adding │
                                                                       │ depth!"        │
                                                                       └────────────────┘
                          ↓ Model predicts: Apple = 5.0m
                          ↓ Fake depth surface hallucinated!
```

### AFTER (With Occlusion Masking):

```
Depth Map        Predicted     Target        Occlusion Mask      Masked Error
┌────────────────┐┌────────────┐┌────────────┐┌────────────────┐  ┌─────────────────┐
│ 2.0  2.0  2.1  ││ [leaf][leaf]││ [apple]   ││ 1.0  1.0  0.0  ││  │ 0.0  0.0  0.0  │
│ 2.0  2.0  2.3  ││ [branch][sky]││ [branch] ││ 1.0  0.0  1.0  ││  │ 0.0  HIGH*0=0   │
│ 3.0  3.0  3.0  ││ [trunk][trunk]││ [trunk] ││ 1.0  1.0  1.0  ││  │ 0.0  0.0  0.0   │
└────────────────┘└────────────────┘└────────┘└────────────────┘  └────────────────┘
                     ↓ Smooth depth
                     ↓ Apple region masked (0) = no penalty
                     ↓ Model learns realistic geometry!
```

---

## How to Detect Occlusion? (Technical)

### Approach: Depth Gradient (Fast & Simple)

**Idea:** Occlusion happens at edges where depth changes suddenly

```
Smooth region (no occlusion):
Depth: [2.0, 2.0, 2.1, 2.1, 2.0]
Gradient: [0.0, 0.1, 0.0, -0.1]  ← Small gradients

Sharp boundary (occlusion):
Depth: [2.0, 2.0, 8.5, 8.5, 8.0]
Gradient: [0.0, 6.5, 0.0, -0.5]  ← BIG gradient!
                ↑ Threshold: if gradient > 0.5m → mark as boundary
```

**Algorithm:**

```python
depth_gradient = |depth[x+1] - depth[x]|

if depth_gradient > threshold:
    mask[x] = 0  # Uncertain (occlusion boundary)
else:
    mask[x] = 1  # Confident (smooth region)
```

---

## Real Citrus Example

```
RGB Image from canopy:
┌─────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░ │  ░ = leaves (dense)
│ ░░░[branch]░░░░░░░░░░░ │  [branch] = thin structure
│ ░░░░░░░░░░░░░░░░░░░░░ │  
│ ░░░░[fruit]░░░░░░░░░░░ │  [fruit] = occluded by leaves
│ ░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────┘

Depth prediction WITHOUT occlusion masking:
┌─────────────────────────┐
│ 3.5  3.4  3.6  3.5  3.6 │  ← Smooth, but fruit region is made up!
│ 3.3  2.8  3.2  3.1  3.4 │     (We can't see the fruit, so we shouldn't
│ 3.4  3.3  3.5  3.4  3.3 │      predict depth for it)
│ 3.2  2.5  3.3  3.0  3.5 │  ← Branch discontinuity, leaf occlusion
│ 3.3  3.4  3.6  3.5  3.2 │     create confusing signals
└─────────────────────────┘

Depth prediction WITH occlusion masking:
┌─────────────────────────┐
│ 3.5  3.4  3.6  3.5  3.6 │  ← Smooth surface learned well
│ 3.3 [2.7] 3.2  3.1  3.4 │     [branch] sharp edge: mask prevents
│ 3.4  3.3  3.5  3.4  3.3 │      overfitting to reprojection error
│ 3.2 [2.5] 3.3  3.0  3.5 │     [fruit] region: masked, so model
│ 3.3  3.4  3.6  3.5  3.2 │      doesn't waste learning on it
└─────────────────────────┘
     ↓ Clean, realistic, no hallucination!
```

---

## In Your Project (Implementation Flow)

```
1. INPUT: Depth prediction from model
   ↓
2. COMPUTE: Depth gradients (how fast does depth change?)
   ↓
3. DETECT: Where gradients > threshold → mark as occlusion
   ↓
4. CREATE: Mask (1=confident, 0=uncertain)
   ↓
5. APPLY: Loss = Reprojection_error * Mask
   ↓
6. TRAIN: Model learns to ignore uncertain pixels
   ↓
7. OUTPUT: Smooth, realistic depth in vegetation
```

---

## Key Parameters to Tune

| Parameter | Effect | Range |
|---|---|---|
| `grad_threshold` | Sensitivity to depth changes | 0.3–0.8m |
| `dilation_radius` | How wide is occlusion region | 1–4 pixels |

**How to tune:**
- If too many pixels masked (depth is too smooth): **increase grad_threshold**
- If too few pixels masked (sees hallucinations): **decrease grad_threshold**
- If boundaries are fuzzy: **increase dilation_radius**
- If boundaries are too thick: **decrease dilation_radius**

---

## Expected Impact (M4a)

| Metric | Before | After | Why? |
|---|---|---|---|
| Depth error (MAE) | 0.40m | 0.35m | Model doesn't hallucinate at occlusions |
| Edge sharpness | Low | High | Boundaries preserved, not smoothed |
| Canopy geometry | Fuzzy | Clear | Vegetation structure visible |
| Runtime | 35ms | 36ms | ~0% overhead |

---

## Checklist: Is Occlusion Masking Working?

After training, check:

- [ ] Occlusion mask shows boundaries (not all 0s or all 1s)
- [ ] Depth predictions are smooth in sky/ground (mask = 1)
- [ ] Depth predictions are cautious at edges (mask = 0)
- [ ] Validation error decreased vs baseline
- [ ] Qualitative images look more realistic (fewer "fake surfaces")
- [ ] Runtime didn't increase significantly

If all checkboxes ✓: **Phase 1 is complete!**

---

## Common Mistakes to Avoid

❌ **Mistake 1:** Apply mask AFTER averaging loss across batch  
✅ **Fix:** Apply mask BEFORE averaging

❌ **Mistake 2:** Forget to pad gradients back to original size  
✅ **Fix:** Use `F.pad()` to match depth dimensions

❌ **Mistake 3:** Use threshold that's too high (grad_threshold = 50m)  
✅ **Fix:** Use reasonable threshold for your depth range (0.3–0.8m for Citrus)

❌ **Mistake 4:** Dilation radius too large (occludes entire image)  
✅ **Fix:** Start small (radius=2), increase if needed

---

## Summary

**Occlusion masking = Prevent the loss from penalizing unpredictable pixels**

It's like telling the model:  
- "These pixels (smooth regions): predict depth accurately"  
- "These pixels (boundaries): you can't predict, ignore them"

**Result:** Better depth in vegetation-dense scenes!

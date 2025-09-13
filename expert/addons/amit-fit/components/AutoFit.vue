<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, nextTick } from 'vue'

interface Props {
  min?: number
  max?: number
  step?: number
  pad?: number
}
const props = withDefaults(defineProps<Props>(), {
  min: 18,
  max: 56,
  step: 1,
  pad: 0,
})

const box = ref<HTMLDivElement | null>(null)
const inner = ref<HTMLDivElement | null>(null)

let ro: ResizeObserver | null = null
let rafId = 0
let debounceId: number | undefined

// Hysteresis: remember last measured size; ignore sub-pixel changes
let lastW = -1
let lastH = -1

function fits(fontPx: number): boolean {
  const b = box.value!
  const i = inner.value!
  i.style.fontSize = `${fontPx}px`
  // Force layout before measuring
  // eslint-disable-next-line @typescript-eslint/no-unused-expressions
  i.offsetHeight
  const wOk = i.scrollWidth <= (b.clientWidth - props.pad * 2)
  const hOk = i.scrollHeight <= (b.clientHeight - props.pad * 2)
  return wOk && hOk
}

function fitNow() {
  if (!box.value || !inner.value) return
  const w = box.value.clientWidth
  const h = box.value.clientHeight
  if (w === 0 || h === 0) {
    // Safe fallback so content is visible even if initial measurement is 0×0
    inner.value.style.fontSize = `${props.min}px`
    // Try again on the next tick
    requestAnimationFrame(() => nextTick().then(fitNow))
    return
  }
  let lo = props.min
  let hi = props.max
  let best = lo
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2)
    if (fits(mid)) { best = mid; lo = mid + (props.step ?? 1) }
    else { hi = mid - (props.step ?? 1) }
  }
  inner.value!.style.fontSize = `${best}px`
}

function schedule() {
  cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => {
    if (!box.value) return
    const w = box.value.clientWidth
    const h = box.value.clientHeight
    // Only re-fit if a meaningful size change happened (>= 1 CSS px)
    if (Math.abs(w - lastW) < 1 && Math.abs(h - lastH) < 1) return
    lastW = w; lastH = h
    // Coalesce bursts of RO/resize events
    if (debounceId) clearTimeout(debounceId)
    debounceId = window.setTimeout(() => { nextTick().then(fitNow) }, 50)
  })
}

onMounted(() => {
  schedule()
  ro = new ResizeObserver(() => schedule())
  if (box.value) ro.observe(box.value)
  if (inner.value) ro.observe(inner.value)
  window.addEventListener('resize', schedule, { passive: true })
  window.addEventListener('orientationchange', schedule, { passive: true })
  // Re-fit when webfonts finish loading (prevents post-load shrink)
  // @ts-expect-error: fonts is not in lib.dom.d.ts in some TS targets
  if (document.fonts?.ready) document.fonts.ready.then(() => schedule())
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  if (debounceId) clearTimeout(debounceId)
  ro?.disconnect()
  window.removeEventListener('resize', schedule)
  window.removeEventListener('orientationchange', schedule)
})
</script>

<template>
  <!-- IMPORTANT: min-h-0 to allow shrinking inside any flex/grid parent -->
  <div ref="box" class="grid h-full min-h-0 place-content-center">
    <div ref="inner" style="line-height:1.18">
      <slot />
    </div>
  </div>
</template>

<style scoped>
/* Keep lists compact and measurement-stable inside AutoFit */
::v-slotted(ul), ::v-slotted(ol),
:slotted(ul), :slotted(ol) {
  max-width: 90vw;
  word-break: break-word;
  margin: 0;
  padding-left: var(--amit-bullet-indent, 1.25rem);
}
</style>


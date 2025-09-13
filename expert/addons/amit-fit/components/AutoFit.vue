<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watchEffect, nextTick } from 'vue'

interface Props {
  min?: number
  max?: number
  step?: number
  pad?: number
}
const props = withDefaults(defineProps<Props>(), { min: 18, max: 56, step: 1, pad: 0 })

const box = ref<HTMLDivElement|null>(null)
const inner = ref<HTMLDivElement|null>(null)
let ro: ResizeObserver | null = null
let raf = 0

function fits(px: number) {
  const b = box.value!, i = inner.value!
  i.style.fontSize = `${px}px`
  // force layout
  // eslint-disable-next-line @typescript-eslint/no-unused-expressions
  i.offsetHeight
  const wOk = i.scrollWidth <= (b.clientWidth - props.pad * 2)
  const hOk = i.scrollHeight <= (b.clientHeight - props.pad * 2)
  return wOk && hOk
}

function fit() {
  if (!box.value || !inner.value) return
  let lo = props.min, hi = props.max, best = lo
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2)
    if (fits(mid)) { best = mid; lo = mid + props.step }
    else { hi = mid - props.step }
  }
  inner.value!.style.fontSize = `${best}px`
}

function schedule() {
  cancelAnimationFrame(raf)
  raf = requestAnimationFrame(() => { nextTick().then(fit) })
}

onMounted(() => {
  schedule()
  ro = new ResizeObserver(schedule)
  if (box.value) ro.observe(box.value)
  if (inner.value) ro.observe(inner.value)
  window.addEventListener('resize', schedule, { passive: true })
})
onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  ro?.disconnect()
  window.removeEventListener('resize', schedule)
})
watchEffect(schedule)
</script>

<template>
  <div ref="box" class="grid h-full place-content-center">
    <div ref="inner" style="line-height:1.18"><slot /></div>
  </div>
</template>

<style scoped>
:slotted(ul), :slotted(ol) {
  max-width: 90vw;
  word-break: break-word;
  margin: 0;              /* important: no extra top/bottom margin */
  padding-left: 1.25rem;  /* nice bullet indent */
}
</style>


<script setup lang="ts">
import AutoFit from '../components/AutoFit.vue'
</script>

<template>
  <!-- Two rows: title area (fixed height) + content area (fills the rest) -->
  <div class="slidev-layout default h-full grid" style="grid-template-rows: auto 1fr;">
    <!-- ===== TITLE ROW ===== -->
    <div
      v-if="$frontmatter.title"
      class="min-h-0"
      :style="{
        /* Use per-slide override if provided; else CSS var; else 10vh */
        height: ($frontmatter.titleHeight ?? 'var(--amit-title-height, 10vh)')
      }"
    >
      <AutoFit
        :min="$frontmatter.titleMin ?? 28"
        :max="$frontmatter.titleMax ?? 64"
        :pad="$frontmatter.titlePad ?? 8"
      >
        <!-- Neutralize theme font-size so AutoFit governs -->
        <h1 class="m-0 font-extrabold leading-[1.06] tracking-[-0.02em] auto-title"
            style="text-wrap: balance; hyphens: auto;">
          {{ $frontmatter.title }}
        </h1>
      </AutoFit>
    </div>

    <!-- ===== CONTENT ROW (BULLETS) ===== -->
    <div class="min-h-0">
      <AutoFit :min="20" :max="52" :pad="12">
        <slot />
      </AutoFit>
    </div>

    <slot name="footer" />
  </div>
</template>

<style scoped>
/* If someone types an H1/H2 in the body, hide the first so we don't double-render titles */
.prose :is(h1,h2):first-child { display: none; }

/* Critical: let AutoFit control the title size */
.auto-title { font-size: 1em; }
</style>


<script setup lang="ts">
import AutoFit from '../components/AutoFit.vue'
</script>

<template>
  <!-- FLEX instead of grid: fewer edge-cases with collapsed rows -->
  <div class="slidev-layout default h-full min-h-0 flex flex-col">
    <!-- ===== TITLE ROW ===== -->
    <div
      v-if="$frontmatter.title"
      class="shrink-0 min-h-0"
      :style="{ height: ($frontmatter.titleHeight ?? 'var(--amit-title-height, 10vh)') }"
    >
      <div class="h-full min-h-0">
        <AutoFit
          :min="$frontmatter.titleMin ?? 28"
          :max="$frontmatter.titleMax ?? 56"
          :pad="$frontmatter.titlePad ?? 8"
        >
          <!-- Neutralize theme size so AutoFit governs -->
          <h1 class="m-0 font-extrabold leading-[1.06] tracking-[-0.02em] auto-title"
              style="text-wrap: balance; hyphens: auto;">
            {{ $frontmatter.title }}
          </h1>
        </AutoFit>
      </div>
    </div>

    <!-- ===== OPTIONAL SUBTITLE ROW ===== -->
    <div
      v-if="$frontmatter.subtitle"
      class="shrink-0 min-h-0"
      :style="{ height: ($frontmatter.subtitleHeight ?? 'var(--amit-subtitle-height, 6vh)') }"
    >
      <div class="h-full min-h-0">
        <AutoFit
          :min="$frontmatter.subtitleMin ?? 18"
          :max="$frontmatter.subtitleMax ?? 32"
          :pad="$frontmatter.subtitlePad ?? 6"
        >
          <h2 class="m-0 font-semibold auto-subtitle" style="text-wrap: balance; hyphens: auto;">
            {{ $frontmatter.subtitle }}
          </h2>
        </AutoFit>
      </div>
    </div>

    <!-- ===== CONTENT (BULLETS) ===== -->
    <div class="flex-1 min-h-0">
      <div class="content-box h-full min-h-0">
        <AutoFit :min="22" :max="52" :pad="12">
          <slot />
        </AutoFit>
      </div>
    </div>

    <slot name="footer" />
  </div>
</template>

<style scoped>
/* If someone types an H1/H2 in the body, hide the first so we don't double-render titles */
.prose :is(h1,h2):first-child { display: none; }

/* Critical: let AutoFit control the title/subtitle size */
.auto-title { font-size: 1em; }
.auto-subtitle { font-size: 1em; }

/* Safe areas + max readable width for bullets */
.content-box {
  padding-left: var(--amit-safe-x, 6vw);
  padding-right: var(--amit-safe-x, 6vw);
  max-width: var(--amit-max-content, 80ch);
  margin-left: auto;
  margin-right: auto;
}
</style>


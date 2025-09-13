<script setup lang="ts">
import AutoFit from '../components/AutoFit.vue'
</script>

<template>
  <!-- Center the whole stack; keep heights flexible and safe -->
  <div class="slidev-layout default h-full min-h-0 flex items-center justify-center relative">
    <div class="w-full px-[var(--amit-safe-x,6vw)] max-w-[min(120ch,90vw)]">

      <!-- Title -->
      <div class="min-h-0" :style="{ height: ($frontmatter.coverTitleHeight ?? 'var(--cover-title-height, 32vh)') }">
        <AutoFit
          :min="$frontmatter.titleMin ?? 32"
          :max="$frontmatter.titleMax ?? 96"
          :pad="$frontmatter.titlePad ?? 8"
        >
          <h1 class="m-0 font-extrabold auto-title"
              style="text-wrap: balance; hyphens: auto; letter-spacing:-0.02em; line-height:1.04;">
            {{ $frontmatter.title || $frontmatter.coverTitle || '' }}
          </h1>
        </AutoFit>
      </div>

      <!-- Subtitle (optional) -->
      <div v-if="$frontmatter.subtitle" class="min-h-0 mt-2"
           :style="{ height: ($frontmatter.coverSubtitleHeight ?? 'var(--cover-subtitle-height, 14vh)') }">
        <AutoFit
          :min="$frontmatter.subtitleMin ?? 22"
          :max="$frontmatter.subtitleMax ?? 40"
          :pad="$frontmatter.subtitlePad ?? 6"
        >
          <h2 class="m-0 font-semibold auto-subtitle"
              style="text-wrap: balance; hyphens: auto; line-height:1.06;">
            {{ $frontmatter.subtitle }}
          </h2>
        </AutoFit>
      </div>

      <!-- Presenter / meta (name, email, org/website—each optional) -->
      <div class="min-h-0 mt-6" :style="{ height: ($frontmatter.coverMetaHeight ?? 'var(--cover-meta-height, 12vh)') }">
        <AutoFit :min="$frontmatter.metaMin ?? 16" :max="$frontmatter.metaMax ?? 22" :pad="4">
          <div class="text-center leading-tight">
            <div v-if="$frontmatter.by" class="font-semibold">{{ $frontmatter.by }}</div>
            <div v-if="$frontmatter.email">
              <a :href="`mailto:${$frontmatter.email}`">{{ $frontmatter.email }}</a>
            </div>
            <div v-if="$frontmatter.org">{{ $frontmatter.org }}</div>
            <div v-if="$frontmatter.website">
              <a :href="$frontmatter.website" target="_blank" rel="noreferrer">{{ $frontmatter.website }}</a>
            </div>
          </div>
        </AutoFit>
      </div>
    </div>

    <!-- Optional logo in the corner -->
    <img v-if="$frontmatter.logo"
         :src="$frontmatter.logo"
         alt="logo"
         class="absolute right-8 bottom-8 max-h-[10vh] max-w-[20vw]" />
  </div>
</template>

<style scoped>
/* Let AutoFit control sizes (theme sizes are neutralized) */
.auto-title { font-size: 1em; }
.auto-subtitle { font-size: 1em; }
</style>


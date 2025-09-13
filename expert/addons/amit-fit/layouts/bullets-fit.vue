<script setup lang="ts">
import AutoFit from '../components/AutoFit.vue'
</script>

<template>
  <!-- 2-row grid: header (auto height) + content (fills the rest) -->
  <div class="slidev-layout default h-full grid" style="grid-template-rows: auto 1fr;">
    <!-- Header: uses front-matter title if provided -->
    <div class="pb-4">
      <h1 v-if="$frontmatter.title" class="m-0">{{$frontmatter.title}}</h1>
      <slot name="header" />
    </div>

    <!-- Content area: min-h-0 so it can actually shrink; AutoFit sizes bullets to fill -->
    <div class="min-h-0">
      <AutoFit :min="20" :max="60" :pad="12">
        <slot />
      </AutoFit>
    </div>

    <slot name="footer" />
  </div>
</template>

<style scoped>
/* If someone writes a Markdown H1/H2 in the content, hide the first one so it doesn't double with front-matter title */
.prose :is(h1,h2):first-child { display: none; }
</style>


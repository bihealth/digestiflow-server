<template>
  <div id="app">
    <sheet-editor :project="project"></sheet-editor>
  </div>
</template>

<script>
import SheetEditor from './components/SheetEditor'
export default {
  props: ['project'],
  name: 'App',
  components: {SheetEditor}
}
</script>

<style>

</style>

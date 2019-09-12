<template>
  <div id="app">
    <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
    <HelloWorld msg="Welcome to Your Vue.js App"/>
    <TestApi msg="Test API "/>
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'
import TestApi from './components/TestApi.vue'

export default {
  name: 'app',
  components: {
    HelloWorld,
    TestApi,
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

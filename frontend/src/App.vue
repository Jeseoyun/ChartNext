<template>
  <v-app>
    <v-main class="pa-0">
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style>
.v-application {
  padding: 0 !important;
  margin: 0 !important;
}
</style>

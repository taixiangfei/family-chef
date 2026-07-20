<script>
export default {
  onLaunch() {
    // App lifecycle hook kept for mini program compatibility.
  }
}
</script>

<style>
page {
  min-height: 100%;
  background: #f4ead8;
  color: #2b241c;
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
}

view,
text,
scroll-view,
input,
button {
  box-sizing: border-box;
}

button {
  padding: 0;
  margin: 0;
  line-height: 1;
  background: transparent;
}

button::after {
  border: 0;
}

input,
textarea {
  caret-color: #c84f31;
}
</style>

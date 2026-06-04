function rest() {
  document.querySelector('a[aria-label="Next page"]').click()
}

var str = ""
for(var a of document.getElementsByClassName("b_attribution")) {
    var split = a.textContent.trim().split(" ");
    str += split[split.length-1] + "\n";
}

console.log(str)
fetch("http://localhost:3000", {
  method: "POST",
  headers: { "Content-Type": "text/plain" },
  body: str,
})
  .then((response) => response.text())
  .then((data) => console.log("Server response:", data))
  .then((data) => rest())
  .catch((error) => console.error("Error:", error));
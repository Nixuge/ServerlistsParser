function rest() {
  var flag = false;
  for(var a of document.getElementsByClassName("NKTSme")) {
      if (a.className.includes("YyVfkd")) {
          flag = true;
          continue;
      }
      if (flag) {
          var elem = a.getElementsByTagName("a")[0];
          console.log(elem);
          elem.click();
          break;
      }
  }
}

function processLink(href) {
    if (href.includes("laby.net/")) {
        href = href.replace("https://www.laby.net", "https://laby.net");
        href = href.split("?lang=")[0]
    }
    else if (href.includes("namemc.com/")) {
        // href = "https://namemc.com" + href.split("namemc.com")[1]
        href = href.split("/server/")[1]
    }

    return href;
}

var str = ""
for(var a of document.getElementsByClassName("zReHs")) {
    str += processLink(a.href) + "\n";
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
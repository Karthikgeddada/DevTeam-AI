async function runAI() {

const task = document.getElementById("taskInput").value

const response = await fetch(`http://127.0.0.1:8000/run?task=${task}`)

const data = await response.json()

const files = data.code.files

const filesDiv = document.getElementById("files")
filesDiv.innerHTML = ""

files.forEach(file => {

const btn = document.createElement("button")
btn.innerText = file.filename

btn.onclick = () => {
document.getElementById("content").textContent = file.content
}

filesDiv.appendChild(btn)

})

}